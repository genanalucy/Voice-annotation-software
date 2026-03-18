# 语音标注软件

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

## 打包

### macOS

```bash
chmod +x build_mac.sh
./build_mac.sh
```

输出位置：

- `dist/语音标注软件.app`

### Windows

在 Windows 电脑上进入项目目录后运行：

```bat
build_windows.bat
```

输出位置：

- `dist/audio-annotation-tool/audio-annotation-tool.exe`

## 功能

- 支持批量读取音频文件夹中的 `wma`、`m4a`、`mp3`、`wav`、`flac` 等格式
- 顶部显示当前音频名称、播放进度和上一条/下一条/暂停/继续播放
- 左侧为问题勾选区，支持单选和多选
- 右侧实时汇总当前已选结果
- 底部可填写备注，并支持重做和提交
- 提交后会在当前目录的 `json/` 文件夹生成 `音频名.json`
- 如果 `json/音频名.json` 已存在，切换到该音频时会自动回填之前的标注

## 自定义题目

题目定义在 `question_config.py` 中：

- `type="single"` 表示单选
- `type="multi"` 表示多选
- `label` 是界面显示名
- `value` 是写入 JSON 的值

可以直接按你的业务需求增删问题和选项。
