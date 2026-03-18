from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt, QUrl
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from question_config import QUESTION_SECTIONS, REMARK_KEY


SUPPORTED_AUDIO_EXTENSIONS = {
    ".aac",
    ".amr",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}

THEMES = {
    "light": {
        "window_start": "#f4f7fb",
        "window_end": "#e8eef8",
        "panel_bg": "rgba(255, 255, 255, 0.72)",
        "panel_alt_bg": "rgba(255, 255, 255, 0.58)",
        "card_bg": "rgba(255, 255, 255, 0.86)",
        "card_border": "rgba(124, 146, 181, 0.22)",
        "text_primary": "#162033",
        "text_muted": "#5f6f8f",
        "accent": "#1f6feb",
        "accent_hover": "#175fd1",
        "secondary_bg": "rgba(223, 231, 245, 0.72)",
        "secondary_hover": "rgba(214, 225, 242, 0.96)",
        "input_bg": "rgba(250, 252, 255, 0.92)",
        "input_border": "rgba(154, 172, 204, 0.35)",
        "shadow": "#adc1e6",
        "shadow_alpha": 80,
        "slider_groove": "rgba(173, 190, 220, 0.45)",
    },
    "dark": {
        "window_start": "#0f1726",
        "window_end": "#172235",
        "panel_bg": "rgba(18, 28, 44, 0.76)",
        "panel_alt_bg": "rgba(18, 28, 44, 0.66)",
        "card_bg": "rgba(24, 36, 56, 0.88)",
        "card_border": "rgba(138, 166, 214, 0.22)",
        "text_primary": "#f4f7ff",
        "text_muted": "#a9b6cf",
        "accent": "#6ea8ff",
        "accent_hover": "#5c97f4",
        "secondary_bg": "rgba(38, 54, 80, 0.9)",
        "secondary_hover": "rgba(50, 68, 98, 0.96)",
        "input_bg": "rgba(18, 28, 44, 0.95)",
        "input_border": "rgba(112, 139, 184, 0.35)",
        "shadow": "#08111f",
        "shadow_alpha": 160,
        "slider_groove": "rgba(90, 114, 156, 0.54)",
    },
}


def format_ms(ms: int) -> str:
    seconds = max(ms, 0) // 1000
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    if hour:
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    return f"{minute:02d}:{second:02d}"


class AnnotationWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("语音标注软件")
        self.resize(1520, 900)

        self.audio_files: list[Path] = []
        self.audio_index = -1
        self.audio_dir: Path | None = None
        self.json_dir = Path.cwd() / "json"
        self.json_dir.mkdir(exist_ok=True)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        self.single_groups: dict[str, QButtonGroup] = {}
        self.multi_groups: dict[str, list[QCheckBox]] = {}
        self.question_labels: dict[str, str] = {}
        self.preview_cache = "{}"
        self.current_theme = "light"
        self.shadow_targets: list[QWidget] = []
        self.is_slider_pressed = False

        self._build_ui()
        self._connect_player_signals()
        self.apply_theme()
        self.update_summary()

    def _build_ui(self) -> None:
        self.root = QWidget()
        self.root.setObjectName("appRoot")
        self.setCentralWidget(self.root)

        root_layout = QVBoxLayout(self.root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setObjectName("mainScrollArea")
        root_layout.addWidget(scroll_area)

        content = QWidget()
        content.setObjectName("contentWidget")
        scroll_area.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        hero_card, hero_layout = self.create_glass_card("heroCard", 20, 18, 20, 18)
        hero_row = QHBoxLayout()
        hero_row.setSpacing(16)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(6)

        app_title = QLabel("语音标注软件")
        app_title.setObjectName("appTitle")
        app_subtitle = QLabel("清晰、轻快、适合连续标注的桌面工作台。")
        app_subtitle.setObjectName("appSubtitle")
        self.audio_name_label = QLabel("当前音频：未加载")
        self.audio_name_label.setObjectName("audioNameLabel")

        hero_text.addWidget(app_title)
        hero_text.addWidget(app_subtitle)
        hero_text.addWidget(self.audio_name_label)
        hero_text.addStretch()

        hero_actions = QHBoxLayout()
        hero_actions.setSpacing(10)
        hero_actions.addStretch()

        self.theme_button = QPushButton("切换夜间")
        self.theme_button.setCheckable(True)
        self.theme_button.setProperty("variant", "secondary")
        self.theme_button.setMinimumHeight(44)
        self.theme_button.setMinimumWidth(146)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.open_folder_button = QPushButton("打开音频文件夹")
        self.open_folder_button.setProperty("variant", "secondary")
        self.open_folder_button.setMinimumHeight(44)
        self.open_folder_button.setMinimumWidth(164)
        self.open_folder_button.clicked.connect(self.choose_audio_folder)

        hero_actions.addWidget(self.theme_button)
        hero_actions.addWidget(self.open_folder_button)

        hero_row.addLayout(hero_text, 1)
        hero_row.addLayout(hero_actions)
        hero_layout.addLayout(hero_row)
        main_layout.addWidget(hero_card)

        progress_card, progress_layout = self.create_glass_card("panelCard", 16, 16, 16, 16)
        progress_header = QHBoxLayout()
        progress_header.setSpacing(12)

        progress_title = QLabel("播放进度")
        progress_title.setObjectName("sectionTitle")
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("timeLabel")

        progress_header.addWidget(progress_title)
        progress_header.addStretch()
        progress_header.addWidget(self.time_label)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)

        progress_layout.addLayout(progress_header)
        progress_layout.addWidget(self.progress_slider)
        main_layout.addWidget(progress_card)

        control_card, control_layout = self.create_glass_card("panelCard", 12, 14, 12, 14)
        controls = QHBoxLayout()
        controls.setSpacing(14)
        controls.addStretch()

        self.prev_button = QPushButton("上一条")
        self.prev_button.setProperty("variant", "secondary")
        self.prev_button.clicked.connect(self.play_previous)

        self.play_button = QPushButton("继续播放")
        self.play_button.setProperty("variant", "primary")
        self.play_button.clicked.connect(self.resume_playback)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setProperty("variant", "secondary")
        self.pause_button.clicked.connect(self.pause_playback)

        self.next_button = QPushButton("下一条")
        self.next_button.setProperty("variant", "secondary")
        self.next_button.clicked.connect(self.play_next)

        for button in (self.prev_button, self.play_button, self.pause_button, self.next_button):
            button.setMinimumHeight(44)
            button.setMinimumWidth(130)
            controls.addWidget(button)

        controls.addStretch()
        control_layout.addLayout(controls)
        main_layout.addWidget(control_card)

        questions_shell, questions_shell_layout = self.create_glass_card("panelCard", 16, 16, 16, 16)
        questions_title = QLabel("标注维度")
        questions_title.setObjectName("sectionTitle")
        questions_shell_layout.addWidget(questions_title)

        questions_panel = QWidget()
        questions_panel.setObjectName("questionsPanel")
        self.questions_layout = QHBoxLayout(questions_panel)
        self.questions_layout.setContentsMargins(0, 0, 0, 0)
        self.questions_layout.setSpacing(12)
        self._build_question_groups()

        questions_shell_layout.addWidget(questions_panel)
        main_layout.addWidget(questions_shell)

        remark_card, remark_layout = self.create_glass_card("panelCard", 16, 16, 16, 16)
        remark_title = QLabel("描述音频")
        remark_title.setObjectName("sectionTitle")
        self.remark_edit = QPlainTextEdit()
        self.remark_edit.setObjectName("remarkEdit")
        self.remark_edit.setPlaceholderText("简要描述这段音频的内容、场景或特殊情况。")
        self.remark_edit.textChanged.connect(self.update_summary)
        self.remark_edit.setFixedHeight(60)

        remark_layout.addWidget(remark_title)
        remark_layout.addWidget(self.remark_edit)
        main_layout.addWidget(remark_card)

        action_card, action_layout = self.create_glass_card("panelCard", 12, 16, 12, 16)
        actions = QHBoxLayout()
        actions.setSpacing(12)
        actions.addStretch()

        self.preview_button = QPushButton("预览 JSON")
        self.preview_button.setProperty("variant", "secondary")
        self.preview_button.setMinimumHeight(54)
        self.preview_button.setMinimumWidth(190)
        self.preview_button.clicked.connect(self.show_preview_dialog)

        self.reset_button = QPushButton("重做")
        self.reset_button.setProperty("variant", "secondary")
        self.reset_button.setMinimumHeight(54)
        self.reset_button.setMinimumWidth(190)
        self.reset_button.clicked.connect(self.reset_current_annotation)

        self.submit_button = QPushButton("提交")
        self.submit_button.setProperty("variant", "primary")
        self.submit_button.setMinimumHeight(54)
        self.submit_button.setMinimumWidth(230)
        self.submit_button.clicked.connect(self.submit_annotation)

        actions.addWidget(self.preview_button)
        actions.addWidget(self.reset_button)
        actions.addWidget(self.submit_button)
        actions.addStretch()
        action_layout.addLayout(actions)
        main_layout.addWidget(action_card)
        main_layout.addStretch()

    def _build_question_groups(self) -> None:
        questions = [question for section in QUESTION_SECTIONS for question in section["questions"]]
        column_layouts: list[QVBoxLayout] = []

        for _ in range(3):
            column = QVBoxLayout()
            column.setSpacing(12)
            column.setContentsMargins(0, 0, 0, 0)
            column_layouts.append(column)
            self.questions_layout.addLayout(column, 1)

        for index, question in enumerate(questions):
            self.question_labels[question["key"]] = question["label"]

            card, card_layout = self.create_glass_card("questionCard", 14, 14, 14, 14)
            card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            card_layout.setSpacing(8)

            label = QLabel(f"{question['label']}  ({question['key']})")
            label.setObjectName("questionTitle")
            label.setWordWrap(True)
            card_layout.addWidget(label)

            if question["type"] == "single":
                group = QButtonGroup(self)
                group.setExclusive(True)
                self.single_groups[question["key"]] = group
                for option in question["options"]:
                    button = QRadioButton(f"{option['label']}  [{option['value']}]")
                    button.setProperty("value", option["value"])
                    button.setObjectName("optionButton")
                    button.toggled.connect(self.update_summary)
                    group.addButton(button)
                    card_layout.addWidget(button)
            else:
                checkboxes: list[QCheckBox] = []
                self.multi_groups[question["key"]] = checkboxes
                for option in question["options"]:
                    checkbox = QCheckBox(f"{option['label']}  [{option['value']}]")
                    checkbox.setProperty("value", option["value"])
                    checkbox.setObjectName("optionButton")
                    checkbox.stateChanged.connect(self.update_summary)
                    checkboxes.append(checkbox)
                    card_layout.addWidget(checkbox)

            column_layouts[index % 3].addWidget(card)

        for column in column_layouts:
            column.addStretch()

    def _connect_player_signals(self) -> None:
        self.player.positionChanged.connect(self._sync_position)
        self.player.durationChanged.connect(self._sync_duration)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)

    def choose_audio_folder(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择音频文件夹", str(Path.cwd()))
        if not directory:
            return
        self.load_audio_folder(Path(directory))

    def load_audio_folder(self, folder: Path) -> None:
        files = sorted(
            path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
        )
        if not files:
            QMessageBox.warning(self, "未找到音频", "当前文件夹中没有支持的音频文件。")
            return

        self.audio_dir = folder
        self.audio_files = files
        self.audio_index = 0
        self.load_current_audio(auto_play=False)

    def load_current_audio(self, auto_play: bool = True) -> None:
        if not self.audio_files or self.audio_index < 0:
            return

        audio_path = self.audio_files[self.audio_index]
        self.audio_name_label.setText(f"当前音频：{audio_path.name}")
        self.player.setSource(QUrl.fromLocalFile(str(audio_path)))
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        self.load_existing_annotation()
        self.update_summary()

        if auto_play:
            self.player.play()

    def play_previous(self) -> None:
        if not self.audio_files:
            return
        if self.audio_index > 0:
            self.audio_index -= 1
            self.load_current_audio()

    def play_next(self) -> None:
        if not self.audio_files:
            return
        if self.audio_index < len(self.audio_files) - 1:
            self.audio_index += 1
            self.load_current_audio()

    def pause_playback(self) -> None:
        self.player.pause()

    def resume_playback(self) -> None:
        if not self.audio_files:
            self.choose_audio_folder()
            return
        self.player.play()

    def _on_slider_pressed(self) -> None:
        self.is_slider_pressed = True

    def _on_slider_released(self) -> None:
        self.is_slider_pressed = False
        self.player.setPosition(self.progress_slider.value())

    def _sync_position(self, position: int) -> None:
        if not self.is_slider_pressed:
            self.progress_slider.setValue(position)
        self.time_label.setText(f"{format_ms(position)} / {format_ms(self.player.duration())}")

    def _sync_duration(self, duration: int) -> None:
        self.progress_slider.setRange(0, duration)
        self.time_label.setText(f"{format_ms(self.player.position())} / {format_ms(duration)}")

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.EndOfMedia and self.audio_index < len(self.audio_files) - 1:
            self.audio_index += 1
            self.load_current_audio()

    def current_audio_path(self) -> Path | None:
        if not self.audio_files or self.audio_index < 0:
            return None
        return self.audio_files[self.audio_index]

    def current_json_path(self) -> Path | None:
        audio_path = self.current_audio_path()
        if not audio_path:
            return None
        return self.json_dir / f"{audio_path.stem}.json"

    def collect_annotation(self) -> dict:
        audio_path = self.current_audio_path()
        payload: dict[str, object] = {"audio_id": audio_path.stem if audio_path else ""}

        for key, group in self.single_groups.items():
            checked = group.checkedButton()
            payload[key] = checked.property("value") if checked else ""

        for key, checkboxes in self.multi_groups.items():
            payload[key] = [box.property("value") for box in checkboxes if box.isChecked()]

        payload[REMARK_KEY] = self.remark_edit.toPlainText().strip()
        return payload

    def update_summary(self) -> None:
        payload = self.collect_annotation()
        self.preview_cache = json.dumps(payload, ensure_ascii=False, indent=2)

    def show_preview_dialog(self) -> None:
        self.update_summary()
        dialog = QDialog(self)
        dialog.setWindowTitle("JSON 预览")
        dialog.resize(700, 620)
        dialog.setStyleSheet(self.dialog_stylesheet())

        layout = QVBoxLayout(dialog)
        preview = QPlainTextEdit()
        preview.setObjectName("jsonPreview")
        preview.setReadOnly(True)
        preview.setPlainText(self.preview_cache)
        layout.addWidget(preview)

        close_button = QPushButton("关闭")
        close_button.setProperty("variant", "primary")
        close_button.clicked.connect(dialog.accept)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(close_button)
        layout.addLayout(button_row)
        dialog.exec()

    def reset_current_annotation(self) -> None:
        for group in self.single_groups.values():
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)

        for checkboxes in self.multi_groups.values():
            for checkbox in checkboxes:
                checkbox.setChecked(False)

        self.remark_edit.clear()
        self.update_summary()

    def load_existing_annotation(self) -> None:
        self.reset_current_annotation()
        json_path = self.current_json_path()
        if not json_path or not json_path.exists():
            return

        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            QMessageBox.warning(self, "读取失败", f"已有标注文件读取失败：{json_path.name}")
            return

        for key, group in self.single_groups.items():
            value = payload.get(key)
            if not value:
                continue
            for button in group.buttons():
                if button.property("value") == value:
                    button.setChecked(True)
                    break

        for key, checkboxes in self.multi_groups.items():
            selected_values = set(payload.get(key, []))
            for checkbox in checkboxes:
                checkbox.setChecked(checkbox.property("value") in selected_values)

        blocker = QSignalBlocker(self.remark_edit)
        self.remark_edit.setPlainText(payload.get(REMARK_KEY, ""))
        del blocker
        self.update_summary()

    def submit_annotation(self) -> None:
        audio_path = self.current_audio_path()
        if not audio_path:
            QMessageBox.information(self, "提示", "请先打开一个包含音频文件的文件夹。")
            return

        payload = self.collect_annotation()
        json_path = self.current_json_path()
        if not json_path:
            return

        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        QMessageBox.information(self, "提交成功", f"已生成：{json_path}")

    def toggle_theme(self) -> None:
        self.current_theme = "dark" if self.theme_button.isChecked() else "light"
        self.theme_button.setText("切换日间" if self.current_theme == "dark" else "切换夜间")
        self.apply_theme()

    def create_glass_card(
        self,
        object_name: str,
        left: int = 16,
        top: int = 16,
        right: int = 16,
        bottom: int = 16,
    ) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName(object_name)
        frame.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(left, top, right, bottom)
        layout.setSpacing(10)

        self.attach_shadow(frame)
        return frame, layout

    def attach_shadow(self, widget: QWidget) -> None:
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(36)
        effect.setOffset(0, 16)
        widget.setGraphicsEffect(effect)
        self.shadow_targets.append(widget)

    def apply_theme(self) -> None:
        theme = THEMES[self.current_theme]
        for widget in self.shadow_targets:
            effect = widget.graphicsEffect()
            if isinstance(effect, QGraphicsDropShadowEffect):
                shadow_color = QColor(theme["shadow"])
                shadow_color.setAlpha(theme["shadow_alpha"])
                effect.setColor(shadow_color)

        self.setStyleSheet(self.build_stylesheet(theme))

    def build_stylesheet(self, theme: dict[str, str | int]) -> str:
        return f"""
            QWidget#appRoot {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {theme["window_start"]},
                    stop: 1 {theme["window_end"]}
                );
                color: {theme["text_primary"]};
            }}
            QFrame#heroCard {{
                background: {theme["panel_bg"]};
                border: 1px solid {theme["card_border"]};
                border-radius: 24px;
            }}
            QFrame#panelCard {{
                background: {theme["panel_alt_bg"]};
                border: 1px solid {theme["card_border"]};
                border-radius: 20px;
            }}
            QFrame#questionCard {{
                background: {theme["card_bg"]};
                border: 1px solid {theme["card_border"]};
                border-radius: 18px;
            }}
            QLabel#appTitle {{
                font-size: 28px;
                font-weight: 800;
                color: {theme["text_primary"]};
            }}
            QLabel#appSubtitle {{
                font-size: 13px;
                color: {theme["text_muted"]};
            }}
            QLabel#audioNameLabel {{
                font-size: 22px;
                font-weight: 700;
                color: {theme["text_primary"]};
                padding-top: 6px;
            }}
            QLabel#sectionTitle {{
                font-size: 17px;
                font-weight: 700;
                color: {theme["text_primary"]};
            }}
            QLabel#timeLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {theme["text_muted"]};
            }}
            QLabel#questionTitle {{
                font-size: 14px;
                font-weight: 700;
                color: {theme["text_primary"]};
                padding-bottom: 4px;
            }}
            QPlainTextEdit#remarkEdit,
            QPlainTextEdit#jsonPreview {{
                background: {theme["input_bg"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["input_border"]};
                border-radius: 14px;
                padding: 8px 10px;
                font-size: 13px;
            }}
            QPlainTextEdit#jsonPreview {{
                font-family: Menlo, Monaco, monospace;
            }}
            QPushButton {{
                border-radius: 14px;
                border: none;
                padding: 10px 22px;
                font-size: 15px;
                font-weight: 700;
            }}
            QPushButton[variant="primary"] {{
                background: {theme["accent"]};
                color: white;
            }}
            QPushButton[variant="primary"]:hover {{
                background: {theme["accent_hover"]};
            }}
            QPushButton[variant="secondary"] {{
                background: {theme["secondary_bg"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["card_border"]};
            }}
            QPushButton[variant="secondary"]:hover {{
                background: {theme["secondary_hover"]};
            }}
            QRadioButton#optionButton,
            QCheckBox#optionButton {{
                color: {theme["text_primary"]};
                font-size: 12px;
                spacing: 10px;
                padding-top: 2px;
                padding-bottom: 2px;
            }}
            QSlider#progressSlider::groove:horizontal {{
                height: 10px;
                background: {theme["slider_groove"]};
                border-radius: 5px;
            }}
            QSlider#progressSlider::sub-page:horizontal {{
                background: {theme["accent"]};
                border-radius: 5px;
            }}
            QSlider#progressSlider::handle:horizontal {{
                background: white;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid {theme["accent"]};
            }}
        """

    def dialog_stylesheet(self) -> str:
        theme = THEMES[self.current_theme]
        return f"""
            QDialog {{
                background: {theme["panel_bg"]};
                color: {theme["text_primary"]};
            }}
            QPlainTextEdit#jsonPreview {{
                background: {theme["input_bg"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["input_border"]};
                border-radius: 14px;
                padding: 8px 10px;
                font-size: 13px;
                font-family: Menlo, Monaco, monospace;
            }}
            QPushButton {{
                border-radius: 12px;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton[variant="primary"] {{
                background: {theme["accent"]};
                color: white;
            }}
        """


def main() -> None:
    app = QApplication(sys.argv)
    window = AnnotationWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
