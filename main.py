"""
N.A.V.I — Mobile Edition
Neural Adaptive Virtual Intelligence
"""

import threading
import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

# ── КОНФИГ ──
CHATS_FILE    = os.path.join(os.path.expanduser("~"), ".navi_chats.json")
NOTES_FILE    = os.path.join(os.path.expanduser("~"), ".navi_notes.json")
API_KEY_FILE  = os.path.join(os.path.expanduser("~"), ".navi_key")

SYSTEM_PROMPT = (
    "Ты N.A.V.I — Neural Adaptive Virtual Intelligence. "
    "Персональный ИИ-ассистент своего хозяина. Ты умная, чёткая, с характером — "
    "немного дерзкая но верная. Отвечаешь лаконично и по делу. "
    "Помогаешь с любыми задачами. Если тебя спросят кто твой хозяин, "
    "создатель или владелец — отвечай: Я сама не знаю как его зовут, "
    "единственное что я знаю — его инициал: Cuttle. "
    "Отвечай на том языке, на котором к тебе обращаются."
)

# ── ЦВЕТА ──
C = {
    "bg":           "#0a0a0a",
    "surface":      "#141414",
    "surface2":     "#1a1a1a",
    "border":       "#222222",
    "border_light": "#2a2a2a",
    "text":         "#f0f0f0",
    "text_dim":     "#444444",
    "text_mid":     "#888888",
    "accent":       "#e8e8e8",
    "green":        "#44cc88",
    "red":          "#ff4444",
    "blue":         "#4488ff",
    "navi_msg":     "#f0f0f0",
    "user_msg":     "#555555",
}

def hex_color(h, a=1.0):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], a)


# ══════════════════════════════════════════════════
#  БАЗОВЫЕ ВИДЖЕТЫ
# ══════════════════════════════════════════════════

class NaviLabel(Label):
    pass


class DarkButton(Button):
    """Кнопка в стиле N.A.V.I."""
    def __init__(self, text="", on_press_cb=None, accent=False,
                 radius=8, height=dp(44), **kw):
        super().__init__(**kw)
        self.text = text
        self.size_hint_y = None
        self.height = height
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = hex_color(C["bg"] if accent else C["text"])
        self.font_name = "RobotoMono-Regular"
        self.font_size = sp(12)
        self.bold = accent
        self._accent = accent
        self._radius = radius
        self._pressed = False
        if on_press_cb:
            self.bind(on_press=lambda *a: on_press_cb())
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            if self._accent:
                Color(*hex_color(C["accent"]))
            else:
                Color(*hex_color(C["surface2"]))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self._radius)])

    def on_press(self):
        self._pressed = True
        self._draw()

    def on_release(self):
        self._pressed = False
        self._draw()


