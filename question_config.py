QUESTION_SECTIONS = [
    {
        "title": "第一阶",
        "questions": [
            {
                "key": "noise_clarity",
                "label": "底噪与清晰度",
                "type": "single",
                "default": "良好",
                "options": [
                    {"label": "极好 声音很干净，背景安静", "value": "极好"},
                    {"label": "良好 有点沙沙声，但不影响听清人声", "value": "良好"},
                    {"label": "较差 杂音很大，得竖起耳朵努力听", "value": "较差"},
                    {"label": "极差 杂音完全盖过人声，彻底没法用", "value": "极差"},
                ],
            },
            {
                "key": "reverb_feeling",
                "label": "房间回声与空旷感",
                "type": "single",
                "default": "轻微回声",
                "options": [
                    {"label": "无回声 声音很干，像在被窝或小卧室里说话", "value": "无回声"},
                    {"label": "轻微回声 像在普通大教室或空客厅，有一点点回音", "value": "轻微回声"},
                    {"label": "严重回声 像在地下车库或大澡堂，声音拖尾很长", "value": "严重回声"},
                ],
            },
            {
                "key": "noise_type",
                "label": "异常噪声类型",
                "type": "multi",
                "default": ["无明显噪声"],
                "exclusive_value": "无明显噪声",
                "options": [
                    {"label": "无明显噪声 背景一直很平稳", "value": "无明显噪声"},
                    {"label": "突发杂音 突然有咳嗽、关门、敲桌子、掉东西声", "value": "突发杂音"},
                    {"label": "背景人声 旁边有其他人在说话或有电视声", "value": "背景人声"},
                    {"label": "持续风噪/电流 一直有呼呼风声或滋滋啦啦的电流声", "value": "持续风噪/电流"},
                    {"label": "自然环境音 有明显的鸟叫、虫鸣、狗吠、车流声等", "value": "自然环境音"},
                ],
            },
            {
                "key": "device_distort",
                "label": "麦克风失真",
                "type": "multi",
                "default": ["正常无故障"],
                "exclusive_value": "正常无故障",
                "options": [
                    {"label": "正常无故障 声音健康自然", "value": "正常无故障"},
                    {"label": "炸麦/破音 声音太大导致刺耳、劈了", "value": "炸麦/破音"},
                    {"label": "声音发闷 像隔着东西捂着嘴，或者离麦克风太远", "value": "声音发闷"},
                ],
            },
            {
                "key": "voice_volume",
                "label": "人声音量感",
                "type": "single",
                "default": "音量正常",
                "options": [
                    {"label": "音量正常 不费力就能听清", "value": "音量正常"},
                    {"label": "声音极小 人声太弱，需要把电脑音量开得非常大才能听见", "value": "声音极小"},
                    {"label": "忽大忽小 同一个人在一句话里，声音突然变大又突然变小，极不稳定", "value": "忽大忽小"},
                ],
            },
            {
                "key": "emotion_state",
                "label": "精神与情绪状态",
                "type": "single",
                "default": "平静自然",
                "options": [
                    {"label": "平静自然 正常念稿子的状态", "value": "平静自然"},
                    {"label": "紧张/拘束 声音发紧、发抖、放不开", "value": "紧张/拘束"},
                    {"label": "疲惫/敷衍 念得没力气，尾音往下掉，感觉想快点结束", "value": "疲惫/敷衍"},
                    {"label": "积极/愉悦 声音明亮，有活力", "value": "积极/愉悦"},
                ],
            },
            {
                "key": "articulation",
                "label": "吐字清晰度",
                "type": "single",
                "default": "吐字清晰",
                "options": [
                    {"label": "吐字清晰 每个字都咬得很清楚", "value": "吐字清晰"},
                    {"label": "轻微含糊 嘴巴不太张得开，但能听懂词", "value": "轻微含糊"},
                    {"label": "严重吞音 嘴里像含着东西，糊在一起听不清念了啥", "value": "严重吞音"},
                ],
            },
            {
                "key": "pronunciation_standard",
                "label": "语音标准度与规范性",
                "type": "multi",
                "default": ["发音标准"],
                "exclusive_value": "发音标准",
                "options": [
                    {"label": "发音标准", "value": "发音标准"},
                    {"label": "轻微口音 腔调稍有偏差，带地方味或普通话感", "value": "轻微口音"},
                    {"label": "声调不准 音高起伏与标准调值不符，或出现错读", "value": "声调不准"},
                ],
            },
            {
                "key": "speech_style",
                "label": "发音风格",
                "type": "single",
                "default": "自然朗读",
                "options": [
                    {"label": "自然朗读 像新闻播音或讲故事，有正常起伏", "value": "自然朗读"},
                    {"label": "机械棒读 毫无感情，像机器人一个字一个字往外蹦", "value": "机械棒读"},
                    {"label": "教学式拖音 故意一字一顿、严重拉长字音，非常不自然", "value": "教学式拖音"},
                    {"label": "闲聊口语 像在跟人日常聊天一样放松", "value": "闲聊口语"},
                ],
            },
            {
                "key": "speech_speed",
                "label": "整体语速",
                "type": "single",
                "default": "正常适中",
                "options": [
                    {"label": "正常适中 舒缓自然", "value": "正常适中"},
                    {"label": "明显偏快 像在赶时间", "value": "明显偏快"},
                    {"label": "极度拖沓/水时长 故意放慢速度，字与字之间隔得很开", "value": "极度拖沓/水时长"},
                ],
            },
            {
                "key": "pause_status",
                "label": "异常停顿与留白",
                "type": "single",
                "default": "紧凑无多余空白",
                "options": [
                    {"label": "紧凑无多余空白 节奏紧凑，没有多余的废时间", "value": "紧凑无多余空白"},
                    {"label": "句中发呆/死寂 一句话中间，出现了极度不自然的长时间停顿", "value": "句中发呆/死寂"},
                    {"label": "头尾留白冗长 话是完整的，但在开始前或结束后空了好几秒没声音", "value": "头尾留白冗长"},
                    {"label": "头尾和句中都有长静音 录音极其松散", "value": "头尾和句中都有长静音"},
                ],
            },
            {
                "key": "fluency",
                "label": "朗读流畅度",
                "type": "single",
                "default": "流利顺畅",
                "options": [
                    {"label": "流利顺畅 一口气顺畅读完", "value": "流利顺畅"},
                    {"label": "结巴/字词重复 卡壳了，或者某个字读了两遍", "value": "结巴/字词重复"},
                    {"label": "口误后自我修正 读错了，自己又停下来重新读对了一遍", "value": "口误后自我修正"},
                ],
            },
        ],
    }
]

REMARK_KEY = "audio_description"
