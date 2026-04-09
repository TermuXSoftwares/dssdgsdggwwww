"""
UnBlock v1.0.0 - Modern GUI for WebSocket Proxy
By MORALFUCK & Flowseal
"""
from __future__ import annotations

import json
import logging
import os
import sys
import webbrowser
import shutil
from pathlib import Path
from typing import Dict, Optional, List

import asyncio as _asyncio

AUTOSTART_DESKTOP = Path.home() / ".config" / "autostart" / "unblock.desktop"

from PyQt6.QtCore import (
    Qt, QSize, QTimer, QThread, pyqtSignal, QPoint,
)
from PyQt6.QtGui import (
    QFont, QIcon, QPalette, QColor, QPixmap,
    QPainter, QCursor, QAction, QPainterPath,
    QMouseEvent, QPaintEvent, QCloseEvent
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QGridLayout,
    QScrollArea, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QMessageBox,
    QLineEdit, QCheckBox, QSpinBox
)

APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "UnBlock"
CONFIG_FILE = APP_DIR / "config.json"
LOG_FILE = APP_DIR / "proxy.log"

COLORS = {
    "primary": "#3390ec",
    "primary_hover": "#2b7cd4",
    "primary_light": "#e6f3ff",
    "bg_main": "#ffffff",
    "bg_secondary": "#f5f7fa",
    "bg_sidebar": "#f0f4f8",
    "text_primary": "#1c1c1e",
    "text_secondary": "#8e8e93",
    "success": "#34c759",
    "warning": "#ff9500",
    "error": "#ff3b30",
    "border": "#e5e5e5",
}

DEFAULT_CONFIG = {
    "port": 1080,
    "host": "127.0.0.1",
    "dc_ip": ["2:149.154.167.220", "4:149.154.167.220"],
    "verbose": False,
    "autostart": False,
}

log = logging.getLogger("unblock-gui")

def get_autostart_enabled() -> bool:
    return AUTOSTART_DESKTOP.exists()

def set_autostart_enabled(enabled: bool) -> bool:
    try:
        if enabled:
            AUTOSTART_DESKTOP.parent.mkdir(parents=True, exist_ok=True)
            exe_path = shutil.which("python3") or shutil.which("python") or sys.executable
            script_path = Path(__file__).resolve()
            content = f"""[Desktop Entry]
Type=Application
Name=UnBlock
Exec={exe_path} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
            AUTOSTART_DESKTOP.write_text(content, encoding="utf-8")
        else:
            if AUTOSTART_DESKTOP.exists():
                AUTOSTART_DESKTOP.unlink()
        return True
    except Exception:
        return False

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
        except Exception as exc:
            log.warning("Failed to load config: %s", exc)
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    _ensure_dirs()
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

ICONS = {
    "home": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M12 3L4 9v12h5v-7h6v7h5V9z"/></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>',
    "donate": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#34c759"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    "play": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff"><path d="M8 5v14l11-7z"/></svg>',
    "stop": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffffff"><path d="M6 6h12v12H6z"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>',
    "telegram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.75-.33 1.42.18 1.16 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z"/></svg>',
    "chat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3390ec"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>',
    "close": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#666666"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>',
    "minimize": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#666666"><path d="M19 13H5v-2h14v2z"/></svg>',
    "maximize": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#666666"><path d="M18 4H6c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H6V6h12v12z"/></svg>',
}

def create_icon_from_svg(svg_string: str, size: int = 32) -> QIcon:
    from PyQt6.QtSvg import QSvgRenderer
    svg_bytes = svg_string.strip().encode('utf-8')
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer = QSvgRenderer(svg_bytes)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

class RoundedButton(QPushButton):
    def __init__(self, text: str = "", parent=None, icon: QIcon = None,
                 bg_color: str = None, hover_color: str = None):
        super().__init__(text, parent)
        self._bg_color = bg_color or COLORS["primary"]
        self._hover_color = hover_color or COLORS["primary_hover"]
        self._current_color = self._bg_color
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._current_color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:pressed {{ background-color: #1a6bb8; }}
            QPushButton:disabled {{ background-color: #c0c0c0; }}
        """)

    def enterEvent(self, event):
        self._current_color = self._hover_color
        self._update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._current_color = self._bg_color
        self._update_style()
        super().leaveEvent(event)