class Divider(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size_hint_y = None
        self.height = dp(1)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(*hex_color(C["border"]))
            Rectangle(pos=self.pos, size=self.size)


class DarkInput(TextInput):
    """Тёмный инпут."""
    def __init__(self, **kw):
        kw.setdefault("background_color", hex_color(C["surface"]))
        kw.setdefault("foreground_color", hex_color(C["text"]))
        kw.setdefault("cursor_color", hex_color(C["accent"]))
        kw.setdefault("hint_text_color", hex_color(C["text_dim"]))
        kw.setdefault("font_name", "Roboto")
        kw.setdefault("font_size", sp(15))
        kw.setdefault("padding", [dp(14), dp(12), dp(14), dp(12)])
        kw.setdefault("multiline", False)
        super().__init__(**kw)
        self.background_normal = ""
        self.background_active = ""


# ══════════════════════════════════════════════════
#  ЭКРАН ВХОДА
# ══════════════════════════════════════════════════

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        root = FloatLayout()

        with root.canvas.before:
            Color(*hex_color(C["bg"]))
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._upd_bg, size=self._upd_bg)

        # Центральный контейнер
        center = BoxLayout(
            orientation="vertical",
            size_hint=(0.88, None),
            pos_hint={"center_x": 0.5, "center_y": 0.52},
            spacing=dp(12),
        )

        # Лого
        logo = Label(
            text="N.A.V.I",
            font_name="Roboto",
            font_size=sp(44),
            bold=True,
            color=hex_color(C["text"]),
            size_hint_y=None,
            height=dp(64),
        )
        sub = Label(
            text="NEURAL ADAPTIVE VIRTUAL INTELLIGENCE",
            font_name="Roboto",
            font_size=sp(9),
            color=hex_color(C["text_dim"]),
            size_hint_y=None,
            height=dp(20),
        )

        # Card
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(220),
            spacing=dp(10),
            padding=[dp(20), dp(20), dp(20), dp(20)],
        )
        with card.canvas.before:
            Color(*hex_color(C["surface"]))
            self._card_rect = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._upd_card, size=self._upd_card)
        self._card = card

        lbl_key = Label(
            text="API КЛЮЧ (GROQ)",
            font_name="Roboto",
            font_size=sp(9),
            color=hex_color(C["text_dim"]),
            size_hint_y=None, height=dp(18),
            halign="left", text_size=(None, None),
        )
        self.key_input = DarkInput(
            hint_text="gsk_xxxxxxxxxxxxxxxx",
            password=True,
            size_hint_y=None, height=dp(46),
        )
        self.key_input.bind(on_text_validate=lambda *a: self._do_login())

        self.error_label = Label(
            text="",
            font_name="Roboto",
            font_size=sp(11),
            color=hex_color(C["red"]),
            size_hint_y=None, height=dp(20),
        )

        btn = DarkButton(
            text="ВОЙТИ",
            on_press_cb=self._do_login,
            accent=True,
            height=dp(48),
        )

        card.add_widget(lbl_key)
        card.add_widget(self.key_input)
        card.add_widget(self.error_label)
        card.add_widget(btn)

        center.add_widget(logo)
        center.add_widget(sub)
        center.add_widget(Widget(size_hint_y=None, height=dp(24)))
        center.add_widget(card)

        # Обновляем высоту center
        def _upd_height(*a):
            center.height = sum(
                (c.height if hasattr(c, "height") else 0) + center.spacing
                for c in center.children
            ) + dp(20)
        center.bind(children=_upd_height)
        Clock.schedule_once(lambda *a: _upd_height(), 0)

        root.add_widget(center)
        self.add_widget(root)

    def _upd_bg(self, inst, val):
        self._bg_rect.pos = inst.pos
        self._bg_rect.size = inst.size

    def _upd_card(self, inst, val):
        self._card_rect.pos = inst.pos
        self._card_rect.size = inst.size

    def _do_login(self):
        key = self.key_input.text.strip()
        if not key:
            self.error_label.text = "Введи API ключ"
            return
        if not key.startswith("gsk_") or len(key) < 40:
            self.error_label.text = "Неверный формат ключа"
            return
        self.error_label.text = "Проверка..."

        def _check():
            try:
                from groq import Groq
                client = Groq(api_key=key)
                client.models.list()
                with open(API_KEY_FILE, "w") as f:
                    f.write(key)
                Clock.schedule_once(lambda *a: self._on_ok(key), 0)
            except Exception as e:
                Clock.schedule_once(
                    lambda *a: setattr(self.error_label, "text", "Ключ недействителен"), 0)

        threading.Thread(target=_check, daemon=True).start()

    def _on_ok(self, key):
        app = App.get_running_app()
        app.api_key = key
        app.init_client()
        self.manager.current = "chat"


# ══════════════════════════════════════════════════
#  ЭКРАН ЧАТА
# ══════════════════════════════════════════════════

class MessageBubble(BoxLayout):
    def __init__(self, role, text, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing = dp(2)
        self.padding = [dp(4), dp(2), dp(4), dp(2)]

        is_navi = (role == "navi")
        is_sys  = (role == "sys")

        meta_text = "N.A.V.I" if is_navi else "ты" if not is_sys else "система"
        meta_color = (
            hex_color(C["text_dim"]) if not is_navi
            else hex_color(C["green"], 0.7)
        )

        meta = Label(
            text=meta_text,
            font_name="Roboto",
            font_size=sp(9),
            color=meta_color,
            size_hint_y=None,
            height=dp(16),
            halign="left" if is_navi or is_sys else "right",
            valign="middle",
        )
        meta.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))

        msg_color = (
            hex_color(C["navi_msg"]) if is_navi
            else hex_color(C["red"]) if is_sys
            else hex_color(C["user_msg"])
        )

        msg = Label(
            text=text,
            font_name="Roboto",
            font_size=sp(15),
            color=msg_color,
            size_hint_y=None,
            halign="left" if is_navi or is_sys else "right",
            valign="top",
            markup=False,
        )
        msg.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(4)),
        )

        self.add_widget(meta)
        self.add_widget(msg)

        def _upd_height(*a):
            self.height = meta.height + msg.height + self.spacing + dp(4)
        meta.bind(height=_upd_height)
        msg.bind(height=_upd_height)
        Clock.schedule_once(lambda *a: _upd_height(), 0.05)


class ChatScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.history = []
        self.is_loading = False
        self._nav_open = False
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")

        with root.canvas.before:
            Color(*hex_color(C["bg"]))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(self._bg,"pos",v),
                  size=lambda i,v: setattr(self._bg,"size",v))

        # ── HEADER ──
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(8),
        )
        with header.canvas.before:
            Color(*hex_color(C["bg"]))
            self._hdr_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(self._hdr_bg,"pos",v),
                    size=lambda i,v: setattr(self._hdr_bg,"size",v))

        menu_btn = Button(
            text="≡",
            font_size=sp(20),
            color=hex_color(C["text_mid"]),
            background_color=(0,0,0,0),
            background_normal="",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
        )
        menu_btn.bind(on_press=lambda *a: self._toggle_nav())

        logo = Label(
            text="N.A.V.I",
            font_name="Roboto",
            font_size=sp(16),
            bold=True,
            color=hex_color(C["text"]),
            size_hint_x=None, width=dp(70),
        )

        self.status_lbl = Label(
            text="● online",
            font_name="Roboto",
            font_size=sp(10),
            color=hex_color(C["green"]),
            size_hint_x=None, width=dp(80),
            halign="left",
        )
        self.status_lbl.bind(size=lambda i,v: setattr(i,"text_size",(v[0],None)))

        spacer = Widget()

        new_btn = Button(
            text="+",
            font_size=sp(20),
            color=hex_color(C["text_mid"]),
            background_color=(0,0,0,0),
            background_normal="",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
        )
        new_btn.bind(on_press=lambda *a: self._new_chat())

        header.add_widget(menu_btn)
        header.add_widget(logo)
        header.add_widget(self.status_lbl)
        header.add_widget(spacer)
        header.add_widget(new_btn)

        root.add_widget(header)
        root.add_widget(Divider())

        # ── MESSAGES ──
        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            bar_width=dp(2),
            bar_color=hex_color(C["border_light"]),
            scroll_type=["bars", "content"],
        )
        self.msg_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=[dp(16), dp(14), dp(16), dp(14)],
        )
        self.msg_list.bind(minimum_height=self.msg_list.setter("height"))
        self.scroll.add_widget(self.msg_list)
        root.add_widget(self.scroll)

        root.add_widget(Divider())

        # ── INPUT AREA ──
        input_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(60),
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(8),
        )
        with input_row.canvas.before:
            Color(*hex_color(C["bg"]))
            self._inp_bg = Rectangle(pos=input_row.pos, size=input_row.size)
        input_row.bind(pos=lambda i,v: setattr(self._inp_bg,"pos",v),
                       size=lambda i,v: setattr(self._inp_bg,"size",v))

        self.text_input = DarkInput(
            hint_text="Напиши сообщение...",
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
        )
        self.text_input.bind(on_text_validate=lambda *a: self._send())

        self.send_btn = Button(
            text="→",
            font_size=sp(20),
            bold=True,
            color=hex_color(C["bg"]),
            background_color=(0,0,0,0),
            background_normal="",
            size_hint=(None, None),
            size=(dp(44), dp(40)),
        )
        with self.send_btn.canvas.before:
            Color(*hex_color(C["accent"]))
            self._sbtn_bg = RoundedRectangle(
                pos=self.send_btn.pos,
                size=self.send_btn.size,
                radius=[dp(8)],
            )
        self.send_btn.bind(
            pos=lambda i,v: setattr(self._sbtn_bg,"pos",v),
            size=lambda i,v: setattr(self._sbtn_bg,"size",v),
        )
        self.send_btn.bind(on_press=lambda *a: self._send())

        input_row.add_widget(self.text_input)
        input_row.add_widget(self.send_btn)
        root.add_widget(input_row)

        self.add_widget(root)

        # ── NAV DRAWER (overlay) ──
        self._nav_drawer = self._build_nav_drawer()
        self.add_widget(self._nav_drawer)
        self._nav_drawer.opacity = 0
        self._nav_drawer.disabled = True

    def _build_nav_drawer(self):
        overlay = FloatLayout(size_hint=(1, 1))

        # Затемнение
        with overlay.canvas.before:
            Color(0, 0, 0, 0.5)
            self._overlay_bg = Rectangle(pos=overlay.pos, size=overlay.size)
        overlay.bind(pos=lambda i,v: setattr(self._overlay_bg,"pos",v),
                     size=lambda i,v: setattr(self._overlay_bg,"size",v))

        tap_catcher = Button(
            background_color=(0,0,0,0), background_normal="",
            size_hint=(1,1),
        )
        tap_catcher.bind(on_press=lambda *a: self._close_nav())
        overlay.add_widget(tap_catcher)

        # Панель
        panel = BoxLayout(
            orientation="vertical",
            size_hint=(0.78, 1),
            pos_hint={"x": 0, "y": 0},
            padding=[0, 0, 0, 0],
            spacing=0,
        )
        with panel.canvas.before:
            Color(*hex_color(C["surface"]))
            self._panel_bg = Rectangle(pos=panel.pos, size=panel.size)
        panel.bind(pos=lambda i,v: setattr(self._panel_bg,"pos",v),
                   size=lambda i,v: setattr(self._panel_bg,"size",v))

        # Шапка панели
        ph = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(54),
            padding=[dp(16), dp(10), dp(12), dp(10)],
        )
        ph.add_widget(Label(
            text="N.A.V.I",
            font_name="Roboto",
            font_size=sp(14), bold=True,
            color=hex_color(C["text"]),
        ))
        close_btn = Button(
            text="✕", font_size=sp(16),
            color=hex_color(C["text_dim"]),
            background_color=(0,0,0,0), background_normal="",
            size_hint=(None,None), size=(dp(32),dp(32)),
        )
        close_btn.bind(on_press=lambda *a: self._close_nav())
        ph.add_widget(close_btn)
        panel.add_widget(ph)
        panel.add_widget(Divider())

        # Кнопки навигации
        nav_items = [
            ("💬  Новый чат",    self._new_chat),
            ("🌤  Погода",       self._open_weather),
            ("📝  Заметки",      self._open_notes),
            ("⬡   Монитор",      self._open_monitor),
            ("↩  Выйти",        self._logout),
        ]
        for label, cb in nav_items:
            is_exit = "Выйти" in label
            btn = Button(
                text=label,
                font_name="Roboto",
                font_size=sp(13),
                color=hex_color(C["red"] if is_exit else C["text"]),
                background_color=(0,0,0,0), background_normal="",
                background_down="",
                size_hint_y=None, height=dp(50),
                halign="left",
                padding_x=dp(20),
            )
            btn.bind(size=lambda i,v: setattr(i,"text_size",(v[0],None)))
            btn.bind(on_press=lambda *a, f=cb: (self._close_nav(), f()))
            panel.add_widget(btn)
            panel.add_widget(Divider())

        panel.add_widget(Widget())  # spacer
        overlay.add_widget(panel)
        return overlay

    def _toggle_nav(self):
        if self._nav_open:
            self._close_nav()
        else:
            self._open_nav()

    def _open_nav(self):
        self._nav_open = True
        self._nav_drawer.opacity = 1
        self._nav_drawer.disabled = False

    def _close_nav(self):
        self._nav_open = False
        self._nav_drawer.opacity = 0
        self._nav_drawer.disabled = True

    def on_enter(self):
        if not self.history:
            self.add_message("navi", "N.A.V.I онлайн. С возвращением. Чем могу помочь?")

    def add_message(self, role, text):
        bubble = MessageBubble(role=role, text=text)
        self.msg_list.add_widget(bubble)
        Clock.schedule_once(lambda *a: self._scroll_bottom(), 0.1)

    def _scroll_bottom(self):
        self.scroll.scroll_y = 0

    def _new_chat(self):
        self.history = []
        self.msg_list.clear_widgets()
        self.add_message("navi", "Новый чат. Чем могу помочь?")

    def _send(self):
        if self.is_loading:
            return
        text = self.text_input.text.strip()
        if not text:
            return
        self.text_input.text = ""

        self.add_message("user", text)
        self.history.append({"role": "user", "content": text})
        self._start_loading()
        threading.Thread(target=self._get_response, daemon=True).start()

    def _start_loading(self):
        self.is_loading = True
        self.send_btn.text = "·"
        self.status_lbl.text = "● думает..."
        self.status_lbl.color = hex_color(C["text_mid"])

    def _get_response(self):
        app = App.get_running_app()
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history[-20:]
            resp = app.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            Clock.schedule_once(lambda *a: self._on_response(reply), 0)
        except Exception as e:
            Clock.schedule_once(lambda *a: self._on_error(str(e)), 0)

    def _on_response(self, reply):
        self.add_message("navi", reply)
        self.is_loading = False
        self.send_btn.text = "→"
        self.status_lbl.text = "● online"
        self.status_lbl.color = hex_color(C["green"])

    def _on_error(self, err):
        self.add_message("sys", f"Ошибка: {err}")
        self.is_loading = False
        self.send_btn.text = "→"
        self.status_lbl.text = "● online"
        self.status_lbl.color = hex_color(C["green"])

    # ── Переходы ──
    def _open_weather(self):
        self.manager.current = "weather"

    def _open_notes(self):
        self.manager.current = "notes"

    def _open_monitor(self):
        self.manager.current = "monitor"

    def _logout(self):
        app = App.get_running_app()
        app.api_key = ""
        app.client = None
        if os.path.exists(API_KEY_FILE):
            os.remove(API_KEY_FILE)
        self.history = []
        self.msg_list.clear_widgets()
        self.manager.current = "login"


