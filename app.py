import streamlit as st
import json
import os
import random
from datetime import datetime

st.set_page_config(
    page_title="baguaingjing",
    page_icon="☯",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

os.makedirs(DATA_DIR, exist_ok=True)


TRIGRAMS = {
    "乾": {
        "symbol": "☰",
        "lines": [1, 1, 1],
        "nature": "天",
        "meaning": "刚健、创造、主动",
        "desc": "乾卦象征天，常用来表示创造力、进取心与领导性。"
    },
    "兑": {
        "symbol": "☱",
        "lines": [1, 1, 0],
        "nature": "泽",
        "meaning": "喜悦、交流、和悦",
        "desc": "兑卦象征泽，强调表达、沟通、愉悦与互动。"
    },
    "离": {
        "symbol": "☲",
        "lines": [1, 0, 1],
        "nature": "火",
        "meaning": "光明、依附、明辨",
        "desc": "离卦象征火，常联系到光明、认知、判断与文明。"
    },
    "震": {
        "symbol": "☳",
        "lines": [1, 0, 0],
        "nature": "雷",
        "meaning": "发动、惊醒、开端",
        "desc": "震卦象征雷，强调行动、启动与变化的开端。"
    },
    "巽": {
        "symbol": "☴",
        "lines": [0, 1, 1],
        "nature": "风",
        "meaning": "进入、渗透、柔顺",
        "desc": "巽卦象征风，也可联系木，强调渐进影响与柔和进入。"
    },
    "坎": {
        "symbol": "☵",
        "lines": [0, 1, 0],
        "nature": "水",
        "meaning": "险陷、流动、智慧",
        "desc": "坎卦象征水，常联系困难、流动、谨慎与应变能力。"
    },
    "艮": {
        "symbol": "☶",
        "lines": [0, 0, 1],
        "nature": "山",
        "meaning": "止、界限、沉静",
        "desc": "艮卦象征山，强调停止、节制、边界与反思。"
    },
    "坤": {
        "symbol": "☷",
        "lines": [0, 0, 0],
        "nature": "地",
        "meaning": "柔顺、承载、包容",
        "desc": "坤卦象征地，强调承载、配合、滋养与稳定。"
    }
}


HEXAGRAMS = [
    {"no": 1, "name": "乾", "upper": "乾", "lower": "乾", "summary": "元亨利贞，象征创造与刚健。"},
    {"no": 2, "name": "坤", "upper": "坤", "lower": "坤", "summary": "厚德载物，象征承载与包容。"},
    {"no": 3, "name": "屯", "upper": "坎", "lower": "震", "summary": "万事开头难，重在建立秩序。"},
    {"no": 4, "name": "蒙", "upper": "艮", "lower": "坎", "summary": "启蒙求知，强调教育与学习。"},
    {"no": 5, "name": "需", "upper": "坎", "lower": "乾", "summary": "等待时机，强调准备与耐心。"},
    {"no": 6, "name": "讼", "upper": "乾", "lower": "坎", "summary": "争议与辨析，提醒审慎处理冲突。"},
    {"no": 7, "name": "师", "upper": "坤", "lower": "坎", "summary": "组织与纪律，强调群体协作。"},
    {"no": 8, "name": "比", "upper": "坎", "lower": "坤", "summary": "亲比合作，重视关系与团结。"},
    {"no": 9, "name": "小畜", "upper": "巽", "lower": "乾", "summary": "小有积蓄，宜渐进推进。"},
    {"no": 10, "name": "履", "upper": "乾", "lower": "兑", "summary": "履行规范，重视礼与分寸。"},
    {"no": 11, "name": "泰", "upper": "坤", "lower": "乾", "summary": "通泰和顺，象征顺畅与协调。"},
    {"no": 12, "name": "否", "upper": "乾", "lower": "坤", "summary": "闭塞不通，提醒调整结构。"},
    {"no": 13, "name": "同人", "upper": "乾", "lower": "离", "summary": "与人协作，强调共识与合作。"},
    {"no": 14, "name": "大有", "upper": "离", "lower": "乾", "summary": "丰盛充实，重在守成与明辨。"},
    {"no": 15, "name": "谦", "upper": "坤", "lower": "艮", "summary": "谦逊有节，利于长久发展。"},
    {"no": 16, "name": "豫", "upper": "震", "lower": "坤", "summary": "喜悦奋发，但需防松散。"},
    {"no": 17, "name": "随", "upper": "兑", "lower": "震", "summary": "随顺而动，强调适应与跟进。"},
    {"no": 18, "name": "蛊", "upper": "艮", "lower": "巽", "summary": "整顿积弊，重在修正与治理。"},
    {"no": 19, "name": "临", "upper": "坤", "lower": "兑", "summary": "临事而治，重视责任与接近。"},
    {"no": 20, "name": "观", "upper": "巽", "lower": "坤", "summary": "观察反思，强调审视与体察。"},
    {"no": 21, "name": "噬嗑", "upper": "离", "lower": "震", "summary": "明辨与执行并重，处理阻碍。"},
    {"no": 22, "name": "贲", "upper": "艮", "lower": "离", "summary": "文饰与形式，提醒内外平衡。"},
    {"no": 23, "name": "剥", "upper": "艮", "lower": "坤", "summary": "剥落衰减，宜守正待时。"},
    {"no": 24, "name": "复", "upper": "坤", "lower": "震", "summary": "返回起点，意味着重启与修复。"},
    {"no": 25, "name": "无妄", "upper": "乾", "lower": "震", "summary": "自然真实，强调不妄为。"},
    {"no": 26, "name": "大畜", "upper": "艮", "lower": "乾", "summary": "积蓄力量，宜厚积薄发。"},
    {"no": 27, "name": "颐", "upper": "艮", "lower": "震", "summary": "养正其本，强调滋养与言行。"},
    {"no": 28, "name": "大过", "upper": "兑", "lower": "巽", "summary": "承压过重，需调整支撑结构。"},
    {"no": 29, "name": "坎", "upper": "坎", "lower": "坎", "summary": "重险之中，重在谨慎与智慧。"},
    {"no": 30, "name": "离", "upper": "离", "lower": "离", "summary": "光明相继，强调认知与文明。"},
    {"no": 31, "name": "咸", "upper": "兑", "lower": "艮", "summary": "感应相通，强调互动与影响。"},
    {"no": 32, "name": "恒", "upper": "震", "lower": "巽", "summary": "持久有常，强调稳定与坚持。"},
    {"no": 33, "name": "遁", "upper": "乾", "lower": "艮", "summary": "适时退避，也是一种智慧。"},
    {"no": 34, "name": "大壮", "upper": "震", "lower": "乾", "summary": "力量增长，宜守正不躁进。"},
    {"no": 35, "name": "晋", "upper": "离", "lower": "坤", "summary": "前进上升，强调光明与进展。"},
    {"no": 36, "name": "明夷", "upper": "坤", "lower": "离", "summary": "光明受伤，宜内守与审势。"},
    {"no": 37, "name": "家人", "upper": "巽", "lower": "离", "summary": "家内秩序，强调责任与角色。"},
    {"no": 38, "name": "睽", "upper": "离", "lower": "兑", "summary": "差异与背离，重在求同存异。"},
    {"no": 39, "name": "蹇", "upper": "坎", "lower": "艮", "summary": "行进艰难，宜求助与调整。"},
    {"no": 40, "name": "解", "upper": "震", "lower": "坎", "summary": "缓解释放，适合解除压力。"},
    {"no": 41, "name": "损", "upper": "艮", "lower": "兑", "summary": "有所减损，以求整体平衡。"},
    {"no": 42, "name": "益", "upper": "巽", "lower": "震", "summary": "增益发展，重在有益于整体。"},
    {"no": 43, "name": "夬", "upper": "兑", "lower": "乾", "summary": "决断行动，但须防偏激。"},
    {"no": 44, "name": "姤", "upper": "乾", "lower": "巽", "summary": "相遇之机，需辨别轻重。"},
    {"no": 45, "name": "萃", "upper": "兑", "lower": "坤", "summary": "会聚集合，利于凝聚资源。"},
    {"no": 46, "name": "升", "upper": "坤", "lower": "巽", "summary": "逐步上升，重在积累与耐心。"},
    {"no": 47, "name": "困", "upper": "兑", "lower": "坎", "summary": "处困之时，重在守志。"},
    {"no": 48, "name": "井", "upper": "坎", "lower": "巽", "summary": "井养众人，强调基础资源。"},
    {"no": 49, "name": "革", "upper": "兑", "lower": "离", "summary": "改革变更，需把握时机。"},
    {"no": 50, "name": "鼎", "upper": "离", "lower": "巽", "summary": "器物更新，象征文化与转化。"},
    {"no": 51, "name": "震", "upper": "震", "lower": "震", "summary": "震动惊醒，推动新的开始。"},
    {"no": 52, "name": "艮", "upper": "艮", "lower": "艮", "summary": "止而后定，强调静与界限。"},
    {"no": 53, "name": "渐", "upper": "巽", "lower": "艮", "summary": "循序渐进，贵在稳步前行。"},
    {"no": 54, "name": "归妹", "upper": "震", "lower": "兑", "summary": "关系安排，提醒辨位与分寸。"},
    {"no": 55, "name": "丰", "upper": "震", "lower": "离", "summary": "丰盛明亮，亦需防过满。"},
    {"no": 56, "name": "旅", "upper": "离", "lower": "艮", "summary": "旅途变动，宜谨慎与自持。"},
    {"no": 57, "name": "巽", "upper": "巽", "lower": "巽", "summary": "柔顺深入，强调渗透与影响。"},
    {"no": 58, "name": "兑", "upper": "兑", "lower": "兑", "summary": "喜悦交流，贵在真诚沟通。"},
    {"no": 59, "name": "涣", "upper": "巽", "lower": "坎", "summary": "涣散之后，重在重新凝聚。"},
    {"no": 60, "name": "节", "upper": "坎", "lower": "兑", "summary": "节制有度，强调规则与边界。"},
    {"no": 61, "name": "中孚", "upper": "巽", "lower": "兑", "summary": "诚信感通，重视真实与信任。"},
    {"no": 62, "name": "小过", "upper": "震", "lower": "艮", "summary": "小事可行，大事宜慎。"},
    {"no": 63, "name": "既济", "upper": "坎", "lower": "离", "summary": "事情初成，仍需保持谨慎。"},
    {"no": 64, "name": "未济", "upper": "离", "lower": "坎", "summary": "尚未完成，强调继续调整。"}
]


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def trigram_lines_to_text(lines):
    result = []
    for line in lines:
        if line == 1:
            result.append("──────")
        else:
            result.append("──  ──")
    return "\n".join(result[::-1])


def hexagram_lines(upper, lower):
    return TRIGRAMS[lower]["lines"] + TRIGRAMS[upper]["lines"]


def lines_to_display(lines):
    arr = []
    for v in lines[::-1]:
        arr.append("──────" if v == 1 else "──  ──")
    return "\n".join(arr)


def find_hexagram(upper, lower):
    for h in HEXAGRAMS:
        if h["upper"] == upper and h["lower"] == lower:
            return h
    return None


def transform_hexagram(lines, moving_line):
    changed = lines[:]
    idx = moving_line - 1
    changed[idx] = 0 if changed[idx] == 1 else 1
    return changed


def lines_to_trigram_name(lines3):
    for name, info in TRIGRAMS.items():
        if info["lines"] == lines3:
            return name
    return None


def changed_hexagram_from_move(upper, lower, moving_line):
    original = hexagram_lines(upper, lower)
    changed = transform_hexagram(original, moving_line)
    lower_changed = changed[:3]
    upper_changed = changed[3:]
    lower_name = lines_to_trigram_name(lower_changed)
    upper_name = lines_to_trigram_name(upper_changed)
    result_hex = find_hexagram(upper_name, lower_name)
    return original, changed, upper_name, lower_name, result_hex


def add_history_record(title):
    if "history" not in st.session_state:
        st.session_state.history = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.insert(0, f"{ts} - {title}")
    st.session_state.history = st.session_state.history[:20]


def render_home():
    add_history_record("浏览：首页")
    st.title("☯ baguaingjing")
    st.subheader("易经八卦互动学习应用")

    st.info("本项目用于文化与学习用途，帮助理解易经、八卦与六十四卦的基本结构，不构成确定性预测或专业建议。")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
### 项目简介
`baguaingjing` 是一个面向学习者的中文互动应用，内容聚焦于：
- 易经基础概念
- 八卦与六十四卦结构
- 变卦的基本演示
- 互动测验与学习笔记

本应用强调文化理解、历史背景与结构化学习，不把易经包装成绝对化的结论工具。
        """)

    with col2:
        daily = random.choice(HEXAGRAMS)
        st.markdown("### 今日一卦")
        st.write(f"**第 {daily['no']} 卦：{daily['name']}**")
        st.write(f"上卦：{daily['upper']}　下卦：{daily['lower']}")
        st.write(daily["summary"])

    st.markdown("### 最近学习记录")
    history = st.session_state.get("history", [])
    if history:
        for item in history[:8]:
            st.write(f"- {item}")
    else:
        st.write("目前还没有学习记录。")


def render_basics():
    add_history_record("浏览：易经基础")
    st.title("易经基础")

    st.markdown("""
### 阴阳
阴阳是中国传统思想中的基本范畴，可理解为事物中相对、互补、流动变化的两个方面。  
在卦象中，阳爻通常用实线表示，阴爻通常用断线表示。

### 八卦
八卦由三个爻组成，共有八种基本组合。  
两个三爻卦上下相叠，形成六爻卦，即六十四卦的基础。

### 六十四卦
六十四卦并不是孤立的符号集合，而是由八卦两两组合构成的结构系统。  
学习时可先理解“卦象结构”，再理解“名称与含义”。

### 学习建议
建议先学会八卦名称、自然象征与基本意义，再进入六十四卦和变卦。
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("阴阳两类爻", "2")
    col2.metric("八卦", "8")
    col3.metric("六十四卦", "64")


def render_trigrams():
    add_history_record("浏览：八卦图谱")
    st.title("八卦图谱")

    selected = st.selectbox("选择一个八卦", list(TRIGRAMS.keys()))
    info = TRIGRAMS[selected]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"## {selected} {info['symbol']}")
        st.code(trigram_lines_to_text(info["lines"]))
    with col2:
        st.write(f"**自然象征：** {info['nature']}")
        st.write(f"**关键词：** {info['meaning']}")
        st.write(f"**说明：** {info['desc']}")

    st.markdown("### 八卦总览")
    cols = st.columns(4)
    items = list(TRIGRAMS.items())
    for i, (name, item) in enumerate(items):
        with cols[i % 4]:
            st.markdown(f"**{name} {item['symbol']}**")
            st.code(trigram_lines_to_text(item["lines"]))
            st.caption(f"{item['nature']}｜{item['meaning']}")


