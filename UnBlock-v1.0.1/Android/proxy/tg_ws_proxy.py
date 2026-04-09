from __future__ import annotations

import asyncio
import base64
import logging
import os
import socket as _socket
import ssl
import struct
import time
from typing import Dict, List, Optional, Set, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT_PORT = 1080
log = logging.getLogger('tg-ws-proxy')

_TCP_NODELAY = True
_RECV_BUF = 256 * 1024
_SEND_BUF = 256 * 1024

_TG_RANGES = [
    (struct.unpack('!I', _socket.inet_aton('185.76.151.0'))[0],
     struct.unpack('!I', _socket.inet_aton('185.76.151.255'))[0]),
    (struct.unpack('!I', _socket.inet_aton('149.154.160.0'))[0],
     struct.unpack('!I', _socket.inet_aton('149.154.175.255'))[0]),
    (struct.unpack('!I', _socket.inet_aton('91.105.192.0'))[0],
     struct.unpack('!I', _socket.inet_aton('91.105.193.255'))[0]),
    (struct.unpack('!I', _socket.inet_aton('91.108.0.0'))[0],
     struct.unpack('!I', _socket.inet_aton('91.108.255.255'))[0]),
]

_IP_TO_DC: Dict[str, Tuple[int, bool]] = {
    '149.154.175.50': (1, False), '149.154.175.51': (1, False),
    '149.154.175.53': (1, False), '149.154.175.54': (1, False),
    '149.154.175.52': (1, True),
    '149.154.167.41': (2, False), '149.154.167.50': (2, False),
    '149.154.167.51': (2, False), '149.154.167.220': (2, False),
    '95.161.76.100': (2, False),
    '149.154.167.151': (2, True), '149.154.167.222': (2, True),
    '149.154.167.223': (2, True), '149.154.162.123': (2, True),
    '149.154.175.100': (3, False), '149.154.175.101': (3, False),
    '149.154.175.102': (3, True),
    '149.154.167.91': (4, False), '149.154.167.92': (4, False),
    '149.154.164.250': (4, True), '149.154.166.120': (4, True),
    '149.154.166.121': (4, True), '149.154.167.118': (4, True),
    '149.154.165.111': (4, True),
    '91.108.56.100': (5, False), '91.108.56.101': (5, False),
    '91.108.56.116': (5, False), '91.108.56.126': (5, False),
    '149.154.171.5': (5, False),
    '91.108.56.102': (5, True), '91.108.56.128': (5, True),
    '91.108.56.151': (5, True),
    '91.105.192.100': (203, False),
}