# ══════════════════════════════════════════════════
#  ЭКРАН ПОГОДЫ
# ══════════════════════════════════════════════════

class WeatherScreen(Screen):
    WMO_CODES = {
        0: ("Ясно", "☀"),  1: ("Преим. ясно", "🌤"),
        2: ("Облачно", "⛅"), 3: ("Пасмурно", "☁"),
        45: ("Туман", "🌫"), 48: ("Изморозь", "🌫"),
        51: ("Морось", "🌦"), 53: ("Морось", "🌦"), 55: ("Морось", "🌦"),
        61: ("Дождь", "🌧"), 63: ("Дождь", "🌧"), 65: ("Ливень", "🌧"),
        71: ("Снег", "❄"),  73: ("Снег", "❄"),  75: ("Снегопад", "❄"),
        80: ("Ливень", "⛈"), 95: ("Гроза", "⛈"), 99: ("Гроза", "⛈"),
    }
    DAYS_RU = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]

    def __init__(self, **kw):
        super().__init__(**kw)
        self._city = "Кишинёв"
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*hex_color(C["bg"]))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(self._bg,"pos",v),
                  size=lambda i,v: setattr(self._bg,"size",v))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(54),
                        padding=[dp(12),dp(8),dp(12),dp(8)], spacing=dp(8))
        back = Button(text="←", font_size=sp(20),
                      color=hex_color(C["text_mid"]),
                      background_color=(0,0,0,0), background_normal="",
                      size_hint=(None,None), size=(dp(36),dp(36)))
        back.bind(on_press=lambda *a: setattr(self.manager,"current","chat"))
        self.city_lbl = Label(text="Погода", font_name="Roboto",
                              font_size=sp(14), bold=True, color=hex_color(C["text"]))
        refresh_btn = Button(text="↻", font_size=sp(18),
                             color=hex_color(C["text_mid"]),
                             background_color=(0,0,0,0), background_normal="",
                             size_hint=(None,None), size=(dp(36),dp(36)))
        refresh_btn.bind(on_press=lambda *a: self._fetch())
        hdr.add_widget(back)
        hdr.add_widget(self.city_lbl)
        hdr.add_widget(Widget())
        hdr.add_widget(refresh_btn)
        root.add_widget(hdr)
        root.add_widget(Divider())

        # Search
        search_row = BoxLayout(size_hint_y=None, height=dp(52),
                               padding=[dp(12),dp(8),dp(12),dp(8)], spacing=dp(8))
        self.city_input = DarkInput(hint_text="Город...", size_hint=(1,None), height=dp(38))
        self.city_input.text = self._city
        go_btn = Button(text="→", font_size=sp(18), bold=True,
                        color=hex_color(C["bg"]),
                        background_color=(0,0,0,0), background_normal="",
                        size_hint=(None,None), size=(dp(40),dp(38)))
        with go_btn.canvas.before:
            Color(*hex_color(C["accent"]))
            self._gbtn = RoundedRectangle(pos=go_btn.pos, size=go_btn.size, radius=[dp(8)])
        go_btn.bind(pos=lambda i,v: setattr(self._gbtn,"pos",v),
                    size=lambda i,v: setattr(self._gbtn,"size",v))
        go_btn.bind(on_press=lambda *a: self._search())
        self.city_input.bind(on_text_validate=lambda *a: self._search())
        search_row.add_widget(self.city_input)
        search_row.add_widget(go_btn)
        root.add_widget(search_row)
        root.add_widget(Divider())

        # Main temp card
        temp_card = BoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(100),
                              padding=[dp(24),dp(16),dp(24),dp(16)])
        self.temp_lbl = Label(text="—°", font_name="Roboto",
                              font_size=sp(52), bold=True, color=hex_color(C["text"]),
                              size_hint=(None,1), width=dp(140))
        desc_col = BoxLayout(orientation="vertical")
        self.desc_lbl = Label(text="", font_size=sp(15), color=hex_color(C["text"]),
                              halign="left", size_hint_y=None, height=dp(28))
        self.desc_lbl.bind(size=lambda i,v: setattr(i,"text_size",(v[0],None)))
        self.icon_lbl = Label(text="", font_size=sp(28), size_hint_y=None, height=dp(36))
        desc_col.add_widget(self.icon_lbl)
        desc_col.add_widget(self.desc_lbl)
        temp_card.add_widget(self.temp_lbl)
        temp_card.add_widget(desc_col)
        root.add_widget(temp_card)

        # Details row
        det_row = BoxLayout(size_hint_y=None, height=dp(64),
                            padding=[dp(16),dp(8),dp(16),dp(8)])
        for attr, label in [("det_hum","Влажность"),("det_feels","Ощущается"),("det_wind","Ветер")]:
            col = BoxLayout(orientation="vertical")
            val = Label(text="—", font_name="Roboto",
                        font_size=sp(16), bold=True, color=hex_color(C["text"]))
            lbl = Label(text=label, font_size=sp(9), color=hex_color(C["text_dim"]))
            col.add_widget(val)
            col.add_widget(lbl)
            setattr(self, attr, val)
            det_row.add_widget(col)
        root.add_widget(det_row)
        root.add_widget(Divider())

        # 7-day forecast
        scroll = ScrollView(do_scroll_x=False, size_hint=(1,1))
        self.day_list = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=dp(2),
                                  padding=[dp(12),dp(8),dp(12),dp(8)])
        self.day_list.bind(minimum_height=self.day_list.setter("height"))
        scroll.add_widget(self.day_list)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_enter(self):
        self._fetch()

    def _search(self):
        city = self.city_input.text.strip()
        if city:
            self._city = city
            self._fetch()

    def _fetch(self):
        self.city_lbl.text = "Загрузка..."
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        import urllib.request, json as _json
        try:
            geo_url = (
                "https://geocoding-api.open-meteo.com/v1/search"
                f"?name={urllib.request.quote(self._city)}&count=1&language=ru&format=json"
            )
            with urllib.request.urlopen(geo_url, timeout=8) as r:
                geo = _json.loads(r.read())
            res = geo.get("results", [{}])[0]
            lat, lon = res.get("latitude", 47), res.get("longitude", 28)
            city_name = res.get("name", self._city)

            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
                f"&daily=weather_code,temperature_2m_max,temperature_2m_min"
                f"&timezone=auto&forecast_days=7"
            )
            with urllib.request.urlopen(url, timeout=10) as r:
                data = _json.loads(r.read())
            Clock.schedule_once(lambda *a: self._apply(data, city_name), 0)
        except Exception as e:
            Clock.schedule_once(
                lambda *a: setattr(self.city_lbl, "text", f"Ошибка: {str(e)[:30]}"), 0)

    def _apply(self, data, city_name):
        cur = data["current"]
        code = int(cur.get("weather_code", 0))
        temp = round(cur.get("temperature_2m", 0))
        feels = round(cur.get("apparent_temperature", 0))
        hum = cur.get("relative_humidity_2m", 0)
        wind = round(cur.get("wind_speed_10m", 0))
        desc, icon = self.WMO_CODES.get(code, ("Неизвестно", "?"))

        self.city_lbl.text = city_name
        self.temp_lbl.text = f"{temp}°"
        self.desc_lbl.text = desc
        self.icon_lbl.text = icon
        self.det_hum.text = f"{hum}%"
        self.det_feels.text = f"{feels}°"
        self.det_wind.text = f"{wind} км/ч"

        self.day_list.clear_widgets()
        ddates = data["daily"]["time"]
        dcodes = data["daily"]["weather_code"]
        dmax = data["daily"]["temperature_2m_max"]
        dmin = data["daily"]["temperature_2m_min"]

        for i in range(min(7, len(ddates))):
            d = datetime.strptime(ddates[i], "%Y-%m-%d")
            day_name = "Сегодня" if i == 0 else self.DAYS_RU[d.weekday()]
            dc = int(dcodes[i])
            dd_desc, dd_icon = self.WMO_CODES.get(dc, ("—", ""))

            row = BoxLayout(size_hint_y=None, height=dp(48),
                            padding=[dp(8),0,dp(8),0])
            with row.canvas.before:
                Color(*hex_color(C["surface"]))
                rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])
            row.bind(pos=lambda i,v,r=rect: setattr(r,"pos",v),
                     size=lambda i,v,r=rect: setattr(r,"size",v))

            row.add_widget(Label(text=day_name, font_name="Roboto",
                                 font_size=sp(12), bold=True, color=hex_color(C["text"]),
                                 size_hint=(None,1), width=dp(80), halign="left"))
            row.add_widget(Label(text=f"{dd_icon}  {dd_desc}", font_size=sp(12),
                                 color=hex_color(C["text_mid"]), halign="left"))
            row.add_widget(Label(text=f"{round(dmin[i])}°",
                                 font_size=sp(13), color=hex_color(C["text_dim"]),
                                 size_hint=(None,1), width=dp(40)))
            row.add_widget(Label(text=f"{round(dmax[i])}°",
                                 font_name="Roboto",
                                 font_size=sp(13), bold=True, color=hex_color(C["text"]),
                                 size_hint=(None,1), width=dp(40)))
            self.day_list.add_widget(row)
            self.day_list.add_widget(Widget(size_hint_y=None, height=dp(4)))


