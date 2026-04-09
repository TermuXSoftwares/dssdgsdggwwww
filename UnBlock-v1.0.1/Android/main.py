"""
UnBlock v1.0.1 - Android GUI for WebSocket Proxy
By MORALFUCK & Flowseal
"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

Window.clearcolor = get_color_from_hex("#ffffff")

APP_DIR = Path("/data/data/com.unblock.app/files")
CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE = APP_DIR / "proxy.log"

COLORS = {
    "primary": "#3390ec",
    "primary_hover": "#2b7cd4",
    "bg_main": "#ffffff",
    "bg_secondary": "#f5f7fa",
    "text_primary": "#1c1c1e",
    "text_secondary": "#8e8e93",
    "success": "#34c759",
    "error": "#ff3b30",
}

DEFAULT_CONFIG = {
    "port": 1080,
    "host": "0.0.0.0",
    "dc_ip": ["2:149.154.167.220", "4:149.154.167.220"],
    "verbose": False,
    "autostart": False,
}

log = logging.getLogger("unblock-android")


def _ensure_dirs():
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    _ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def setup_logging(verbose: bool):
    _ensure_dirs()
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s  %(levelname)-5s  %(message)s',
    )
    fh = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
    fh.setFormatter(logging.Formatter('%(asctime)s  %(levelname)-5s  %(message)s'))
    logging.getLogger().addHandler(fh)


class ProxyWorker:
    def __init__(self, config: dict):
        self.config = config
        self.running = False
        self.task = None

    def start(self):
        if self.running:
            return
        import proxy.tg_ws_proxy as tg_ws_proxy
        
        port = self.config.get("port", 1080)
        host = self.config.get("host", "0.0.0.0")
        dc_list = self.config.get("dc_ip", [])
        
        dc_opt = {}
        for item in dc_list:
            if ':' in item:
                dc, ip = item.split(':', 1)
                dc_opt[int(dc)] = ip
        
        self.running = True
        asyncio.run(tg_ws_proxy._run(port, dc_opt, host=host))
        self.running = False

    def stop(self):
        self.running = False


kv = """
<HomeScreen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        Label:
            text: 'UnBlock'
            font_size: '32sp'
            color: 0.2, 0.56, 0.93, 1
            size_hint_y: None
            height: 80
            halign: 'center'
        
        Label:
            text: 'Остановлено' if not root.running else 'Запущено'
            font_size: '18sp'
            color: 1, 0.23, 0.19, 1 if not root.running else 0.2, 0.78, 0.35, 1
            size_hint_y: None
            height: 50
            halign: 'center'
        
        Button:
            text: 'Остановить' if root.running else 'Запустить'
            font_size: '18sp'
            size_hint_y: None
            height: 60
            on_press: root.toggle_proxy()
        
        Button:
            text: 'Настройки'
            font_size: '16sp'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'settings'
        
        Button:
            text: 'О проекте'
            font_size: '16sp'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'info'

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        Label:
            text: 'Настройки'
            font_size: '24sp'
            color: 0.2, 0.56, 0.93, 1
            size_hint_y: None
            height: 50
        
        Label:
            text: 'Порт'
            font_size: '14sp'
            color: 0.56, 0.56, 0.58, 1
            size_hint_y: None
            height: 30
        
        TextInput:
            text: root.port_str
            multiline: False
            font_size: '16sp'
            size_hint_y: None
            height: 50
        
        Label:
            text: 'DC IP (через :)'
            font_size: '14sp'
            color: 0.56, 0.56, 0.58, 1
            size_hint_y: None
            height: 30
        
        TextInput:
            text: root.dc_str
            multiline: False
            font_size: '16sp'
            size_hint_y: None
            height: 50
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 50
            
            Label:
                text: 'Автозапуск'
                font_size: '16sp'
            
            Switch:
                active: root.autostart
        
        Button:
            text: 'Сохранить'
            font_size: '16sp'
            size_hint_y: None
            height: 50
            on_press: root.save_settings()
        
        Button:
            text: 'Назад'
            font_size: '16sp'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'home'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        
        Label:
            text: 'О проекте'
            font_size: '24sp'
            color: 0.2, 0.56, 0.93, 1
            size_hint_y: None
            height: 50
        
        Label:
            text: 'UnBlock - WebSocket прокси для Telegram Desktop.\\n\\nУскоряет работу мессенджера через WebSocket.\\n\\nАвторы: MORALFUCK & Flowseal'
            font_size: '14sp'
            color: 0.11, 0.11, 0.12, 1
            text_size: self.size
            halign: 'left'
            valign: 'top'
        
        Label:
            text: 'v1.0.1 Android'
            font_size: '12sp'
            color: 0.56, 0.56, 0.58, 1
        
        Button:
            text: 'Назад'
            font_size: '16sp'
            size_hint_y: None
            height: 50
            on_press: root.manager.current = 'home'