_DC_OVERRIDES: Dict[int, int] = {203: 2}
_dc_opt: Dict[int, Optional[str]] = {}
_ws_blacklist: Set[Tuple[int, bool]] = set()
_dc_fail_until: Dict[Tuple[int, bool], float] = {}
_DC_FAIL_COOLDOWN = 30.0
_WS_FAIL_TIMEOUT = 2.0

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _xor_mask(data: bytes, mask: bytes) -> bytes:
    if not data:
        return data
    n = len(data)
    mask_rep = (mask * (n // 4 + 1))[:n]
    return (int.from_bytes(data, 'big') ^ int.from_bytes(mask_rep, 'big')).to_bytes(n, 'big')


class RawWebSocket:
    OP_CONTINUATION = 0x0
    OP_TEXT = 0x1
    OP_BINARY = 0x2
    OP_CLOSE = 0x8
    OP_PING = 0x9
    OP_PONG = 0xA

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self._closed = False

    @staticmethod
    async def connect(ip: str, domain: str, path: str = '/apiws', timeout: float = 10.0) -> 'RawWebSocket':
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, 443, ssl=_ssl_ctx, server_hostname=domain),
            timeout=min(timeout, 10))

        ws_key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f'GET {path} HTTP/1.1\r\n'
            f'Host: {domain}\r\n'
            f'Upgrade: websocket\r\n'
            f'Connection: Upgrade\r\n'
            f'Sec-WebSocket-Key: {ws_key}\r\n'
            f'Sec-WebSocket-Version: 13\r\n'
            f'Sec-WebSocket-Protocol: binary\r\n'
            f'Origin: https://web.telegram.org\r\n'
            f'User-Agent: Mozilla/5.0\r\n'
            f'\r\n'
        )
        writer.write(req.encode())
        await writer.drain()

        response_lines = []
        try:
            while True:
                line = await asyncio.wait_for(reader.readline(), timeout=timeout)
                if line in (b'\r\n', b'\n', b''):
                    break
                response_lines.append(line.decode('utf-8', errors='replace').strip())
        except asyncio.TimeoutError:
            writer.close()
            raise

        if not response_lines:
            writer.close()
            raise Exception("Empty response")

        first_line = response_lines[0]
        if '101' not in first_line:
            writer.close()
            raise Exception(f"WebSocket handshake failed: {first_line}")

        return RawWebSocket(reader, writer)

    async def send(self, data: bytes):
        if self._closed:
            raise ConnectionError("WebSocket closed")
        frame = self._build_frame(self.OP_BINARY, data, mask=True)
        self.writer.write(frame)
        await self.writer.drain()

    async def recv(self) -> Optional[bytes]:
        while not self._closed:
            opcode, payload = await self._read_frame()
            if opcode == self.OP_CLOSE:
                self._closed = True
                return None
            if opcode == self.OP_PING:
                continue
            if opcode == self.OP_PONG:
                continue
            if opcode in (self.OP_TEXT, self.OP_BINARY):
                return payload
        return None

    async def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            pass

    @staticmethod
    def _build_frame(opcode: int, data: bytes, mask: bool = False) -> bytes:
        header = bytearray()
        header.append(0x80 | opcode)
        length = len(data)
        mask_bit = 0x80 if mask else 0x00

        if length < 126:
            header.append(mask_bit | length)
        elif length < 65536:
            header.append(mask_bit | 126)
            header.extend(struct.pack('>H', length))
        else:
            header.append(mask_bit | 127)
            header.extend(struct.pack('>Q', length))

        if mask:
            mask_key = os.urandom(4)
            header.extend(mask_key)
            return bytes(header) + _xor_mask(data, mask_key)
        return bytes(header) + data

    async def _read_frame(self) -> Tuple[int, bytes]:
        hdr = await self.reader.readexactly(2)
        opcode = hdr[0] & 0x0F
        is_masked = bool(hdr[1] & 0x80)
        length = hdr[1] & 0x7F

        if length == 126:
            length = struct.unpack('>H', await self.reader.readexactly(2))[0]
        elif length == 127:
            length = struct.unpack('>Q', await self.reader.readexactly(8))[0]

        if is_masked:
            mask_key = await self.reader.readexactly(4)
            payload = await self.reader.readexactly(length)
            return opcode, _xor_mask(payload, mask_key)

        payload = await self.reader.readexactly(length)
        return opcode, payload


def _is_telegram_ip(ip: str) -> bool:
    try:
        n = struct.unpack('!I', _socket.inet_aton(ip))[0]
        return any(lo <= n <= hi for lo, hi in _TG_RANGES)
    except OSError:
        return False


def _dc_from_init(data: bytes) -> Tuple[Optional[int], bool]:
    try:
        key = bytes(data[8:40])
        iv = bytes(data[40:56])
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
        encryptor = cipher.encryptor()
        keystream = encryptor.update(b'\x00' * 64) + encryptor.finalize()
        plain = bytes(a ^ b for a, b in zip(data[56:64], keystream[56:64]))
        proto = struct.unpack('<I', plain[0:4])[0]
        dc_raw = struct.unpack('<h', plain[4:6])[0]
        if proto in (0xEFEFEFEF, 0xEEEEEEEE, 0xDDDDDDDD):
            dc = abs(dc_raw)
            if 1 <= dc <= 5 or dc == 203:
                return dc, (dc_raw < 0)
    except Exception:
        pass
    return None, False