def render_hexagrams():
    add_history_record("浏览：六十四卦")
    st.title("六十四卦")

    search_mode = st.radio("查询方式", ["按编号", "按卦名", "按上下卦"], horizontal=True)

    result = None

    if search_mode == "按编号":
        no = st.number_input("输入卦序号", min_value=1, max_value=64, value=1, step=1)
        result = next((h for h in HEXAGRAMS if h["no"] == no), None)

    elif search_mode == "按卦名":
        name = st.selectbox("选择卦名", [h["name"] for h in HEXAGRAMS])
        result = next((h for h in HEXAGRAMS if h["name"] == name), None)

    else:
        upper = st.selectbox("选择上卦", list(TRIGRAMS.keys()), key="hex_upper")
        lower = st.selectbox("选择下卦", list(TRIGRAMS.keys()), key="hex_lower")
        result = find_hexagram(upper, lower)

    if result:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"## 第 {result['no']} 卦：{result['name']}")
            lines = hexagram_lines(result["upper"], result["lower"])
            st.code(lines_to_display(lines))
        with col2:
            st.write(f"**上卦：** {result['upper']}（{TRIGRAMS[result['upper']]['nature']}）")
            st.write(f"**下卦：** {result['lower']}（{TRIGRAMS[result['lower']]['nature']}）")
            st.write(f"**简释：** {result['summary']}")