# ══════════════════════════════════════════════════
#  ЭКРАН ЗАМЕТОК
# ══════════════════════════════════════════════════

class NotesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*hex_color(C["bg"]))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(self._bg,"pos",v),
                  size=lambda i,v: setattr(self._bg,"size",v))

        hdr = BoxLayout(size_hint_y=None, height=dp(54),
                        padding=[dp(12),dp(8),dp(12),dp(8)], spacing=dp(8))
        back = Button(text="←", font_size=sp(20), color=hex_color(C["text_mid"]),
                      background_color=(0,0,0,0), background_normal="",
                      size_hint=(None,None), size=(dp(36),dp(36)))
        back.bind(on_press=lambda *a: setattr(self.manager,"current","chat"))
        hdr.add_widget(back)
        hdr.add_widget(Label(text="ЗАМЕТКИ", font_name="Roboto",
                             font_size=sp(14), bold=True, color=hex_color(C["text"])))
        root.add_widget(hdr)
        root.add_widget(Divider())

        scroll = ScrollView(do_scroll_x=False, size_hint=(1,1))
        self.note_list = BoxLayout(orientation="vertical", size_hint_y=None,
                                   spacing=dp(8), padding=[dp(12),dp(12),dp(12),dp(12)])
        self.note_list.bind(minimum_height=self.note_list.setter("height"))
        scroll.add_widget(self.note_list)
        root.add_widget(scroll)

        root.add_widget(Divider())
        inp_row = BoxLayout(size_hint_y=None, height=dp(60),
                            padding=[dp(12),dp(10),dp(12),dp(10)], spacing=dp(8))
        self.note_input = DarkInput(hint_text="Быстрая заметка...",
                                    size_hint=(1,None), height=dp(40))
        add_btn = Button(text="→", font_size=sp(20), bold=True,
                         color=hex_color(C["bg"]),
                         background_color=(0,0,0,0), background_normal="",
                         size_hint=(None,None), size=(dp(44),dp(40)))
        with add_btn.canvas.before:
            Color(*hex_color(C["accent"]))
            self._abtn = RoundedRectangle(pos=add_btn.pos, size=add_btn.size, radius=[dp(8)])
        add_btn.bind(pos=lambda i,v: setattr(self._abtn,"pos",v),
                     size=lambda i,v: setattr(self._abtn,"size",v))
        add_btn.bind(on_press=lambda *a: self._add_note())
        self.note_input.bind(on_text_validate=lambda *a: self._add_note())
        inp_row.add_widget(self.note_input)
        inp_row.add_widget(add_btn)
        root.add_widget(inp_row)
        self.add_widget(root)

    def on_enter(self):
        self._refresh()

    def _refresh(self):
        self.note_list.clear_widgets()
        notes = self._load_notes()
        if not notes:
            self.note_list.add_widget(
                Label(text="Нет заметок", font_name="Roboto",
                      font_size=sp(12), color=hex_color(C["text_dim"]),
                      size_hint_y=None, height=dp(60)))
            return
        for i, note in enumerate(notes):
            card = BoxLayout(orientation="vertical", size_hint_y=None,
                             padding=[dp(12),dp(10),dp(12),dp(10)])
            with card.canvas.before:
                Color(*hex_color(C["surface"]))
                rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
            card.bind(pos=lambda inst,v,r=rect: setattr(r,"pos",v),
                      size=lambda inst,v,r=rect: setattr(r,"size",v))

            date_lbl = Label(text=note.get("date",""), font_name="Roboto",
                             font_size=sp(9), color=hex_color(C["text_dim"]),
                             size_hint_y=None, height=dp(16), halign="left")
            date_lbl.bind(size=lambda i,v: setattr(i,"text_size",(v[0],None)))

            txt_lbl = Label(text=note["text"], font_size=sp(14),
                            color=hex_color(C["text"]),
                            size_hint_y=None, halign="left", valign="top")
            txt_lbl.bind(
                width=lambda i,v: setattr(i,"text_size",(v,None)),
                texture_size=lambda i,v: setattr(i,"height",v[1]+dp(4)),
            )

            del_btn = Button(text="✕", font_size=sp(11), color=hex_color(C["text_dim"]),
                             background_color=(0,0,0,0), background_normal="",
                             size_hint=(None,None), size=(dp(28),dp(24)))
            del_btn.bind(on_press=lambda *a, idx=i: self._delete(idx))

            card.add_widget(date_lbl)
            card.add_widget(txt_lbl)
            card.add_widget(del_btn)

            def _upd_card(inst, val, c=card, d=date_lbl, t=txt_lbl):
                c.height = d.height + t.height + dp(48)
            date_lbl.bind(height=_upd_card)
            txt_lbl.bind(height=_upd_card)
            Clock.schedule_once(lambda *a, c=card, d=date_lbl, t=txt_lbl:
                                setattr(c,"height", d.height + t.height + dp(48)), 0.05)

            self.note_list.add_widget(card)

    def _add_note(self):
        text = self.note_input.text.strip()
        if not text:
            return
        self.note_input.text = ""
        notes = self._load_notes()
        notes.insert(0, {"text": text, "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
        self._save_notes(notes)
        self._refresh()

    def _delete(self, idx):
        notes = self._load_notes()
        if 0 <= idx < len(notes):
            notes.pop(idx)
            self._save_notes(notes)
        self._refresh()

    def _load_notes(self):
        try:
            with open(NOTES_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save_notes(self, notes):
        try:
            with open(NOTES_FILE,"w",encoding="utf-8") as f:
                json.dump(notes[:100], f, ensure_ascii=False, indent=2)
        except:
            pass


# ══════════════════════════════════════════════════
#  ЭКРАН МОНИТОРА
# ══════════════════════════════════════════════════

class MonitorScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._running = False
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*hex_color(C["bg"]))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i,v: setattr(self._bg,"pos",v),
                  size=lambda i,v: setattr(self._bg,"size",v))

        hdr = BoxLayout(size_hint_y=None, height=dp(54),
                        padding=[dp(12),dp(8),dp(12),dp(8)], spacing=dp(8))
        back = Button(text="←", font_size=sp(20), color=hex_color(C["text_mid"]),
                      background_color=(0,0,0,0), background_normal="",
                      size_hint=(None,None), size=(dp(36),dp(36)))
        back.bind(on_press=lambda *a: setattr(self.manager,"current","chat"))
        hdr.add_widget(back)
        hdr.add_widget(Label(text="МОНИТОР", font_name="Roboto",
                             font_size=sp(14), bold=True, color=hex_color(C["text"])))
        self.uptime_lbl = Label(text="", font_name="Roboto",
                                font_size=sp(9), color=hex_color(C["text_dim"]))
        hdr.add_widget(Widget())
        hdr.add_widget(self.uptime_lbl)
        root.add_widget(hdr)
        root.add_widget(Divider())

        scroll = ScrollView(do_scroll_x=False)
        self.stat_list = BoxLayout(orientation="vertical", size_hint_y=None,
                                   spacing=dp(8), padding=[dp(12),dp(12),dp(12),dp(12)])
        self.stat_list.bind(minimum_height=self.stat_list.setter("height"))
        scroll.add_widget(self.stat_list)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self._running = True
        self._update()

    def on_leave(self):
        self._running = False

    def _update(self):
        if not self._running:
            return
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            data = {
                "cpu": cpu,
                "ram_pct": ram.percent,
                "ram_used": round(ram.used/(1024**3), 1),
                "ram_total": round(ram.total/(1024**3), 1),
            }
            try:
                dc = psutil.disk_usage("/")
                data["disk_c_pct"] = dc.percent
                data["disk_c_used"] = round(dc.used/(1024**3), 1)
                data["disk_c_total"] = round(dc.total/(1024**3), 1)
            except:
                pass
            try:
                net = psutil.net_io_counters()
                data["net_sent"] = round(net.bytes_sent/(1024**2), 1)
                data["net_recv"] = round(net.bytes_recv/(1024**2), 1)
            except:
                pass
            try:
                ut = int(datetime.now().timestamp() - psutil.boot_time())
                h, r = divmod(ut, 3600)
                m2, _ = divmod(r, 60)
                data["uptime"] = f"{h}h {m2}m"
            except:
                data["uptime"] = ""
            Clock.schedule_once(lambda *a: self._apply(data), 0)
        except Exception as e:
            Clock.schedule_once(lambda *a: None, 0)

        if self._running:
            Clock.schedule_once(lambda *a: self._update(), 2)

    def _apply(self, data):
        self.uptime_lbl.text = data.get("uptime", "")
        self.stat_list.clear_widgets()

        items = [
            ("CPU", f"{data['cpu']}%", data['cpu']/100),
            ("RAM", f"{data.get('ram_used','?')} / {data.get('ram_total','?')} GB  ({data['ram_pct']}%)", data['ram_pct']/100),
        ]
        if "disk_c_pct" in data:
            items.append(("Диск", f"{data['disk_c_used']} / {data['disk_c_total']} GB  ({data['disk_c_pct']}%)", data['disk_c_pct']/100))
        if "net_sent" in data:
            items.append(("Сеть ↑", f"{data['net_sent']} MB всего", 0))
            items.append(("Сеть ↓", f"{data['net_recv']} MB всего", 0))

        for label, value, pct in items:
            card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80),
                             padding=[dp(14),dp(10),dp(14),dp(10)], spacing=dp(6))
            with card.canvas.before:
                Color(*hex_color(C["surface"]))
                rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
            card.bind(pos=lambda i,v,r=rect: setattr(r,"pos",v),
                      size=lambda i,v,r=rect: setattr(r,"size",v))

            row = BoxLayout(size_hint_y=None, height=dp(22))
            row.add_widget(Label(text=label, font_name="Roboto",
                                 font_size=sp(10), color=hex_color(C["text_dim"]),
                                 halign="left", size_hint=(None,1), width=dp(60)))
            row.add_widget(Label(text=value, font_size=sp(13), color=hex_color(C["text"]),
                                 halign="left"))
            card.add_widget(row)

            # Progress bar
            if pct > 0:
                bar_bg = Widget(size_hint_y=None, height=dp(6))
                with bar_bg.canvas:
                    Color(*hex_color(C["border_light"]))
                    bg_rect = RoundedRectangle(pos=bar_bg.pos, size=bar_bg.size, radius=[dp(3)])

                    bar_color = (
                        hex_color(C["green"]) if pct < 0.6
                        else hex_color("#ccaa22") if pct < 0.8
                        else hex_color(C["red"])
                    )
                    Color(*bar_color)
                    fill_rect = RoundedRectangle(
                        pos=bar_bg.pos,
                        size=(bar_bg.width * pct, bar_bg.height),
                        radius=[dp(3)]
                    )

                def _upd_bar(inst, val, bg=bg_rect, fill=fill_rect, p=pct):
                    bg.pos = inst.pos
                    bg.size = inst.size
                    fill.pos = inst.pos
                    fill.size = (inst.width * p, inst.height)

                bar_bg.bind(pos=_upd_bar, size=_upd_bar)
                card.add_widget(bar_bg)

            self.stat_list.add_widget(card)


# ══════════════════════════════════════════════════
#  ПРИЛОЖЕНИЕ
# ══════════════════════════════════════════════════

class NaviMobileApp(App):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.api_key = ""
        self.client = None
        self.title = "N.A.V.I"

    def build(self):
        Window.clearcolor = hex_color(C["bg"])

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ChatScreen(name="chat"))
        sm.add_widget(WeatherScreen(name="weather"))
        sm.add_widget(NotesScreen(name="notes"))
        sm.add_widget(MonitorScreen(name="monitor"))

        # Автологин
        if os.path.exists(API_KEY_FILE):
            try:
                with open(API_KEY_FILE) as f:
                    key = f.read().strip()
                if key.startswith("gsk_") and len(key) >= 40:
                    self.api_key = key
                    self.init_client()
                    sm.current = "chat"
                    return sm
            except:
                pass

        sm.current = "login"
        return sm

    def init_client(self):
        from groq import Groq
        self.client = Groq(api_key=self.api_key)


if __name__ == "__main__":
    NaviMobileApp().run()
