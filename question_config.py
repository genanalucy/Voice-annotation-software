QUESTION_SECTIONS = [
    {
        "title": "模块一：环境与声学特征（提取物理特征 X1）",
        "questions": [
            {
                "key": "scene_type",
                "label": "录音场景",
                "type": "single",
                "options": [
                    {"label": "录音棚/极静", "value": "Studio"},
                    {"label": "室内安静-寝室/办公室", "value": "Indoor-Quiet"},
                    {"label": "室内嘈杂-食堂/走廊", "value": "Indoor-Noisy"},
                    {"label": "室外安静-公园/阳台", "value": "Outdoor-Quiet"},
                    {"label": "室外嘈杂-马路/操场", "value": "Outdoor-Noisy"},
                ],
            },
            {
                "key": "noise_type",
                "label": "噪声类型",
                "type": "multi",
                "options": [
                    {"label": "无明显噪声", "value": "None"},
                    {"label": "持续底噪-风扇/电流", "value": "Continuous"},
                    {"label": "突发噪声-关门/掉落", "value": "Impulse"},
                    {"label": "背景人声-他人说话", "value": "Babble"},
                    {"label": "自然风噪", "value": "Wind"},
                ],
            },
            {
                "key": "reverb_level",
                "label": "混响程度",
                "type": "single",
                "options": [
                    {"label": "无明显混响-干音", "value": "Dry"},
                    {"label": "轻微混响-普通房间", "value": "Slight"},
                    {"label": "严重混响-空旷大厅", "value": "Severe"},
                ],
            },
            {
                "key": "device_distort",
                "label": "硬件失真",
                "type": "multi",
                "options": [
                    {"label": "正常", "value": "Normal"},
                    {"label": "电流麦/炸麦", "value": "Electric"},
                    {"label": "声音发闷-设备太远", "value": "Muffled"},
                    {"label": "爆音截幅-电平过大", "value": "Clipping"},
                ],
            },
            {
                "key": "snr_feeling",
                "label": "信噪比听感",
                "type": "single",
                "options": [
                    {"label": "极好-人声极清晰", "value": "Excellent"},
                    {"label": "良好-有底噪不影响", "value": "Good"},
                    {"label": "较差-需仔细辨认", "value": "Poor"},
                    {"label": "极差-无法听清", "value": "Terrible"},
                ],
            },
        ],
    },
    {
        "title": "模块二：说话人与语言状态（提取语义/风格特征 X2）",
        "questions": [
            {
                "key": "speaker_gender",
                "label": "性别预估",
                "type": "single",
                "options": [
                    {"label": "男", "value": "Male"},
                    {"label": "女", "value": "Female"},
                    {"label": "无法分辨", "value": "Unknown"},
                ],
            },
            {
                "key": "speech_speed",
                "label": "发音语速",
                "type": "single",
                "options": [
                    {"label": "极快", "value": "Very-Fast"},
                    {"label": "偏快", "value": "Fast"},
                    {"label": "正常", "value": "Normal"},
                    {"label": "偏慢/字正腔圆", "value": "Slow"},
                ],
            },
            {
                "key": "articulation",
                "label": "发音清晰度",
                "type": "single",
                "options": [
                    {"label": "吐字清晰", "value": "Clear"},
                    {"label": "略带口音", "value": "Accented"},
                    {"label": "含糊吞音", "value": "Mumbled"},
                ],
            },
            {
                "key": "speech_style",
                "label": "语言状态",
                "type": "single",
                "options": [
                    {"label": "机械朗读/生硬", "value": "Reading"},
                    {"label": "自然对话/闲聊", "value": "Conversational"},
                    {"label": "带情绪-笑/激动", "value": "Emotional"},
                ],
            },
        ],
    },
    {
        "title": "模块三：终极目标标签（目标变量 Target Y）",
        "questions": [
            {
                "key": "final_decision",
                "label": "综合处理建议",
                "type": "single",
                "options": [
                    {"label": "1. 完美可用", "value": "完美可用"},
                    {"label": "2. 带噪可用", "value": "带噪可用"},
                    {"label": "3. 需要重新切分", "value": "需要重新切分"},
                    {"label": "4. 废弃", "value": "废弃"},
                ],
            }
        ],
    },
]

REMARK_KEY = "remark"