def render_change_demo():
    add_history_record("浏览：变卦演示")
    st.title("变卦演示")

    upper = st.selectbox("选择上卦", list(TRIGRAMS.keys()), key="change_upper")
    lower = st.selectbox("选择下卦", list(TRIGRAMS.keys()), key="change_lower")
    moving_line = st.slider("选择动爻（1 为初爻，6 为上爻）", 1, 6, 1)

    original_hex = find_hexagram(upper, lower)
    original_lines, changed_lines, upper_name, lower_name, changed_hex = changed_hexagram_from_move(upper, lower, moving_line)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 本卦")
        if original_hex:
            st.write(f"**第 {original_hex['no']} 卦：{original_hex['name']}**")
        st.code(lines_to_display(original_lines))

    with col2:
        st.markdown("### 之卦")
        if changed_hex:
            st.write(f"**第 {changed_hex['no']} 卦：{changed_hex['name']}**")
            st.write(f"上卦：{upper_name}　下卦：{lower_name}")
            st.write(changed_hex["summary"])
        else:
            st.write("暂未找到对应之卦。")
        st.code(lines_to_display(changed_lines))

    st.caption("说明：这里的演示用于帮助理解卦象变化的结构，不代表确定性的现实判断。")


def render_content_pages():
    add_history_record("浏览：历史 / 理论 / 实践")
    st.title("历史 / 理论 / 实践")

    tab1, tab2, tab3 = st.tabs(["历史", "理论", "实践"])

    with tab1:
        st.markdown("""
### 历史
《易经》长期被视为中国传统经典之一，而八卦则是其最具代表性的符号系统之一。  
在历史发展中，易学不仅影响占筮传统，也深刻影响中国哲学、文化表达、政治语言和日常思维方式。  
现代学习者在接触易经时，更适合把它理解为一种古代思想与符号体系，而不是简单地把它等同于神秘结论。
        """)

    with tab2:
        st.markdown("""
### 理论
八卦由三个阴阳爻组合而成，分别对应不同的自然象征与抽象意义。  
两个八卦上下叠加后构成六爻卦，形成六十四种组合，这种结构体现了“变化”“关系”“位置”和“时机”的思想。  
学习理论时，建议先理解卦象结构、阴阳变化和上下关系，再阅读卦名与释义。
        """)

    with tab3:
        st.markdown("""
### 实践
现代人学习易经八卦，可以把它用于文化理解、语言分析、哲学思考和结构化反思。  
例如，在阅读古籍、分析传统观念、理解象征表达时，八卦提供了一套很有代表性的观察框架。  
本项目强调的是学习用途、思考工具和文化素养，而不是迷信化应用。
        """)