class SidebarButton(QPushButton):
    def __init__(self, text: str, icon: QIcon, parent=None):
        super().__init__(text, parent)
        self._is_selected = False
        self.setIcon(icon)
        self.setIconSize(QSize(24, 24))
        self.setCheckable(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._update_style()

    def _update_style(self):
        bg = COLORS["primary_light"] if self._is_selected else "transparent"
        text_color = COLORS["primary"] if self._is_selected else COLORS["text_secondary"]
        font_weight = "600" if self._is_selected else "500"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                border-radius: 10px;
                padding: 14px 20px;
                font-size: 14px;
                font-weight: {font_weight};
                text-align: left;
                padding-left: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS["primary_light"]};
                color: {COLORS["primary"]};
            }}
        """)

    def set_selected(self, selected: bool):
        self._is_selected = selected
        self.setChecked(selected)
        self._update_style()

class StatusIndicator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = "stopped"
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dot = QLabel()
        self.dot.setFixedSize(12, 12)
        self.dot.setStyleSheet("border-radius: 6px;")
        self.label = QLabel("Остановлено")
        self.label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(self.dot)
        layout.addWidget(self.label)
        self._apply_style(COLORS["error"])

    def _apply_style(self, color: str):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 59, 48, 48);
                border-radius: 20px;
            }}
        """)
        self.dot.setStyleSheet(f"background-color: {color};")
        self.label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 600;")

    def set_status(self, status: str):
        self._status = status
        if status == "running":
            self.label.setText("Запущено")
            self._apply_style(COLORS["success"])
        else:
            self.label.setText("Остановлено")
            self._apply_style(COLORS["error"])

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(8)
        self.title_label = QLabel("UnBlock v1.0.0 - By MORALFUCK & Flowseal")
        self.title_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #333333; padding-left: 8px;")
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.min_btn = self._create_button("minimize")
        self.min_btn.clicked.connect(lambda: self.window().showMinimized())
        layout.addWidget(self.min_btn)
        self.max_btn = self._create_button("maximize")
        self.max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(self.max_btn)
        self.close_btn = self._create_button("close")
        self.close_btn.setStyleSheet("QPushButton { background-color: transparent; border: none; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #e81123; }")
        self.close_btn.clicked.connect(self._on_close_clicked)
        layout.addWidget(self.close_btn)

    def _create_button(self, icon_name: str) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(32, 32)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon = create_icon_from_svg(ICONS[icon_name], 20)
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))
        btn.setStyleSheet("QPushButton { background-color: transparent; border: none; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #f0f0f0; } QPushButton:pressed { background-color: #e0e0e0; }")
        return btn

    def _toggle_maximize(self):
        win = self.window()
        if win.isMaximized():
            win.showNormal()
        else:
            win.showMaximized()

    def _on_close_clicked(self):
        win = self.window()
        if hasattr(win, '_close_app'):
            win._close_app()
        else:
            win.close()

class RoundedWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._border_radius = 20
        self._border_width = 1
        self._drag_pos = None

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(
            float(self._border_width),
            float(self._border_width),
            float(self.width() - 2 * self._border_width),
            float(self.height() - 2 * self._border_width),
            float(self._border_radius),
            float(self._border_radius)
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 50:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None:
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

class AnimatedStack(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_index = 0

    def setCurrentIndex(self, index):
        if index == self._current_index:
            return
        super().setCurrentIndex(index)
        self._current_index = index

class HomePage(QWidget):
    start_proxy = pyqtSignal()
    stop_proxy = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(
                180, 180, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("UnBlock")
            logo_label.setStyleSheet("font-size: 56px; font-weight: bold; color: #3390ec;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(51, 144, 236, 100))
        shadow.setOffset(0, 0)
        logo_label.setGraphicsEffect(shadow)
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.action_button = RoundedButton("Запустить")
        self.action_button.setFixedSize(220, 60)
        play_icon = create_icon_from_svg(ICONS["play"], 24)
        self.action_button.setIcon(play_icon)
        self.action_button.clicked.connect(self._on_action_clicked)
        layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(40)

    def _on_action_clicked(self):
        if self._running:
            self.stop_proxy.emit()
        else:
            self.start_proxy.emit()

    def set_running(self, running: bool):
        self._running = running
        if running:
            self.status_indicator.set_status("running")
            self.action_button.setText("Остановить")
            stop_icon = create_icon_from_svg(ICONS["stop"], 24)
            self.action_button.setIcon(stop_icon)
            self.action_button._bg_color = COLORS["error"]
            self.action_button._hover_color = "#e63946"
        else:
            self.status_indicator.set_status("stopped")
            self.action_button.setText("Запустить")
            play_icon = create_icon_from_svg(ICONS["play"], 24)
            self.action_button.setIcon(play_icon)
            self.action_button._bg_color = COLORS["primary"]
            self.action_button._hover_color = COLORS["primary_hover"]
        self.action_button._update_style()

class SettingsPage(QWidget):
    settings_changed = pyqtSignal(dict)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(24)
        title = QLabel("Настройки")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1c1c1e;")
        layout.addWidget(title)
        layout.addSpacing(20)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { background: #f0f4f8; width: 12px; border-radius: 6px; margin: 0px; } QScrollBar::handle:vertical { background: #3390ec; min-height: 30px; border-radius: 6px; } QScrollBar::handle:vertical:hover { background: #2b7cd4; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; } QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.addWidget(self._create_section_title("Основные настройки"))
        content_layout.addWidget(self._create_label("IP-адрес прокси"))
        self.host_input = QLineEdit(self._config.get("host", "127.0.0.1"))
        self._style_input(self.host_input)
        content_layout.addWidget(self.host_input)
        content_layout.addWidget(self._create_label("Порт прокси"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self._config.get("port", 1080))
        self.port_input.setFixedHeight(48)
        self.port_input.setStyleSheet("QSpinBox { background-color: #f5f7fa; border: 1px solid #e5e5e5; border-radius: 10px; padding: 12px 16px; font-size: 14px; color: #1c1c1e; } QSpinBox:focus { border-color: #3390ec; } QSpinBox::up-button, QSpinBox::down-button { width: 20px; height: 20px; border: none; background: #3390ec; border-radius: 4px; margin: 2px; } QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #2b7cd4; } QSpinBox::up-button:pressed, QSpinBox::down-button:pressed { background: #1a6bb8; } QSpinBox::up-arrow { image: none; border: none; width: 8px; height: 8px; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 4px solid white; margin-top: 2px; } QSpinBox::down-arrow { image: none; border: none; width: 8px; height: 8px; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid white; margin-bottom: 2px; }")
        content_layout.addWidget(self.port_input)
        content_layout.addWidget(self._create_section_title("DC маппинги"))
        content_layout.addWidget(self._create_label("DC IP (разделитель точка с запятой)"))
        self.dc_text = QLineEdit("; ".join(self._config.get("dc_ip", DEFAULT_CONFIG["dc_ip"])))
        self._style_input(self.dc_text)
        content_layout.addWidget(self.dc_text)
        content_layout.addWidget(self._create_section_title("Дополнительно"))
        self.verbose_check = QCheckBox("Подробное логирование (verbose)")
        self.verbose_check.setChecked(self._config.get("verbose", False))
        self.verbose_check.setStyleSheet(f"QCheckBox {{ font-size: 14px; color: {COLORS['text_primary']}; spacing: 10px; }} QCheckBox::indicator {{ width: 20px; height: 20px; border-radius: 6px; border: 2px solid {COLORS['border']}; background: white; }} QCheckBox::indicator:checked {{ background-color: {COLORS['primary']}; border-color: {COLORS['primary']}; }}")
        content_layout.addWidget(self.verbose_check)
        self.autostart_check = QCheckBox("Автозапуск при старте системы")
        self.autostart_check.setChecked(self._config.get("autostart", False))
        self.autostart_check.setStyleSheet(f"QCheckBox {{ font-size: 14px; color: {COLORS['text_primary']}; spacing: 10px; }} QCheckBox::indicator {{ width: 20px; height: 20px; border-radius: 6px; border: 2px solid {COLORS['border']}; background: white; }} QCheckBox::indicator:checked {{ background-color: {COLORS['primary']}; border-color: {COLORS['primary']}; }}")
        content_layout.addWidget(self.autostart_check)
        content_layout.addStretch()
        self.save_button = RoundedButton("Сохранить настройки")
        self.save_button.setFixedHeight(54)
        self.save_button.clicked.connect(self._on_save)
        content_layout.addWidget(self.save_button)
        content_layout.addSpacing(20)
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _create_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 16px; font-weight: 700; color: #3390ec; margin-top: 10px;")
        return label

    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1c1c1e;")
        return label

    def _style_input(self, widget):
        widget.setStyleSheet("QLineEdit { background-color: #f5f7fa; border: 1px solid #e5e5e5; border-radius: 10px; padding: 12px 16px; font-size: 14px; color: #1c1c1e; } QLineEdit:focus { border-color: #3390ec; }")
        widget.setFixedHeight(48)

    def _on_save(self):
        try:
            host = self.host_input.text().strip()
            port = self.port_input.value()
            dc_ips = [x.strip() for x in self.dc_text.text().split(";") if x.strip()]
            verbose = self.verbose_check.isChecked()
            autostart = self.autostart_check.isChecked()
            import socket
            socket.inet_aton(host)
            if not (1 <= port <= 65535):
                raise ValueError("Некорректный порт")
            new_config = {
                "host": host, "port": port, "dc_ip": dc_ips,
                "verbose": verbose, "autostart": autostart,
            }
            save_config(new_config)
            self._config = new_config
            set_autostart_enabled(autostart)
            QMessageBox.information(self, "Успешно", "Настройки сохранены!\nПрокси будет перезапущен.")
            self.settings_changed.emit(new_config)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Некорректные настройки:\n{e}")

class SupportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        title = QLabel("Поддержать нас")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1c1c1e;")
        layout.addWidget(title)
        layout.addSpacing(20)
        desc = QLabel("Если вам нравится этот проект, вы можете поддержать разработчика.\n\nЛюбая помощь важна для развития и улучшения UnBlock!")
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 16px; color: #8e8e93; line-height: 1.6;")
        layout.addWidget(desc)
        layout.addSpacing(40)
        self.donate_button = RoundedButton("Поддержать проект")
        self.donate_button.setFixedSize(260, 60)
        donate_icon = create_icon_from_svg(ICONS["donate"], 28)
        self.donate_button.setIcon(donate_icon)
        self.donate_button.clicked.connect(self._open_donate)
        layout.addWidget(self.donate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def _open_donate(self):
        webbrowser.open("https://t.me/moralfuck_project/36")

class InfoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        title = QLabel("О проекте")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1c1c1e;")
        layout.addWidget(title)
        layout.addSpacing(20)
        desc = QLabel("<b>UnBlock</b> — это современный прокси для Telegram Desktop,\nкоторый ускоряет работу мессенджера через WebSocket.\n\nОснован на проекте:\n<a href='https://github.com/Flowseal/tg-ws-proxy' style='color: #3390ec;'>github.com/Flowseal/tg-ws-proxy</a>")
        desc.setWordWrap(True)
        desc.setOpenExternalLinks(True)
        desc.setStyleSheet("font-size: 15px; color: #1c1c1e; line-height: 1.6;")
        layout.addWidget(desc)
        layout.addSpacing(30)
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(16)
        buttons_layout.setHorizontalSpacing(20)
        self.social_buttons = [
            ("Автор", "https://t.me/moralfuckog", "user"),
            ("Проект", "https://t.me/moralfuck_project", "telegram"),
            ("Поддержать нас", "https://t.me/moralfuck_project/36", "donate"),
            ("По всем вопросам", "https://t.me/moralfuckadminbot", "chat"),
        ]
        for i, (name, url, icon_name) in enumerate(self.social_buttons):
            btn = self._create_social_button(name, icon_name, url)
            buttons_layout.addWidget(btn, i // 2, i % 2)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        version = QLabel("UnBlock v1.0.0")
        version.setStyleSheet("font-size: 12px; color: #8e8e93;")
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)

    def _create_social_button(self, text: str, icon_name: str, url: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(200, 56)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(lambda: webbrowser.open(url))
        icon = create_icon_from_svg(ICONS[icon_name], 24)
        btn.setIcon(icon)
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 14px; padding-left: 20px; font-size: 14px; font-weight: 500; }} QPushButton:hover {{ background-color: {COLORS['primary_light']}; border-color: {COLORS['primary']}; color: {COLORS['primary']}; }}")
        return btn

class ProxyWorker(QThread):
    started = pyqtSignal()
    stopped = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._stop_event = None
        self._loop = None

    def run(self):
        loop = _asyncio.new_event_loop()
        _asyncio.set_event_loop(loop)
        self._loop = loop
        self._stop_event = _asyncio.Event()
        try:
            dc_opt = self._parse_dc_ip_list(self._config.get("dc_ip", []))
            loop.run_until_complete(
                self._run_proxy(
                    self._config.get("port", 1080),
                    dc_opt,
                    stop_event=self._stop_event,
                    host=self._config.get("host", "127.0.0.1")
                )
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()
            self.stopped.emit()

    def _parse_dc_ip_list(self, dc_ip_list: List[str]) -> Dict[int, str]:
        result = {}
        for item in dc_ip_list:
            if ':' not in item:
                raise ValueError(f"Invalid format: {item}")
            dc, ip = item.split(':', 1)
            result[int(dc)] = ip
        return result

    async def _run_proxy(self, port: int, dc_opt: dict, stop_event, host: str):
        import proxy.tg_ws_proxy as tg_ws_proxy
        await tg_ws_proxy._run(port, dc_opt, stop_event=stop_event, host=host)

    def stop(self):
        try:
            if self._stop_event and self._loop:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            self.wait(1000)
        except:
            pass

class MainWindow(RoundedWindow):
    def __init__(self):
        super().__init__()
        self._config = load_config()
        self._proxy_worker: Optional[ProxyWorker] = None
        self._proxy_running = False
        self._hidden_to_tray = False
        self._setup_window()
        self._setup_ui()
        self._setup_tray()

    def _setup_window(self):
        self.setWindowTitle("UnBlock v1.0.0 - By MORALFUCK & Flowseal")
        self.setFixedSize(850, 600)
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)
        content_frame = QFrame()
        content_frame.setStyleSheet(f"QFrame {{ background-color: {COLORS['bg_main']}; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; }}")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.sidebar = self._create_sidebar()
        content_layout.addWidget(self.sidebar)
        self.stack = AnimatedStack()
        self.stack.setStyleSheet(f"QStackedWidget {{ background-color: {COLORS['bg_main']}; }}")
        self.stack.addWidget(HomePage())
        settings_page = SettingsPage(self._config)
        if get_autostart_enabled():
            settings_page._config["autostart"] = True
            settings_page.autostart_check.setChecked(True)
        self.stack.addWidget(settings_page)
        self.stack.addWidget(SupportPage())
        self.stack.addWidget(InfoPage())
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame)
        home_page = self.stack.widget(0)
        home_page.start_proxy.connect(self._start_proxy)
        home_page.stop_proxy.connect(self._stop_proxy)
        settings_page = self.stack.widget(1)
        settings_page.settings_changed.connect(self._on_settings_changed)

    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"QFrame {{ background-color: {COLORS['bg_sidebar']}; border-bottom-left-radius: 20px; }}")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)
        logo_label = QLabel("UnBlock")
        logo_label.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {COLORS['primary']}; padding: 16px 12px;")
        layout.addWidget(logo_label)
        layout.addSpacing(20)
        self.nav_buttons = {}
        nav_items = [
            ("Главная", "home", 0),
            ("Настройки", "settings", 1),
            ("Поддержать нас", "donate", 2),
            ("Инфо", "info", 3),
        ]
        for text, icon_name, index in nav_items:
            icon = create_icon_from_svg(ICONS[icon_name], 28)
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, idx=index: self._on_nav_clicked(idx))
            layout.addWidget(btn)
            self.nav_buttons[text] = btn
        self.nav_buttons["Главная"].set_selected(True)
        layout.addStretch()
        version = QLabel("v1.0.0")
        version.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding: 12px;")
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignBottom)
        return sidebar

    def _on_nav_clicked(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn_name in enumerate(["Главная", "Настройки", "Поддержать нас", "Инфо"]):
            btn = self.nav_buttons[btn_name]
            btn.set_selected(i == index)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(COLORS["primary"]))
            self.tray_icon.setIcon(QIcon(pixmap))
        tray_menu = QMenu()
        tray_menu.setStyleSheet("QMenu { background-color: #ffffff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 8px 0px; } QMenu::item { background-color: transparent; padding: 10px 20px; font-size: 14px; color: #1c1c1e; margin: 2px 8px; border-radius: 6px; } QMenu::item:selected { background-color: #e6f3ff; color: #3390ec; } QMenu::separator { height: 1px; background: #e5e5e5; margin: 4px 8px; }")
        self.tray_show_action = QAction("Показать", self)
        self.tray_show_action.triggered.connect(self._toggle_visibility)
        tray_menu.addAction(self.tray_show_action)
        tray_menu.addSeparator()
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(lambda: self._show_page(1))
        tray_menu.addAction(settings_action)
        info_action = QAction("Инфо", self)
        info_action.triggered.connect(lambda: self._show_page(3))
        tray_menu.addAction(info_action)
        tray_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self._close_app)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_visibility()

    def _toggle_visibility(self):
        if self.isVisible() and not self.isMinimized():
            self._hide_window()
        else:
            self._show_window()

    def _hide_window(self):
        self._hidden_to_tray = True
        self.hide()
        self._update_tray_text()

    def _show_window(self):
        self._hidden_to_tray = False
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.activateWindow()
        self.raise_()
        self._update_tray_text()

    def _update_tray_text(self):
        if hasattr(self, 'tray_show_action'):
            if self.isVisible() and not self.isMinimized():
                self.tray_show_action.setText("Скрыть")
            else:
                self.tray_show_action.setText("Показать")

    def _show_page(self, index: int):
        self._show_window()
        self.stack.setCurrentIndex(index)
        for i, btn_name in enumerate(["Главная", "Настройки", "Поддержать нас", "Инфо"]):
            btn = self.nav_buttons[btn_name]
            btn.set_selected(i == index)

    def _start_proxy(self):
        if self._proxy_running:
            return
        self._proxy_worker = ProxyWorker(self._config)
        self._proxy_worker.started.connect(self._on_proxy_started)
        self._proxy_worker.stopped.connect(self._on_proxy_stopped)
        self._proxy_worker.error.connect(self._on_proxy_error)
        self._proxy_worker.start()
        home_page = self.stack.widget(0)
        home_page.set_running(True)
        self._proxy_running = True

    def _stop_proxy(self):
        if self._proxy_worker:
            try:
                self._proxy_worker.stop()
            except:
                pass
            self._proxy_worker = None
        self._proxy_running = False

    def _on_proxy_started(self):
        log.info("Proxy started")

    def _on_proxy_stopped(self):
        log.info("Proxy stopped")
        self._proxy_running = False
        self._proxy_worker = None
        home_page = self.stack.widget(0)
        home_page.set_running(False)

    def _on_proxy_error(self, error_msg: str):
        log.error(f"Proxy error: {error_msg}")
        self._proxy_running = False
        self._proxy_worker = None
        home_page = self.stack.widget(0)
        home_page.set_running(False)
        QMessageBox.critical(self, "Ошибка прокси", f"Не удалось запустить прокси:\n{error_msg}")

    def _on_settings_changed(self, new_config: dict):
        self._config = new_config
        if self._proxy_running:
            self._stop_proxy()
            QTimer.singleShot(600, self._start_proxy)

    def _close_app(self):
        try:
            if self._proxy_running:
                self._stop_proxy()
        except:
            pass
        try:
            self.tray_icon.hide()
        except:
            pass
        self.close()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        if self._hidden_to_tray:
            event.accept()
        else:
            event.ignore()
            self._hidden_to_tray = True
            self.hide()
            self.tray_icon.showMessage(
                "UnBlock",
                "Приложение свёрнуто в трей. Для выхода используйте меню трея.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def showEvent(self, event):
        super().showEvent(event)
        self._update_tray_text()

def setup_logging(verbose: bool = False):
    _ensure_dirs()
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
        except Exception:
            pass
    fh = logging.FileHandler(str(LOG_FILE), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-5s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"))
    root.addHandler(fh)

def main():
    _ensure_dirs()
    config = load_config()
    save_config(config)
    if config.get("autostart", False):
        set_autostart_enabled(True)
    setup_logging(config.get("verbose", False))
    app = QApplication(sys.argv)
    app.setApplicationName("UnBlock")
    app.setOrganizationName("MORALFUCK")
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["bg_main"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["bg_main"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["bg_main"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text_primary"]))
    app.setPalette(palette)
    app.setStyleSheet("""
        * { outline: none; }
        QLabel {
            qproperty-textInteractionFlags: NoTextInteraction;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
