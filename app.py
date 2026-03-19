from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt, QUrl
from PySide6.QtGui import QAction
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QRadioButton,
    QSlider,
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
        self.resize(1500, 880)

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
        self.question_types: dict[str, str] = {}
        self.question_configs: dict[str, dict] = {}
        self.required_question_keys: set[str] = set()
        self.multi_exclusive_values: dict[str, str] = {}
        self.preview_cache = "{}"

        self.is_slider_pressed = False

        self._build_ui()
        self._connect_player_signals()
        self.update_summary()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        self.audio_name_label = QLabel("当前音频：未加载")
        self.audio_name_label.setAlignment(Qt.AlignCenter)
        self.audio_name_label.setStyleSheet(
            "font-size: 20px; font-weight: 700; padding: 8px; background: #f5f7fb; border-radius: 8px;"
        )

        self.open_folder_button = QPushButton("打开音频文件夹")
        self.open_folder_button.clicked.connect(self.choose_audio_folder)
        self.open_folder_button.setMinimumHeight(34)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(self.audio_name_label, 1)
        title_layout.addWidget(self.open_folder_button)
        main_layout.addLayout(title_layout)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet("font-size: 12px; color: #666;")

        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.time_label)
        main_layout.addLayout(progress_layout)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.prev_button = QPushButton("上一条")
        self.prev_button.clicked.connect(self.play_previous)
        self.play_button = QPushButton("继续播放")
        self.play_button.clicked.connect(self.resume_playback)
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.pause_playback)
        self.next_button = QPushButton("下一条")
        self.next_button.clicked.connect(self.play_next)

        control_layout.addStretch()
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.next_button)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        questions_panel = QWidget()
        self.questions_layout = QGridLayout(questions_panel)
        self.questions_layout.setContentsMargins(2, 2, 2, 2)
        self.questions_layout.setHorizontalSpacing(8)
        self.questions_layout.setVerticalSpacing(8)
        self._build_question_groups()
        main_layout.addWidget(questions_panel, 1)

        remark_title = QLabel("描述音频")
        remark_title.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.remark_edit = QPlainTextEdit()
        self.remark_edit.setPlaceholderText("简要描述这段音频的内容、场景或特殊情况。")
        self.remark_edit.textChanged.connect(self.update_summary)
        self.remark_edit.setFixedHeight(58)
        self.remark_edit.setStyleSheet("font-size: 13px; padding: 6px 8px;")
        main_layout.addWidget(remark_title)
        main_layout.addWidget(self.remark_edit, 0)
        self.apply_default_selections()

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        self.preview_button = QPushButton("预览 JSON")
        self.preview_button.clicked.connect(self.show_preview_dialog)
        self.reset_button = QPushButton("重做")
        self.reset_button.clicked.connect(self.reset_current_annotation)
        self.reset_button.setMinimumHeight(52)
        self.reset_button.setMinimumWidth(180)
        self.reset_button.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.submit_button = QPushButton("提交")
        self.submit_button.clicked.connect(self.submit_annotation)
        self.submit_button.setMinimumHeight(52)
        self.submit_button.setMinimumWidth(220)
        self.submit_button.setStyleSheet(
            "background: #1f6feb; color: white; font-size: 16px; font-weight: 700; padding: 10px 30px;"
        )
        self.preview_button.setMinimumHeight(52)
        self.preview_button.setMinimumWidth(180)
        self.preview_button.setStyleSheet("font-size: 16px; font-weight: 700;")

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.preview_button)
        bottom_layout.addWidget(self.reset_button)
        bottom_layout.addWidget(self.submit_button)
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        open_folder_action = QAction("打开音频文件夹", self)
        open_folder_action.triggered.connect(self.choose_audio_folder)
        self.menuBar().addAction(open_folder_action)

    def _build_question_groups(self) -> None:
        questions = [question for section in QUESTION_SECTIONS for question in section["questions"]]

        for index, question in enumerate(questions):
            self.question_configs[question["key"]] = question
            self.question_labels[question["key"]] = question["label"]
            self.question_types[question["key"]] = question["type"]
            if question.get("required"):
                self.required_question_keys.add(question["key"])
            if question["type"] == "multi" and question.get("exclusive_value"):
                self.multi_exclusive_values[question["key"]] = question["exclusive_value"]

            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet(
                "QFrame { background: white; border: 1px solid #d9dee7; border-radius: 10px; }"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(4)

            label = QLabel(f"{question['label']}  ({question['key']})")
            label.setWordWrap(True)
            label.setStyleSheet("font-size: 14px; font-weight: 700;")
            card_layout.addWidget(label)

            if question["type"] == "single":
                group = QButtonGroup(self)
                group.setExclusive(True)
                self.single_groups[question["key"]] = group
                for option in question["options"]:
                    button = QRadioButton(f"{option['label']}  [{option['value']}]")
                    button.setProperty("value", option["value"])
                    button.setStyleSheet("font-size: 11px; padding-top: 1px; padding-bottom: 1px;")
                    button.toggled.connect(self.update_summary)
                    group.addButton(button)
                    card_layout.addWidget(button)
            else:
                checkboxes: list[QCheckBox] = []
                self.multi_groups[question["key"]] = checkboxes
                for option in question["options"]:
                    checkbox = QCheckBox(f"{option['label']}  [{option['value']}]")
                    checkbox.setProperty("value", option["value"])
                    checkbox.setStyleSheet("font-size: 11px; padding-top: 1px; padding-bottom: 1px;")
                    checkbox.stateChanged.connect(
                        lambda _state, key=question["key"], box=checkbox: self._handle_multi_change(key, box)
                    )
                    checkboxes.append(checkbox)
                    card_layout.addWidget(checkbox)

            row = index // 4
            column = index % 4
            self.questions_layout.addWidget(card, row, column)

        for column in range(4):
            self.questions_layout.setColumnStretch(column, 1)

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
        if status == QMediaPlayer.EndOfMedia:
            self.player.pause()
            self.player.setPosition(0)
            self.progress_slider.setValue(0)
            self.time_label.setText(f"00:00 / {format_ms(self.player.duration())}")

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

    def apply_default_selections(self) -> None:
        for key, question in self.question_configs.items():
            default_value = question.get("default")
            if question["type"] == "single":
                if not default_value:
                    continue
                group = self.single_groups[key]
                for button in group.buttons():
                    if button.property("value") == default_value:
                        button.setChecked(True)
                        break
            else:
                selected_defaults = set(default_value or [])
                for checkbox in self.multi_groups[key]:
                    checkbox.setChecked(checkbox.property("value") in selected_defaults)

        self.update_summary()

    def _handle_multi_change(self, key: str, changed_box: QCheckBox) -> None:
        exclusive_value = self.multi_exclusive_values.get(key)
        if exclusive_value is None:
            self.update_summary()
            return

        checkboxes = self.multi_groups[key]
        changed_value = changed_box.property("value")

        if changed_box.isChecked() and changed_value == exclusive_value:
            for checkbox in checkboxes:
                if checkbox is changed_box:
                    continue
                blocker = QSignalBlocker(checkbox)
                checkbox.setChecked(False)
                del blocker
        elif changed_box.isChecked() and changed_value != exclusive_value:
            for checkbox in checkboxes:
                if checkbox.property("value") == exclusive_value:
                    blocker = QSignalBlocker(checkbox)
                    checkbox.setChecked(False)
                    del blocker
                    break
        elif not any(box.isChecked() for box in checkboxes):
            for checkbox in checkboxes:
                if checkbox.property("value") == exclusive_value:
                    blocker = QSignalBlocker(checkbox)
                    checkbox.setChecked(True)
                    del blocker
                    break

        self.update_summary()

    def show_preview_dialog(self) -> None:
        self.update_summary()
        dialog = QDialog(self)
        dialog.setWindowTitle("JSON 预览")
        dialog.resize(700, 620)

        layout = QVBoxLayout(dialog)
        preview = QPlainTextEdit()
        preview.setReadOnly(True)
        preview.setPlainText(self.preview_cache)
        preview.setStyleSheet("font-family: Menlo, Monaco, monospace; font-size: 13px;")
        layout.addWidget(preview)

        close_button = QPushButton("关闭")
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
        self.apply_default_selections()

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

        missing_labels: list[str] = []
        for key in self.required_question_keys:
            group = self.single_groups.get(key)
            if group is not None and group.checkedButton() is None:
                missing_labels.append(self.question_labels[key])

        if missing_labels:
            QMessageBox.warning(self, "必填项未完成", f"请先完成这些题目：{', '.join(missing_labels)}")
            return

        payload = self.collect_annotation()
        json_path = self.current_json_path()
        if not json_path:
            return

        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        QMessageBox.information(self, "提交成功", f"已生成：{json_path}")


def main() -> None:
    app = QApplication(sys.argv)
    window = AnnotationWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