def init_quiz():
    if "quiz" not in st.session_state:
        h = random.choice(HEXAGRAMS)
        st.session_state.quiz = {
            "question": h,
            "options": random.sample([x["name"] for x in HEXAGRAMS], 4),
            "answered": False,
            "result": ""
        }
        if h["name"] not in st.session_state.quiz["options"]:
            st.session_state.quiz["options"][0] = h["name"]
            random.shuffle(st.session_state.quiz["options"])


def reset_quiz():
    if "quiz" in st.session_state:
        del st.session_state["quiz"]
    init_quiz()


def render_quiz():
    add_history_record("浏览：互动测验")
    st.title("互动测验")

    init_quiz()
    q = st.session_state.quiz
    h = q["question"]

    st.write("请根据上下卦判断卦名。")
    st.write(f"上卦：**{h['upper']}**　下卦：**{h['lower']}**")
    st.code(lines_to_display(hexagram_lines(h["upper"], h["lower"])))

    choice = st.radio("请选择正确卦名", q["options"], key="quiz_choice")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("提交答案"):
            q["answered"] = True
            if choice == h["name"]:
                q["result"] = f"回答正确：第 {h['no']} 卦 {h['name']}。{h['summary']}"
            else:
                q["result"] = f"回答错误。正确答案是：第 {h['no']} 卦 {h['name']}。{h['summary']}"

    with col2:
        if st.button("换一题"):
            reset_quiz()
            st.rerun()

    if q["answered"]:
        st.success(q["result"])


