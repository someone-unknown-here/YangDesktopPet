import random
import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QPoint, QSize, QMimeData
from PySide6.QtGui import QAction, QMovie, QPixmap, QColor, QPainter, QIcon, QTransform, QDrag
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QApplication,
    QDialog,
    QHBoxLayout,
    QSlider,
    QPushButton,
    QGridLayout,
)

from .asset_manager import scan_states
from .config_manager import load_config, save_config
from .dialogue_manager import load_dialogues
from .models import RuntimeState
from .speech_bubble import SpeechBubble
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SizeDialog(QDialog):
    def __init__(self, current_size, min_size, max_size, on_change, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调整桌宠大小")
        self.setFixedSize(340, 120)
        self.on_change = on_change

        self.setWindowIcon(QIcon(resource_path("assets/yangyangtouxiang.png")))

        layout = QVBoxLayout(self)

        self.label = QLabel(f"当前大小: {current_size}")
        layout.addWidget(self.label)

        row = QHBoxLayout()
        layout.addLayout(row)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_size)
        self.slider.setMaximum(max_size)
        self.slider.setValue(current_size)
        self.slider.valueChanged.connect(self.handle_value_change)
        row.addWidget(self.slider)

        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.hide)
        layout.addWidget(self.close_button)

    def handle_value_change(self, value):
        self.label.setText(f"当前大小: {value}")
        self.on_change(value)

    def update_value(self, value, min_size=None, max_size=None):
        if min_size is not None:
            self.slider.setMinimum(min_size)
        if max_size is not None:
            self.slider.setMaximum(max_size)

        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.label.setText(f"当前大小: {value}")