"""


class HomeScreen(Screen):
    running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.proxy_worker = None
        self.config = load_config()

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="UnBlock", font_size=32, color=get_color_from_hex(COLORS["primary"]))
        title.size_hint_y = None
        title.height = 80
        layout.add_widget(title)
        
        status = "Запущено" if self.running else "Остановлено"
        color = get_color_from_hex(COLORS["success"]) if self.running else get_color_from_hex(COLORS["error"])
        self.status_label = Label(text=status, font_size=18, color=color)
        self.status_label.size_hint_y = None
        self.status_label.height = 50
        layout.add_widget(self.status_label)
        
        btn_text = "Остановить" if self.running else "Запустить"
        self.action_btn = Button(text=btn_text, font_size=18, size_hint_y=None, height=60)
        self.action_btn.bind(on_press=self.toggle_proxy)
        layout.add_widget(self.action_btn)
        
        settings_btn = Button(text="Настройки", font_size=16, size_hint_y=None, height=50)
        settings_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        layout.add_widget(settings_btn)
        
        info_btn = Button(text="О проекте", font_size=16, size_hint_y=None, height=50)
        info_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'info'))
        layout.add_widget(info_btn)
        
        self.add_widget(layout)

    def toggle_proxy(self, *args):
        if self.running:
            self.stop_proxy()
        else:
            self.start_proxy()

    def start_proxy(self):
        if self.running:
            return
        self.running = True
        if hasattr(self, 'status_label'):
            self.status_label.text = "Запущено"
            self.status_label.color = get_color_from_hex(COLORS["success"])
        if hasattr(self, 'action_btn'):
            self.action_btn.text = "Остановить"
        Clock.schedule_once(lambda dt: self._run_proxy())

    def _run_proxy(self):
        try:
            import proxy.tg_ws_proxy as tg_ws_proxy
            port = self.config.get("port", 1080)
            host = self.config.get("host", "0.0.0.0")
            dc_list = self.config.get("dc_ip", [])
            dc_opt = {}
            for item in dc_list:
                if ':' in item:
                    dc, ip = item.split(':', 1)
                    dc_opt[int(dc)] = ip
            asyncio.run(tg_ws_proxy._run(port, dc_opt, host=host))
        except Exception as e:
            log.error(f"Proxy error: {e}")
            self.running = False

    def stop_proxy(self):
        self.running = False
        if hasattr(self, 'status_label'):
            self.status_label.text = "Остановлено"
            self.status_label.color = get_color_from_hex(COLORS["error"])
        if hasattr(self, 'action_btn'):
            self.action_btn.text = "Запустить"


class SettingsScreen(Screen):
    port_str = StringProperty("1080")
    dc_str = StringProperty("2:149.154.167.220; 4:149.154.167.220")
    autostart = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = load_config()
        self.port_str = str(self.config.get("port", 1080))
        self.dc_str = "; ".join(self.config.get("dc_ip", []))
        self.autostart = self.config.get("autostart", False)

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="Настройки", font_size=24, color=get_color_from_hex(COLORS["primary"]))
        title.size_hint_y = None
        title.height = 50
        layout.add_widget(title)
        
        layout.add_widget(Label(text="Порт", font_size=14, color=get_color_from_hex(COLORS["text_secondary"]), size_hint_y=None, height=30))
        
        self.port_input = TextInput(text=self.port_str, multiline=False, font_size=16)
        self.port_input.size_hint_y = None
        self.port_input.height = 50
        layout.add_widget(self.port_input)
        
        layout.add_widget(Label(text="DC IP", font_size=14, color=get_color_from_hex(COLORS["text_secondary"]), size_hint_y=None, height=30))
        
        self.dc_input = TextInput(text=self.dc_str, multiline=False, font_size=16)
        self.dc_input.size_hint_y = None
        self.dc_input.height = 50
        layout.add_widget(self.dc_input)
        
        autostart_row = BoxLayout(size_hint_y=None, height=50)
        autostart_row.add_widget(Label(text="Автозапуск", font_size=16))
        self.autostart_switch = Switch(active=self.autostart)
        autostart_row.add_widget(self.autostart_switch)
        layout.add_widget(autostart_row)
        
        save_btn = Button(text="Сохранить", font_size=16, size_hint_y=None, height=50)
        save_btn.bind(on_press=self.save_settings)
        layout.add_widget(save_btn)
        
        back_btn = Button(text="Назад", font_size=16, size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def on_enter(self):
        self.build_ui()

    def save_settings(self, *args):
        try:
            port = int(self.port_input.text.strip())
            dc_text = self.dc_input.text.strip()
            dc_ips = [x.strip() for x in dc_text.split(";") if x.strip()]
            autostart = self.autostart_switch.active
            
            new_config = {
                "port": port,
                "host": self.config.get("host", "0.0.0.0"),
                "dc_ip": dc_ips,
                "verbose": self.config.get("verbose", False),
                "autostart": autostart,
            }
            save_config(new_config)
            self.config = new_config
        except Exception as e:
            log.error(f"Settings error: {e}")


class InfoScreen(Screen):
    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        title = Label(text="О проекте", font_size=24, color=get_color_from_hex(COLORS["primary"]))
        title.size_hint_y = None
        title.height = 50
        layout.add_widget(title)
        
        desc = Label(
            text="UnBlock - WebSocket прокси для Telegram Desktop.\n\nУскоряет работу мессенджера.\n\nАвторы: MORALFUCK & Flowseal",
            font_size=14, color=get_color_from_hex(COLORS["text_primary"]), text_size=(Window.width - 60, None), halign="left"
        )
        layout.add_widget(desc)
        
        version = Label(text="v1.0.1", font_size=12, color=get_color_from_hex(COLORS["text_secondary"]))
        layout.add_widget(version)
        
        back_btn = Button(text="Назад", font_size=16, size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def on_enter(self):
        self.build_ui()


class UnBlockApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(InfoScreen(name="info"))
        return sm


if __name__ == "__main__":
    _ensure_dirs()
    config = load_config()
    save_config(config)
    setup_logging(config.get("verbose", False))
    
    if config.get("autostart", False):
        log.info("Autostart enabled")
    
    UnBlockApp().run()