def render_notes():
    add_history_record("浏览：学习笔记")
    st.title("学习笔记")

    notes = load_notes()

    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("标题")
        related = st.text_input("关联卦名或主题")
        content = st.text_area("写下你的学习心得")
        submitted = st.form_submit_button("保存笔记")

    if submitted:
        if title.strip() and content.strip():
            record = {
                "title": title.strip(),
                "related": related.strip(),
                "content": content.strip(),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            notes.insert(0, record)
            save_notes(notes)
            st.success("笔记已保存。")
        else:
            st.warning("请至少填写标题和内容。")

    st.markdown("### 已保存笔记")
    if notes:
        for i, note in enumerate(notes[:20], start=1):
            with st.expander(f"{i}. {note['title']}｜{note['time']}"):
                st.write(f"**关联主题：** {note['related'] or '无'}")
                st.write(note["content"])
    else:
        st.write("目前还没有笔记。")


def main():
    st.sidebar.title("导航菜单")
    page = st.sidebar.radio(
        "请选择页面",
        [
            "首页",
            "易经基础",
            "八卦图谱",
            "六十四卦",
            "变卦演示",
            "历史 / 理论 / 实践",
            "互动测验",
            "学习笔记"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("baguaingjing｜易经八卦互动学习应用")
    st.sidebar.caption("用途：文化与学习，不构成确定性预测。")

    if page == "首页":
        render_home()
    elif page == "易经基础":
        render_basics()
    elif page == "八卦图谱":
        render_trigrams()
    elif page == "六十四卦":
        render_hexagrams()
    elif page == "变卦演示":
        render_change_demo()
    elif page == "历史 / 理论 / 实践":
        render_content_pages()
    elif page == "互动测验":
        render_quiz()
    elif page == "学习笔记":
        render_notes()


if __name__ == "__main__":
    main()