def _ws_domains(dc: int, is_media: bool) -> List[str]:
    dc = _DC_OVERRIDES.get(dc, dc)
    if is_media:
        return [f'kws{dc}-1.web.telegram.org', f'kws{dc}.web.telegram.org']
    return [f'kws{dc}.web.telegram.org', f'kws{dc}-1.web.telegram.org']


async def _bridge_ws(reader, writer, ws: RawWebSocket, label: str, dc=None):
    async def tcp_to_ws():
        try:
            while True:
                chunk = await reader.read(65536)
                if not chunk:
                    break
                await ws.send(chunk)
        except (asyncio.CancelledError, ConnectionError, OSError):
            pass

    async def ws_to_tcp():
        try:
            while True:
                data = await ws.recv()
                if data is None:
                    break
                writer.write(data)
                await writer.drain()
        except (asyncio.CancelledError, ConnectionError, OSError):
            pass

    tasks = [asyncio.create_task(tcp_to_ws()), asyncio.create_task(ws_to_tcp())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            t.cancel()
        for t in tasks:
            try:
                await t
            except BaseException:
                pass
        try:
            await ws.close()
        except BaseException:
            pass
        try:
            writer.close()
            await writer.wait_closed()
        except BaseException:
            pass


async def _handle_client(reader, writer):
    peer = writer.get_extra_info('peername')
    label = f"{peer[0]}:{peer[1]}" if peer else "?"

    try:
        hdr = await asyncio.wait_for(reader.readexactly(2), timeout=10)
        if hdr[0] != 5:
            writer.close()
            return
        nmethods = hdr[1]
        await reader.readexactly(nmethods)
        writer.write(b'\x05\x00')
        await writer.drain()

        req = await asyncio.wait_for(reader.readexactly(4), timeout=10)
        _ver, cmd, _rsv, atyp = req
        if cmd != 1:
            writer.close()
            return

        if atyp == 1:
            raw = await reader.readexactly(4)
            dst = _socket.inet_ntoa(raw)
        elif atyp == 3:
            dlen = (await reader.readexactly(1))[0]
            dst = (await reader.readexactly(dlen)).decode()
        else:
            writer.close()
            return

        port = struct.unpack('!H', await reader.readexactly(2))[0]

        if not _is_telegram_ip(dst):
            try:
                rr, rw = await asyncio.wait_for(asyncio.open_connection(dst, port), timeout=10)
            except Exception:
                writer.close()
                return
            writer.write(b'\x05\x00')
            await writer.drain()
            await asyncio.gather(asyncio.create_task(reader.readinto(rr)), asyncio.create_task(rr.readinto(writer)))
            return

        writer.write(b'\x05\x00')
        await writer.drain()

        try:
            init = await asyncio.wait_for(reader.readexactly(64), timeout=15)
        except asyncio.IncompleteReadError:
            return

        dc, is_media = _dc_from_init(init)
        if dc is None and dst in _IP_TO_DC:
            dc, is_media = _IP_TO_DC.get(dst)

        if dc is None or dc not in _dc_opt:
            writer.close()
            return

        domains = _ws_domains(dc, is_media or True)
        target = _dc_opt[dc]

        ws = None
        for domain in domains:
            try:
                ws = await RawWebSocket.connect(target, domain, timeout=5)
                break
            except Exception:
                continue

        if ws is None:
            writer.close()
            return

        await ws.send(init)
        await _bridge_ws(reader, writer, ws, label, dc=dc)

    except Exception:
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def _run(port: int, dc_opt: Dict[int, Optional[str]], stop_event=None, host: str = '0.0.0.0'):
    global _dc_opt
    _dc_opt = dc_opt

    server = await asyncio.start_server(_handle_client, host, port)

    log.info("=" * 40)
    log.info("  Telegram WS Proxy")
    log.info(f"  Listening on {host}:{port}")
    log.info("=" * 40)

    async with server:
        await server.serve_forever()


def run_proxy(port: int, dc_opt: Dict[int, str], stop_event=None, host: str = '0.0.0.0'):
    asyncio.run(_run(port, dc_opt, stop_event, host))