class TalkDialog(QDialog):
    def __init__(self, on_speak, parent=None):
        super().__init__(parent)
        self.setWindowTitle("话痨模式")
        self.setFixedSize(220, 140)
        self.on_speak = on_speak

        self.setWindowIcon(QIcon(resource_path("assets/yangyangtouxiang.png")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.speak_button = QPushButton("说话！")
        self.speak_button.clicked.connect(self.on_speak)
        self.speak_button.setCursor(Qt.PointingHandCursor)

        layout.addWidget(self.speak_button)

        self.setStyleSheet("""
            QDialog {
                background-color: rgba(30, 30, 34, 235);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 14px;
            }

            QPushButton {
                background-color: rgba(255, 255, 255, 18);
                color: white;
                border: 1px solid rgba(255, 255, 255, 45);
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
                font-family: "Microsoft YaHei";
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 32);
                border: 1px solid rgba(255, 255, 255, 80);
            }

            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 50);
            }
        """)

class RewardDialog(QDialog):
    def __init__(self, on_reward, parent=None):
        super().__init__(parent)
        self.setWindowTitle("祝福")
        self.setFixedSize(220, 180)
        self.on_reward = on_reward

        self.setWindowIcon(QIcon(resource_path("assets/yangyangtouxiang.png")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.reward_button = QPushButton("")
        self.reward_button.setFixedSize(110, 110)
        self.reward_button.setIcon(QIcon(resource_path("assets/reward_button.png")))
        self.reward_button.setIconSize(QSize(110, 110))
        self.reward_button.setCursor(Qt.PointingHandCursor)
        self.reward_button.clicked.connect(self.on_reward)
        self.reward_button.setObjectName("rewardButton")

        layout.addWidget(self.reward_button, alignment=Qt.AlignCenter)

        self.reward_button.setStyleSheet("""
            QPushButton#rewardButton {
                border: none;
                background: transparent;
            }
            QPushButton#rewardButton:hover {
                background: transparent;
            }
            QPushButton#rewardButton:pressed {
                padding-top: 4px;
                padding-left: 3px;
            }
        """)

class FoodBarDialog(QDialog):
    def __init__(self, on_close_bar, parent=None):
        super().__init__(parent)
        self.on_close_bar = on_close_bar

    def closeEvent(self, event):
        if self.on_close_bar is not None:
            self.on_close_bar()
        super().closeEvent(event)

class FoodDragLabel(QLabel):
    def __init__(self, food_type: str, icon_path: str | None = None, text_fallback: str = "", parent=None):
        super().__init__(parent)
        self.food_type = food_type
        self.icon_path = icon_path
        self.drag_start_pos = None

        self.setFixedSize(64, 64)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)

        pix = QPixmap(icon_path) if icon_path else QPixmap()
        if not pix.isNull():
            self.setPixmap(
                pix.scaled(
                    52,
                    52,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.setText(text_fallback or food_type)
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 18);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 45);
                    border-radius: 12px;
                    font-size: 20px;
                    font-family: "Microsoft YaHei";
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return

        if self.drag_start_pos is None:
            return

        if (event.pos() - self.drag_start_pos).manhattanLength() < 8:
            return

        mime = QMimeData()
        mime.setData("application/x-desktop-pet-food", self.food_type.encode("utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime)

        if self.pixmap() is not None and not self.pixmap().isNull():
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(self.rect().center())

        self.setCursor(Qt.OpenHandCursor)
        drag.exec(Qt.CopyAction)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)


class DesktopPetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.dialogues = load_dialogues()
        self.state_assets = scan_states()

        self.last_spoken_text = None

        self.runtime = RuntimeState(
            current_state=self.config["behavior"].get("state", "normal"),
            current_action=self.config["behavior"].get("fixed_action", ""),
            manual_override=self.config["behavior"].get("manual_override", False),
            action_locked=self.config["behavior"].get("locked_action", False),
        )

        self.current_width = int(self.config["window"].get("default_width", 260))
        self.min_width = int(self.config["window"].get("min_width", 120))
        self.max_width = int(self.config["window"].get("max_width", 500))

        self.mirrored = False
        self.movie = None
        self.movie_mode = "movie"
        self.frame_changed_connected = False

        self.single_play_mode = False
        self.movie_finished_callback = None
        self.movie_finish_pending = False
        self.last_movie_frame_seen = -1

        self.feeding_mode = False
        self.feeding_phase = None
        self.food_dialog = None
        self.pre_feeding_state = None
        self.pre_feeding_action = None
        self.pre_feeding_manual_override = False

        self.food_definitions = [
            {
                "type": "cake",
                "icon": "assets/food_cake.png",
                "fallback": "🍰",
                "label": "Cake",
            },
            {
                "type": "beer",
                "icon": "assets/food_beer.png",
                "fallback": "🍺",
                "label": "Beer",
            },
            {
                "type": "tea",
                "icon": "assets/food_tea.png",
                "fallback": "🍵",
                "label": "Tea",
            },
            {
                "type": "fruit",
                "icon": "assets/food_fruit.png",
                "fallback": "🍎",
                "label": "Fruit",
            },
            {
                "type": "chips",
                "icon": "assets/food_chips.png",
                "fallback": "🍟",
                "label": "Chips",
            },
            {
                "type": "fried_chicken",
                "icon": "assets/food_friedchicken.png",
                "fallback": "🍗",
                "label": "Fried Chicken",
            }
        ]

        flags = Qt.FramelessWindowHint | Qt.Tool | Qt.NoDropShadowWindowHint
        if self.config["window"].get("always_on_top", True):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        central = QWidget()
        central.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pet_label = QLabel()
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.setAttribute(Qt.WA_TranslucentBackground, True)
        layout.addWidget(self.pet_label)

        self.speech = SpeechBubble()
        self.speech.set_outgoing_green_style()

        self.size_dialog = None
        self.talk_dialog = None
        self.reward_dialog = None

        self.build_tray_icon()

        self.resize(self.current_width, self.current_width)

        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 20
        y = screen.bottom() - self.height() - 20
        self.move(x, y)

        self.drag_offset = None
        self.mouse_press_global = None
        self.mouse_press_time = 0.0
        self.mouse_dragging = False

        self.minute_timer = QTimer(self)
        self.minute_timer.timeout.connect(self.tick)
        self.minute_timer.start(60_000)

        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.change_action_if_needed)
        self.action_timer.start(
            max(1, int(self.config["timing"].get("action_change_minutes", 5))) * 60_000
        )

        self.speech_timer = QTimer(self)
        self.speech_timer.timeout.connect(self.random_speak)
        self.speech_timer.start(
            max(1, int(self.config["timing"].get("random_speech_minutes", 4))) * 60_000
        )

        self.special_restore_timer = QTimer(self)
        self.special_restore_timer.setSingleShot(True)
        self.special_restore_timer.timeout.connect(self.restore_after_special)

        self.state_name_map = {
            "normal": "正常",
            "sleeping": "睡觉",
            "eating": "吃饭",
            "annoyed": "生气",
            "reward": "开心",
            "working": "工作/学习",
            "feeding": "喂食",
            "png_tuber": "PNG Tuber",
            "trash_tuber": "Trash Tuber"
        }

        self.ensure_valid_state()
        self.apply_schedule_rules(force=True)
        self.tick()

    def build_tray_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QColor(140, 185, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()

        self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self)
        tray_menu = QMenu()

        show_action = QAction("显示桌宠", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def quit_application(self):
        self.persist_behavior()
        # self.config["window"]["start_x"] = self.x()
        # self.config["window"]["start_y"] = self.y()
        save_config(self.config)
        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()
        QApplication.quit()

    def create_or_show_reward_dialog(self):
        if self.reward_dialog is None:
            self.reward_dialog = RewardDialog(
                on_reward=self.trigger_reward_reaction,
                parent=self,
            )

        dialog_x = self.x() + self.width() - 55
        dialog_y = self.y() + 260
        self.place_dialog_near_pet(
            self.reward_dialog,
            self.width() - 55,
            260,
        )
        self.reward_dialog.show()
        self.reward_dialog.raise_()
        self.reward_dialog.activateWindow()

    def trigger_reward_reaction(self):
        self.trigger_temporary_state("reward", speech_key="reward", duration_ms=4000)

    def ensure_valid_state(self):
        if not self.state_assets:
            self.pet_label.setText("请先在 states 文件夹里放入 GIF")
            self.pet_label.setStyleSheet(
                "color: white; background: rgba(0,0,0,140); border-radius: 14px; padding: 12px;"
            )
            self.pet_label.adjustSize()
            return

        if self.runtime.current_state not in self.state_assets:
            self.runtime.current_state = "normal" if "normal" in self.state_assets else next(iter(self.state_assets))

        if self.runtime.current_action not in self.state_assets.get(self.runtime.current_state, {}):
            self.runtime.current_action = self.pick_random_action(self.runtime.current_state) or ""

    def get_actions_for_state(self, state_name: str):
        return self.state_assets.get(state_name, {})

    def pick_random_action(self, state_name: str):
        actions = list(self.get_actions_for_state(state_name).keys())
        return random.choice(actions) if actions else None

    def pick_random_variant_index(self, state_name: str, action_name: str):
        variants = self.get_actions_for_state(state_name).get(action_name, [])
        if not variants:
            return 0
        return random.randrange(len(variants))

    def get_current_variants(self):
        return self.get_actions_for_state(self.runtime.current_state).get(self.runtime.current_action, [])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.mouse_press_global = event.globalPosition().toPoint()
            self.mouse_press_time = time.time()
            self.mouse_dragging = False

        elif event.button() == Qt.RightButton:
            self.open_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_offset is not None:
            current_global = event.globalPosition().toPoint()
            if self.mouse_press_global is not None:
                move_dist = (current_global - self.mouse_press_global).manhattanLength()
                if move_dist > 8:
                    self.mouse_dragging = True
            if self.mouse_dragging:
                self.move(current_global - self.drag_offset)
                self.update_bubble_position()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_bubble_position()

        # # These functions are for dialogs that should follow the pet when it moves. If you want to add more dialogs that also follow the pet, add similar code here.
        # # Deleting these right now.
        # if self.size_dialog is not None and self.size_dialog.isVisible():
        #     self.place_dialog_near_pet(
        #         self.size_dialog,
        #         self.width() - 55,
        #         20,
        #     )

        # if self.talk_dialog is not None and self.talk_dialog.isVisible():
        #     self.place_dialog_near_pet(
        #         self.talk_dialog,
        #         self.width() - 55,
        #         150,
        #     )

        # if self.reward_dialog is not None and self.reward_dialog.isVisible():
        #     self.place_dialog_near_pet(
        #         self.reward_dialog,
        #         self.width() - 55,
        #         260,
        #     )

        # if self.food_dialog is not None and self.food_dialog.isVisible():
        #     self.position_food_dialog()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.mouse_press_global = None
        self.mouse_press_time = 0.0
        self.mouse_dragging = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.feeding_mode:
                self.change_action_manual()
                self.register_click_for_annoyed()

    def create_or_show_size_dialog(self):
        if self.size_dialog is None:
            self.size_dialog = SizeDialog(
                current_size=self.current_width,
                min_size=self.min_width,
                max_size=self.max_width,
                on_change=self.apply_square_resize,
                parent=self,
            )
        else:
            self.size_dialog.update_value(
                self.current_width,
                min_size=self.min_width,
                max_size=self.max_width,
            )

        self.place_dialog_near_pet(
            self.size_dialog,
            self.width() - 55,
            20,
        )
        self.size_dialog.show()
        self.size_dialog.raise_()
        self.size_dialog.activateWindow()

    def create_or_show_talk_dialog(self):
        if self.talk_dialog is None:
            self.talk_dialog = TalkDialog(
                on_speak=self.speak_now,
                parent=self,
            )

        self.place_dialog_near_pet(
            self.talk_dialog,
            self.width() - 55,
            150,
        )
        self.talk_dialog.show()
        self.talk_dialog.raise_()
        self.talk_dialog.activateWindow()

    def handle_food_dialog_closed(self):
        if self.feeding_mode:
            self.exit_feeding_mode()

    def create_or_show_food_dialog(self):
        if self.food_dialog is None:
            self.food_dialog = FoodBarDialog(
                on_close_bar=self.handle_food_dialog_closed,
                parent=self,
            )
            self.food_dialog.setWindowTitle("喂食栏")
            self.food_dialog.setFixedSize(250, 180)
            self.food_dialog.setWindowIcon(QIcon(resource_path("assets/yangyangtouxiang.png")))

            layout = QGridLayout(self.food_dialog)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setHorizontalSpacing(10)
            layout.setVerticalSpacing(10)

            for i, item in enumerate(self.food_definitions):
                label = FoodDragLabel(
                    food_type=item["type"],
                    icon_path=resource_path(item["icon"]),
                    text_fallback=item["fallback"],
                    parent=self.food_dialog,
                )
                row = i // 3
                col = i % 3
                layout.addWidget(label, row, col)

            self.food_dialog.setStyleSheet("""
                QDialog {
                    background-color: rgba(30, 30, 34, 235);
                    border: 1px solid rgba(255, 255, 255, 30);
                    border-radius: 14px;
                }
            """)

        self.position_food_dialog()
        self.food_dialog.show()
        self.food_dialog.raise_()
        self.food_dialog.activateWindow()

    def position_food_dialog(self):
        if self.food_dialog is None:
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            self.food_dialog.move(self.pos() + QPoint(50, 50))
            return

        geo = screen.availableGeometry()

        x = self.x() + self.width() - 55
        y = self.y() + self.height() + 10

        dialog_w = self.food_dialog.width()
        dialog_h = self.food_dialog.height()

        x = max(geo.left() + 10, min(x, geo.right() - dialog_w - 10))
        y = max(geo.top() + 10, min(y, geo.bottom() - dialog_h - 10))

        self.food_dialog.move(x, y)

    def choose_dialogue(self, pool):
        if not pool:
            return None

        if len(pool) == 1:
            chosen = pool[0]
        else:
            candidates = [text for text in pool if text != self.last_spoken_text]
            chosen = random.choice(candidates if candidates else pool)

        self.last_spoken_text = chosen
        return chosen

    def open_context_menu(self, pos: QPoint):
        menu = QMenu(self)

        state_menu = menu.addMenu("切换状态")
        state_order = ["normal", "working", "eating", "sleeping", "png_tuber", "trash_tuber", "feeding", "annoyed", "reward"]
        for state_name in state_order:
            display_name = self.state_name_map.get(state_name, state_name)
            action = QAction(display_name, self)
            action.triggered.connect(lambda checked=False, s=state_name: self.set_state(s, manual=True))
            state_menu.addAction(action)

        # special_menu = menu.addMenu("特殊反应")

        # head_action = QAction("头部特殊反应", self)
        # head_action.triggered.connect(self.trigger_head_special)
        # special_menu.addAction(head_action)

        # body_action = QAction("身体特殊反应", self)
        # body_action.triggered.connect(self.trigger_body_special)
        # special_menu.addAction(body_action)

        flip_action = QAction("镜像翻转", self)
        flip_action.triggered.connect(self.toggle_mirror)
        menu.addAction(flip_action)

        size_action = QAction("调整大小", self)
        size_action.triggered.connect(self.create_or_show_size_dialog)
        menu.addAction(size_action)

        feeding_action = QAction("喂食模式", self)
        feeding_action.triggered.connect(self.enter_feeding_mode)
        menu.addAction(feeding_action)

        talk_mode_action = QAction("话痨模式", self)
        talk_mode_action.triggered.connect(self.create_or_show_talk_dialog)
        menu.addAction(talk_mode_action)

        reward_action = QAction("祝福模式", self)
        reward_action.triggered.connect(self.create_or_show_reward_dialog)
        menu.addAction(reward_action)

        lock_action = QAction(
            "解锁动作切换" if self.runtime.action_locked else "锁定当前动作",
            self,
        )
        lock_action.triggered.connect(self.toggle_action_lock)
        menu.addAction(lock_action)

        auto_sleep = QAction(
            "关闭自动睡觉" if self.config["timing"].get("auto_sleep_enabled", True) else "开启自动睡觉",
            self,
        )
        auto_sleep.triggered.connect(self.toggle_auto_sleep)
        menu.addAction(auto_sleep)

        auto_change = QAction(
            "关闭自动换动作" if self.config["timing"].get("auto_change_action", True) else "开启自动换动作",
            self,
        )
        auto_change.triggered.connect(self.toggle_auto_action)
        menu.addAction(auto_change)

        auto_speech = QAction(
            "关闭自动说话" if self.config.get("speech", {}).get("enabled", True) else "开启自动说话",
            self,
        )
        auto_speech.triggered.connect(self.toggle_auto_speech)
        menu.addAction(auto_speech)

        annoy_toggle = QAction(
            "关闭生气feature" if self.config["timing"].get("annoy_enabled", True) else "开启生气feature",
            self,
        )
        annoy_toggle.triggered.connect(self.toggle_annoy_mode)
        menu.addAction(annoy_toggle)

        reset_override = QAction("恢复初始状态", self)
        reset_override.triggered.connect(self.clear_manual_override)
        menu.addAction(reset_override)

        # reload_assets = QAction("重新读取文件夹", self)
        # reload_assets.triggered.connect(self.reload_assets)
        # menu.addAction(reload_assets)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        menu.addAction(quit_action)

        menu.exec(pos)

    def get_bubble_position(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            return self.pos() + QPoint(self.width() + 10, 10)

        geo = screen.availableGeometry()
        x = self.x() + self.width() - 55
        y = self.y() + 10

        x = max(geo.left() + 10, min(x, geo.right() - 220))
        y = max(geo.top() + 10, min(y, geo.bottom() - 100))
        return QPoint(x, y)
    
    def place_dialog_near_pet(self, dialog, offset_x, offset_y):
        if dialog is None:
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            dialog.move(self.x() + offset_x, self.y() + offset_y)
            return

        geo = screen.availableGeometry()

        x = self.x() + offset_x
        y = self.y() + offset_y

        dialog_w = dialog.width()
        dialog_h = dialog.height()

        x = max(geo.left() + 10, min(x, geo.right() - dialog_w - 10))
        y = max(geo.top() + 10, min(y, geo.bottom() - dialog_h - 10))

        dialog.move(x, y)

    def toggle_auto_speech(self):
        current = self.config.get("speech", {}).get("enabled", True)
        self.config["speech"]["enabled"] = not current
        save_config(self.config)

    def speak_now(self):
        pool = self.get_dialogue_pool()
        if not pool:
            return

        text = self.choose_dialogue(pool)
        if not text:
            return
        self.speech.show_message(self.get_bubble_position(), text)

    def toggle_mirror(self):
        self.mirrored = not self.mirrored
        self.apply_current_visual()

    def apply_square_resize(self, new_size: int):
        clamped = max(self.min_width, min(self.max_width, int(new_size)))
        self.current_width = clamped
        self.resize(clamped, clamped)
        self.apply_current_visual()

        if self.size_dialog is not None:
            self.size_dialog.update_value(
                self.current_width,
                min_size=self.min_width,
                max_size=self.max_width,
            )

    def toggle_action_lock(self):
        self.runtime.action_locked = not self.runtime.action_locked
        self.persist_behavior()

    def toggle_auto_sleep(self):
        self.config["timing"]["auto_sleep_enabled"] = not self.config["timing"].get("auto_sleep_enabled", True)
        save_config(self.config)
        self.apply_schedule_rules(force=True)

    def toggle_auto_action(self):
        self.config["timing"]["auto_change_action"] = not self.config["timing"].get("auto_change_action", True)
        save_config(self.config)

    def toggle_annoy_mode(self):
        current = self.config["timing"].get("annoy_enabled", True)
        self.config["timing"]["annoy_enabled"] = not current
        save_config(self.config)

        if not self.config["timing"]["annoy_enabled"]:
            self.runtime.click_timestamps.clear()

            if self.runtime.current_state == "annoyed":
                self.special_restore_timer.stop()
                self.restore_after_special()

    def clear_manual_override(self):
        if self.feeding_mode:
            self.exit_feeding_mode()
            return
        self.runtime.manual_override = False
        self.runtime.action_locked = False
        self.config["speech"]["enabled"] = True
        self.config["timing"]["auto_sleep_enabled"] = True
        self.config["timing"]["auto_change_action"] = True
        self.config["timing"]["annoy_enabled"] = True
        self.config["behavior"]["locked_action"] = False
        self.config["behavior"]["manual_override"] = False
        self.config["behavior"]["state"] = "normal"
        self.config["behavior"]["fixed_action"] = ""
        self.persist_behavior()
        self.apply_schedule_rules(force=True)

    def reload_assets(self):
        self.state_assets = scan_states()
        self.ensure_valid_state()

        if self.feeding_mode and not self.feeding_assets_ready():
            self.exit_feeding_mode()

        self.apply_current_visual()

    def persist_behavior(self):
        if self.feeding_mode:
            state_to_save = self.pre_feeding_state or "normal"
            action_to_save = self.pre_feeding_action or ""
            manual_to_save = self.pre_feeding_manual_override
        else:
            state_to_save = self.runtime.current_state
            action_to_save = self.runtime.current_action
            manual_to_save = self.runtime.manual_override

        self.config["behavior"]["state"] = state_to_save
        self.config["behavior"]["fixed_action"] = action_to_save
        self.config["behavior"]["manual_override"] = manual_to_save
        self.config["behavior"]["locked_action"] = self.runtime.action_locked
        save_config(self.config)

    def clear_movie_connections(self):
        if self.movie is None:
            return
        try:
            self.movie.frameChanged.disconnect(self.handle_movie_frame_changed)
        except Exception:
            pass

    def apply_current_visual(self, loop: bool = True, on_finished=None):
        state_name = self.runtime.current_state
        action_name = self.runtime.current_action
        variants = self.get_actions_for_state(state_name).get(action_name, [])

        if not variants:
            self.pet_label.setText(f"缺少 GIF: {state_name}/{action_name}")
            self.pet_label.setStyleSheet(
                "color: white; background: rgba(0,0,0,140); border-radius: 12px; padding: 10px;"
            )
            self.pet_label.adjustSize()
            return

        self.runtime.current_variant_index %= len(variants)
        path = variants[self.runtime.current_variant_index]

        if self.movie is not None:
            self.clear_movie_connections()
            self.movie.stop()

        self.single_play_mode = not loop
        self.movie_finished_callback = on_finished
        self.movie_finish_pending = False
        self.last_movie_frame_seen = -1

        self.movie = QMovie(str(path))
        self.movie.setScaledSize(QSize(self.current_width, self.current_width))
        self.movie.setCacheMode(QMovie.CacheAll)

        if self.single_play_mode:
            try:
                self.movie.setLoopCount(1)
            except Exception:
                pass

        self.movie.frameChanged.connect(self.handle_movie_frame_changed)

        if self.mirrored:
            self.movie_mode = "pixmap"
            self.movie.start()
            self.update_mirrored_frame()
        else:
            self.movie_mode = "movie"
            self.pet_label.setMovie(self.movie)
            self.movie.start()

        self.pet_label.setStyleSheet("")
        self.adjustSize()

    def handle_movie_frame_changed(self, frame_number: int):
        if self.mirrored:
            self.update_mirrored_frame()

        if not self.single_play_mode:
            return
        if self.movie is None:
            return
        if self.movie_finish_pending:
            return

        frame_count = self.movie.frameCount()
        if frame_count <= 0:
            return

        last_frame = frame_count - 1
        if frame_number == last_frame and self.last_movie_frame_seen != last_frame:
            self.last_movie_frame_seen = last_frame
            self.movie_finish_pending = True

            callback = self.movie_finished_callback

            def finish():
                self.movie_finish_pending = False
                if callback is not None:
                    callback()

            QTimer.singleShot(0, finish)

    def update_mirrored_frame(self):
        if self.movie is None:
            return
        pix = self.movie.currentPixmap()
        if pix.isNull():
            return
        transformed = pix.transformed(QTransform().scale(-1, 1))
        scaled = transformed.scaled(
            self.current_width,
            self.current_width,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.pet_label.setPixmap(scaled)

    def set_state(self, state_name: str, manual: bool):
        if state_name not in self.state_assets:
            QMessageBox.warning(self, "缺少状态", f"状态文件夹 '{state_name}' 不存在")
            return

        self.runtime.current_state = state_name
        self.runtime.manual_override = manual

        if (
            not self.runtime.action_locked
            or self.runtime.current_action not in self.get_actions_for_state(state_name)
        ):
            self.runtime.current_action = self.pick_random_action(state_name) or ""

        self.runtime.current_variant_index = self.pick_random_variant_index(
            self.runtime.current_state,
            self.runtime.current_action,
        )
        self.apply_current_visual()
        self.persist_behavior()

    def set_state_action_direct(self, state_name: str, action_name: str, loop: bool = True, on_finished=None):
        if state_name not in self.state_assets:
            return
        if action_name not in self.get_actions_for_state(state_name):
            return

        self.runtime.current_state = state_name
        self.runtime.current_action = action_name
        self.runtime.current_variant_index = self.pick_random_variant_index(state_name, action_name)
        self.apply_current_visual(loop=loop, on_finished=on_finished)

    def trigger_temporary_state(self, state_name: str, speech_key: str | None = None, duration_ms: int = 4000):
        if self.feeding_mode:
            return
        if state_name not in self.state_assets:
            return

        self.runtime.special_restore_state = self.runtime.current_state
        self.runtime.special_restore_action = self.runtime.current_action
        self.runtime.current_state = state_name
        self.runtime.current_action = self.pick_random_action(state_name) or ""
        self.runtime.current_variant_index = self.pick_random_variant_index(
            self.runtime.current_state,
            self.runtime.current_action,
        )

        self.apply_current_visual()

        if speech_key:
            self.speak_from_key(speech_key)

        self.special_restore_timer.start(duration_ms)

    def restore_after_special(self):
        restore_state = self.runtime.special_restore_state or "normal"
        restore_action = self.runtime.special_restore_action or self.pick_random_action(restore_state) or ""

        if restore_state not in self.state_assets:
            restore_state = "normal" if "normal" in self.state_assets else next(iter(self.state_assets))
            restore_action = self.pick_random_action(restore_state) or ""

        self.runtime.current_state = restore_state
        self.runtime.current_action = restore_action
        self.runtime.current_variant_index = self.pick_random_variant_index(
            self.runtime.current_state,
            self.runtime.current_action,
        )

        self.apply_current_visual()
        self.persist_behavior()
        self.apply_schedule_rules(force=True)

    def trigger_head_special(self):
        self.trigger_temporary_state("special_head", speech_key="special_head", duration_ms=3500)

    def trigger_body_special(self):
        self.trigger_temporary_state("special_body", speech_key="special_body", duration_ms=3500)

    def get_dialogue_pool(self, key=None):
        if key is not None:
            return self.dialogues.get(key, [])
        state = self.runtime.current_state
        pool = list(self.dialogues.get(state, []))
        if state not in {"special_head", "special_body", "annoyed", "reward", "sleeping"}:
            pool.extend(self.dialogues.get("normal", []))
        return pool or ["..."]

    def update_bubble_position(self):
        if self.speech.isVisible():
            self.speech.reposition(self.get_bubble_position())

    def speak_from_key(self, key):
        pool = self.get_dialogue_pool(key)
        if not pool:
            return
        text = self.choose_dialogue(pool)
        if not text:
            return
        self.speech.show_message(self.get_bubble_position(), text)

    def random_speak(self):
        if self.feeding_mode and self.feeding_phase == "reaction":
            return
        if not self.config.get("speech", {}).get("enabled", True):
            return
        if random.random() > float(self.config["timing"].get("speech_probability", 0.35)):
            return
        pool = self.get_dialogue_pool()
        if not pool:
            return
        text = self.choose_dialogue(pool)
        if not text:
            return
        self.speech.show_message(self.get_bubble_position(), text)

    def cycle_to_next_variant(self):
        variants = self.get_current_variants()
        if not variants:
            return
        self.runtime.current_variant_index = (self.runtime.current_variant_index + 1) % len(variants)
        self.apply_current_visual()
        self.persist_behavior()

    def change_action_manual(self):
        if self.feeding_mode:
            return
        if self.runtime.action_locked:
            return

        actions_map = self.get_actions_for_state(self.runtime.current_state)
        if not actions_map:
            return

        current_variants = self.get_current_variants()
        current_path = None
        if current_variants and 0 <= self.runtime.current_variant_index < len(current_variants):
            current_path = current_variants[self.runtime.current_variant_index]

        candidates = []
        for action_name, variants in actions_map.items():
            for i, path in enumerate(variants):
                if current_path is None or path != current_path:
                    candidates.append((action_name, i))

        if not candidates:
            return

        action_name, variant_index = random.choice(candidates)
        self.runtime.current_action = action_name
        self.runtime.current_variant_index = variant_index

        self.apply_current_visual()
        self.persist_behavior()

    # def change_action_manual(self):
    #     if self.feeding_mode:
    #         return
    #     if self.runtime.action_locked:
    #         return

    #     variants = self.get_current_variants()
    #     if len(variants) > 1:
    #         self.cycle_to_next_variant()
    #         return

    #     actions = list(self.get_actions_for_state(self.runtime.current_state).keys())
    #     if len(actions) <= 1:
    #         return

    #     if self.runtime.current_action in actions:
    #         idx = actions.index(self.runtime.current_action)
    #         self.runtime.current_action = actions[(idx + 1) % len(actions)]
    #     else:
    #         self.runtime.current_action = actions[0]

    #     self.runtime.current_variant_index = self.pick_random_variant_index(
    #         self.runtime.current_state,
    #         self.runtime.current_action,
    #     )
    #     self.apply_current_visual()
    #     self.persist_behavior()

    # def maybe_bug_override(self):
    #     if "bug" not in self.state_assets:
    #         return None

    #     now = datetime.now()
    #     current_minute = int(now.timestamp() // 60)
    #     cooldown = int(self.config["timing"].get("bug_state_cooldown_minutes", 25))

    #     if current_minute - self.runtime.last_bug_trigger_minute < cooldown:
    #         return None

    #     if random.random() < float(self.config["timing"].get("bug_state_probability", 0.08)):
    #         self.runtime.last_bug_trigger_minute = current_minute
    #         return "bug"

    #     return None

    def resolve_scheduled_state(self):
        now = datetime.now()
        hour = now.hour
        minute = now.minute

        meal_hours = self.config["timing"].get("meal_hours", [12, 19])
        meal_window = int(self.config["timing"].get("meal_minute_window", 20))
        # sad_delay = int(self.config["timing"].get("sad_meal_delay_minutes", 35))

        if self.config["timing"].get("auto_sleep_enabled", True):
            sleep_hour = int(self.config["timing"].get("sleep_hour", 13))
            wake_hour = int(self.config["timing"].get("wake_hour", 6))

            if hour >= sleep_hour or hour < wake_hour:
                return "sleeping"

        for meal_hour in meal_hours:
            if hour == int(meal_hour) and minute < meal_window:
                return "eating"

            # if hour == int(meal_hour) and minute >= sad_delay and self.runtime.current_state != "eating":
            #     return "sad_meal"

        return "normal"

    # def apply_schedule_rules(self, force=False):
    #     if self.feeding_mode:
    #         return

    #     current_is_special = self.runtime.current_state.startswith("special_")
    #     scheduled_state = self.resolve_scheduled_state()
    #     # bug_state = self.maybe_bug_override()

    #     if self.runtime.manual_override and not force and scheduled_state == "normal" and not current_is_special:
    #         return

    #     # new_state = bug_state or scheduled_state
    #     new_state = scheduled_state

    #     if new_state != self.runtime.current_state or force:
    #         self.runtime.manual_override = False
    #         self.set_state(new_state, manual=False)

    def apply_schedule_rules(self, force=False):
        if self.feeding_mode:
            return

        current_is_special = self.runtime.current_state.startswith("special_")
        scheduled_state = self.resolve_scheduled_state()

        if self.runtime.manual_override and not force and not current_is_special:
            return

        new_state = scheduled_state

        if new_state != self.runtime.current_state or force:
            self.runtime.manual_override = False
            self.set_state(new_state, manual=False)

    def register_click_for_annoyed(self):
        if self.feeding_mode:
            return

        if not self.config["timing"].get("annoy_enabled", True):
            return

        now = time.time()
        self.runtime.click_timestamps.append(now)

        window_seconds = int(self.config["timing"].get("annoy_click_window_seconds", 17))
        threshold = int(self.config["timing"].get("annoy_click_threshold", 15))

        self.runtime.click_timestamps = [
            t for t in self.runtime.click_timestamps if now - t <= window_seconds
        ]

        if len(self.runtime.click_timestamps) >= threshold:
            self.runtime.click_timestamps.clear()
            self.trigger_temporary_state("annoyed", speech_key="annoyed", duration_ms=10000)

    def change_action_if_needed(self):
        if self.feeding_mode:
            return
        if not self.config["timing"].get("auto_change_action", True):
            return
        if self.runtime.action_locked:
            return
        if self.runtime.current_state.startswith("special_"):
            return
        self.change_action_manual()

    def tick(self):
        self.apply_schedule_rules()

    def feeding_assets_ready(self):
        actions = self.get_actions_for_state("feeding")
        if not actions:
            return False
        return "enter" in actions and "idle" in actions and (
            "react" in actions or "react_cake" in actions or "react_beer" in actions or "react_tea" in actions or "react_fruit" in actions or "react_chips" in actions or "react_fried_chicken" in actions
        )

    def enter_feeding_mode(self):
        if self.feeding_mode:
            self.create_or_show_food_dialog()
            return

        if "feeding" not in self.state_assets or not self.feeding_assets_ready():
            QMessageBox.information(
                self,
                "缺少喂食资源",
                "请先准备 states/feeding/enter, idle, react 对应的 GIF。",
            )
            return

        self.pre_feeding_state = self.runtime.current_state
        self.pre_feeding_action = self.runtime.current_action
        self.pre_feeding_manual_override = self.runtime.manual_override

        self.feeding_mode = True
        self.feeding_phase = "enter"
        self.create_or_show_food_dialog()
        self.play_feeding_enter()

    def exit_feeding_mode(self):
        self.feeding_mode = False
        self.feeding_phase = None

        if self.food_dialog is not None and self.food_dialog.isVisible():
            self.food_dialog.hide()

        self.pre_feeding_state = None
        self.pre_feeding_action = None
        self.pre_feeding_manual_override = False

        if "normal" in self.state_assets:
            self.runtime.current_state = "normal"
            self.runtime.current_action = self.pick_random_action("normal") or ""
            self.runtime.manual_override = False
            self.runtime.current_variant_index = self.pick_random_variant_index(
                self.runtime.current_state,
                self.runtime.current_action,
            )
            self.apply_current_visual()
            self.persist_behavior()
        else:
            self.apply_schedule_rules(force=True)

    def play_feeding_enter(self):
        if not self.feeding_mode:
            return
        self.feeding_phase = "enter"
        self.set_state_action_direct(
            "feeding",
            "enter",
            loop=False,
            on_finished=self.play_feeding_idle,
        )

    def play_feeding_idle(self):
        if not self.feeding_mode:
            return
        self.feeding_phase = "idle"
        self.set_state_action_direct(
            "feeding",
            "idle",
            loop=True,
            on_finished=None,
        )

    def play_feeding_reaction(self, food_type: str):
        if not self.feeding_mode:
            return

        self.feeding_phase = "reaction"

        preferred_action = f"react_{food_type}"
        if preferred_action in self.get_actions_for_state("feeding"):
            action_name = preferred_action
        elif "react" in self.get_actions_for_state("feeding"):
            action_name = "react"
        else:
            action_name = "idle"

        self.set_state_action_direct(
            "feeding",
            action_name,
            loop=False if action_name != "idle" else True,
            on_finished=self.play_feeding_idle if action_name != "idle" else None,
        )

        if food_type == "cake":
            self.speak_from_key("feeding_cake")
        elif food_type == "beer":
            self.speak_from_key("feeding_beer")
        elif food_type == "tea":
            self.speak_from_key("feeding_tea")
        elif food_type == "fruit":
            self.speak_from_key("feeding_fruit")
        elif food_type == "chips":
            self.speak_from_key("feeding_chips")
        elif food_type == "fried_chicken":
            self.speak_from_key("feeding_fried_chicken")
        else:
            self.speak_from_key("feeding")

    def feed_pet(self, food_type: str):
        if not self.feeding_mode:
            return
        self.play_feeding_reaction(food_type)

    def dragEnterEvent(self, event):
        if not self.feeding_mode:
            event.ignore()
            return

        mime = event.mimeData()
        if (
            mime is not None
            and mime.hasFormat("application/x-desktop-pet-food")
            and self.feeding_phase in {"idle", "enter"}
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not self.feeding_mode:
            event.ignore()
            return

        mime = event.mimeData()
        if mime is None or not mime.hasFormat("application/x-desktop-pet-food"):
            event.ignore()
            return

        food_type = bytes(mime.data("application/x-desktop-pet-food")).decode("utf-8").strip()
        self.feed_pet(food_type)
        event.acceptProposedAction()

    def closeEvent(self, event):
        self.persist_behavior()
        # self.config["window"]["start_x"] = self.x()
        # self.config["window"]["start_y"] = self.y()
        save_config(self.config)

        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()

        if self.size_dialog is not None:
            self.size_dialog.hide()
        if self.talk_dialog is not None:
            self.talk_dialog.hide()
        if self.reward_dialog is not None:
            self.reward_dialog.hide()
        if self.food_dialog is not None:
            self.food_dialog.hide()

        event.accept()