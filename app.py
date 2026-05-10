import os
import json
import random
from datetime import datetime

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="易经·朱熹解卦",
    page_icon="☯",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'PingFang SC', 'Noto Sans SC', sans-serif;
    }
    .main {background: #f5f4ef;}
    .block-container {
        max-width: 820px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }
    .main-title {
        text-align: center;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        color: #1a1a1a;
        margin-bottom: 4px;
    }
    .sub-title {
        text-align: center;
        font-style: italic;
        font-size: 1rem;
        color: #888;
        margin-bottom: 18px;
    }
    .divider {
        border: none;
        border-top: 1px solid #e8e8e8;
        margin: 14px 0 18px 0;
    }
    .pill-row {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 18px 0 24px 0;
    }
    .pill-active {
        background: #1a1a1a;
        color: white;
        border-radius: 24px;
        padding: 10px 28px;
        font-size: 0.95rem;
        border: none;
        cursor: default;
    }
    .pill-inactive {
        background: #f0efeb;
        color: #888;
        border-radius: 24px;
        padding: 10px 28px;
        font-size: 0.95rem;
        border: none;
        cursor: pointer;
    }
    .rule-box {
        background: #f9f8f4;
        border-left: 4px solid #1a1a1a;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 0.95rem;
        color: #333;
    }
    .yaoci-box {
        background: #faf9f5;
        border: 1px solid #e8e7e2;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .yaoci-main { border-left: 4px solid #c0392b; }
    .yaoci-secondary { border-left: 4px solid #d4a017; }
    .guaci-box {
        background: #f0f4f0;
        border-left: 4px solid #2e7d32;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .soft-box {
        background: #faf8f2;
        border: 1px solid #ebe7dc;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
    }
    .muted {
        color: #7a7a7a;
        font-size: 0.92rem;
    }
    .stButton > button {
        border-radius: 12px;
        font-size: 1rem;
        padding: 10px 18px;
    }
    [data-testid="stTextInput"] input {
        border: none;
        border-bottom: 1.5px solid #ccc;
        border-radius: 0;
        background: transparent;
        font-size: 1rem;
        padding: 8px 4px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
YINYANG_IMAGE = os.path.join(ASSETS_DIR, "yinyang_wuxing.jpg")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

TRIGRAM_MAP = {1: "乾", 2: "兑", 3: "离", 4: "震", 5: "巽", 6: "坎", 7: "艮", 8: "坤"}

TRIGRAMS = {
    "乾": {"symbol": "☰", "lines": [1, 1, 1], "nature": "天", "meaning": "刚健、创造、主动"},
    "兑": {"symbol": "☱", "lines": [1, 1, 0], "nature": "泽", "meaning": "喜悦、交流、和悦"},
    "离": {"symbol": "☲", "lines": [1, 0, 1], "nature": "火", "meaning": "光明、依附、明辨"},
    "震": {"symbol": "☳", "lines": [1, 0, 0], "nature": "雷", "meaning": "发动、惊醒、开端"},
    "巽": {"symbol": "☴", "lines": [0, 1, 1], "nature": "风", "meaning": "进入、渗透、柔顺"},
    "坎": {"symbol": "☵", "lines": [0, 1, 0], "nature": "水", "meaning": "险陷、流动、智慧"},
    "艮": {"symbol": "☶", "lines": [0, 0, 1], "nature": "山", "meaning": "止、界限、沉静"},
    "坤": {"symbol": "☷", "lines": [0, 0, 0], "nature": "地", "meaning": "柔顺、承载、包容"},
}

HEXAGRAMS = [
    {"no": 1, "name": "乾", "upper": "乾", "lower": "乾", "summary": "元亨利贞，象征创造与刚健。", "lines": ["初九：潜龙勿用。", "九二：见龙在田，利见大人。", "九三：君子终日乾乾，夕惕若厉，无咎。", "九四：或跃在渊，无咎。", "九五：飞龙在天，利见大人。", "上九：亢龙有悔。"], "use": "用九：见群龙无首，吉。"},
    {"no": 2, "name": "坤", "upper": "坤", "lower": "坤", "summary": "厚德载物，象征承载与包容。", "lines": ["初六：履霜，坚冰至。", "六二：直、方、大，不习无不利。", "六三：含章可贞，或从王事，无成有终。", "六四：括囊，无咎无誉。", "六五：黄裳，元吉。", "上六：龙战于野，其血玄黄。"], "use": "用六：利永贞。"},
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
    {"no": 64, "name": "未济", "upper": "离", "lower": "坎", "summary": "尚未完成，强调继续调整。"},
]

HEXAGRAM_BY_NO = {h["no"]: h for h in HEXAGRAMS}
HEXAGRAM_BY_NAME = {h["name"]: h for h in HEXAGRAMS}


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def save_history_to_disk(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(history, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


def init_state():
    defaults = {
        "method": "数字起卦",
        "div_result": None,
        "coin_lines": [],
        "coin_details": [],
        "history": load_history(),
        "view": "起卦",
        "ai_result_text": "",
        "ai_result_data": None,
        "search_query": "",
        "search_pick_no": 1,
        "current_hex_in_search": 1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)


def find_hexagram(upper, lower):
    for h in HEXAGRAMS:
        if h["upper"] == upper and h["lower"] == lower:
            return h
    return HEXAGRAMS[0]


def lines_to_trigram(l3):
    for name, tri in TRIGRAMS.items():
        if tri["lines"] == l3:
            return name
    return "乾"


def hex_lines(upper, lower):
    return TRIGRAMS[lower]["lines"] + TRIGRAMS[upper]["lines"]


def get_changed_hex(upper, lower, moving):
    orig = hex_lines(upper, lower)
    chg = orig[:]
    for m in moving:
        chg[m - 1] ^= 1
    ln = lines_to_trigram(chg[:3])
    un = lines_to_trigram(chg[3:])
    return orig, chg, find_hexagram(un, ln)


def render_hex_svg(lines, moving=None, width=130):
    moving = moving or []
    line_h = 11
    gap = 8
    total_h = 6 * (line_h + gap) + 16
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}">']
    for i, (line_no, value) in enumerate(reversed(list(enumerate(lines, 1)))):
        y = 8 + i * (line_h + gap)
        is_moving = line_no in moving
        color = "#c0392b" if is_moving else "#1a1a1a"
        if value == 1:
            parts.append(f'<rect x="4" y="{y}" width="{width-8}" height="{line_h}" rx="3" fill="{color}"/>')
        else:
            half_w = (width - 18) // 2
            parts.append(f'<rect x="4" y="{y}" width="{half_w}" height="{line_h}" rx="3" fill="{color}"/>')
            parts.append(f'<rect x="{width - 4 - half_w}" y="{y}" width="{half_w}" height="{line_h}" rx="3" fill="{color}"/>')
        if is_moving:
            mark = "○" if value == 1 else "×"
            parts.append(f'<text x="{width//2}" y="{y+9}" text-anchor="middle" font-size="8" fill="#c0392b">{mark}</text>')
    parts.append('</svg>')
    return "".join(parts)


def hex_card_html(h, lines, moving=None, label=""):
    moving = moving or []
    svg = render_hex_svg(lines, moving, 120)
    upper = TRIGRAMS.get(h.get("upper", "乾"), {})
    lower = TRIGRAMS.get(h.get("lower", "乾"), {})
    moving_text = ""
    if moving:
        moving_text = f'<div style="font-size:0.75rem;color:#c0392b;margin-top:4px;">动爻：{"、".join([f"第{m}爻" for m in sorted(moving)])}</div>'
    return f"""
    <div style="background:#f5f4ef;border-radius:16px;padding:20px 16px;text-align:center; border:1px solid #ece7db;">
      <div style="font-size:0.75rem;color:#aaa;margin-bottom:4px;">{label}</div>
      <div style="font-size:1.20rem;font-weight:bold;color:#1a1a1a;">第 {h['no']} 卦　{h['name']}</div>
      <div style="margin:12px auto;width:fit-content;">{svg}</div>
      <div style="font-size:0.78rem;color:#888;">
        {upper.get('symbol','')} {h.get('upper','')}（{upper.get('nature','')}）／{lower.get('symbol','')} {h.get('lower','')}（{lower.get('nature','')}）
      </div>
      <div style="font-size:0.88rem;color:#555;margin-top:8px;">{h['summary']}</div>
      {moving_text}
    </div>
    """


def load_asset_image():
    return YINYANG_IMAGE if os.path.exists(YINYANG_IMAGE) else None


def render_cover_image():
    image_path = load_asset_image()
    if image_path:
        st.image(image_path, use_container_width=True)
    else:
        st.info("尚未找到图片文件，请将图片放到 assets/yinyang_wuxing.jpg")


def zhuxi(orig, chg, moving):
    count = len(moving)
    sorted_moving = sorted(moving)
    guaci = orig.get("summary", "")

    def orig_line_text(n):
        lines = orig.get("lines", [])
        return lines[n - 1] if 1 <= n <= len(lines) else f"第{n}爻：此版本未内置该卦完整爻辞，请自行对读原文。"

    def chg_line_text(n):
        lines = chg.get("lines", []) if chg else []
        return lines[n - 1] if 1 <= n <= len(lines) else f"第{n}爻：此版本未内置该卦完整爻辞，请自行对读原文。"

    if count == 0:
        return "六爻不变", f"以本卦卦辞为主：{orig['summary']}", guaci, "", ""
    if count == 1:
        line = orig_line_text(sorted_moving[0])
        return "一爻变，以本卦变爻爻辞为主", line, guaci, line, ""
    if count == 2:
        upper_line = orig_line_text(max(sorted_moving))
        lower_line = orig_line_text(min(sorted_moving))
        return "两爻变，以上位变爻爻辞为主", upper_line, guaci, upper_line, lower_line
    if count == 3:
        return "三爻变，兼看本卦与之卦卦辞", f"本卦：{orig['summary']}　之卦：{chg['summary'] if chg else '未知'}", guaci, "", ""
    if count == 4:
        unchanged = [i for i in range(1, 7) if i not in sorted_moving]
        line = chg_line_text(min(unchanged))
        return "四爻变，以之卦下位不变爻爻辞为主", line, guaci, line, ""
    if count == 5:
        unchanged = [i for i in range(1, 7) if i not in sorted_moving]
        line = chg_line_text(unchanged[0] if unchanged else 1)
        return "五爻变，以之卦唯一不变爻爻辞为主", line, guaci, line, ""
    if count == 6:
        if orig["name"] == "乾":
            line = orig.get("use", "用九：见群龙无首，吉。")
            return "六爻皆变（乾）", line, guaci, line, ""
        if orig["name"] == "坤":
            line = orig.get("use", "用六：利永贞。")
            return "六爻皆变（坤）", line, guaci, line, ""
        line = chg["summary"] if chg else "未知"
        return "六爻皆变，以之卦卦辞为主", line, guaci, line, ""
    return "—", "", guaci, "", ""


def coin_to_line(three):
    heads = sum(three)
    if heads == 3:
        return 1, True, "老阳 ○"
    if heads == 2:
        return 1, False, "少阳"
    if heads == 1:
        return 0, False, "少阴"
    return 0, True, "老阴 ×"


def num_to_trigram(n):
    remainder = n % 8
    return TRIGRAM_MAP[remainder if remainder else 8], (remainder if remainder else 8)


def moving_from_sum(total):
    remainder = total % 6
    return remainder if remainder else 6


def save_history(record):
    history = st.session_state.history
    history.insert(0, record)
    st.session_state.history = history[:100]
    save_history_to_disk(st.session_state.history)


def delete_history(idx):
    history = st.session_state.history
    if 0 <= idx < len(history):
        history.pop(idx)
        st.session_state.history = history
        save_history_to_disk(history)


def build_result_record(question, method, orig_hex, chg_hex, orig_lines, chg_lines, moving, rule_name, rule_text, guaci, main_yaoci, secondary_yaoci, note=""):
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question.strip(),
        "method": method,
        "orig_hex_name": orig_hex["name"],
        "orig_hex_no": orig_hex["no"],
        "chg_hex_name": chg_hex["name"] if chg_hex else "",
        "chg_hex_no": chg_hex["no"] if chg_hex else "",
        "moving": moving,
        "rule_name": rule_name,
        "rule_text": rule_text,
        "guaci": guaci,
        "main_yaoci": main_yaoci,
        "secondary_yaoci": secondary_yaoci,
        "note": note,
        "orig_hex": orig_hex,
        "chg_hex": chg_hex,
        "orig_l": orig_lines,
        "chg_l": chg_lines,
    }


def ai_structured(question, orig, chg, moving, rule_name, rule_text, guaci, main_yaoci, secondary_yaoci):
    api_key = get_secret("OPENROUTER_API_KEY", "")
    if not api_key:
        return None, "未配置 OPENROUTER_API_KEY"

    model = get_secret("MODEL_NAME", "google/gemini-2.5-flash-lite")
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    sec = f"\n辅助参考爻辞：{secondary_yaoci}" if secondary_yaoci else ""
    prompt = f"""
你是一名中文易经学习助手。请根据以下信息，生成结构化解读。

问题：{question}
本卦：第{orig['no']}卦 {orig['name']}（{orig['summary']}）
之卦：{chg['name'] + '（' + chg['summary'] + '）' if chg else '无'}
动爻：{moving if moving else '无'}
朱熹法取用：{rule_name} — {rule_text}
卦辞：{guaci}
主断爻辞：{main_yaoci}{sec}

要求：
- 不神秘化
- 不做确定性承诺
- 用语自然、克制、清晰
- 结合起卦问题，不要泛泛而谈
- 引用朱熹法说明为何取此爻辞
"""
    schema = {
        "name": "iching_interpretation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "result_overview": {"type": "string"},
                "zhuxi_method": {"type": "string"},
                "interpretation": {"type": "string"},
                "action_advice": {"type": "string"},
            },
            "required": ["result_overview", "zhuxi_method", "interpretation", "action_advice"],
            "additionalProperties": False,
        },
    }
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个清晰、克制的中文助手。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_schema", "json_schema": schema},
            temperature=0.5,
        )
        data = json.loads(resp.choices[0].message.content)
        return data, ""
    except Exception as e:
        return None, str(e)


def reset_coin():
    st.session_state.coin_lines = []
    st.session_state.coin_details = []
    st.session_state.div_result = None
    st.session_state.ai_result_text = ""
    st.session_state.ai_result_data = None


def reset_ai_result():
    st.session_state.ai_result_text = ""
    st.session_state.ai_result_data = None


def show_ai_result():
    ai_data = st.session_state.ai_result_data
    if not ai_data:
        return
    with st.expander("起卦结果概览", expanded=True):
        st.write(ai_data.get("result_overview", ""))
    with st.expander("朱熹法取用说明", expanded=True):
        st.write(ai_data.get("zhuxi_method", ""))
    with st.expander("对问题的解读", expanded=True):
        st.write(ai_data.get("interpretation", ""))
    with st.expander("可参考的行动方向", expanded=True):
        st.write(ai_data.get("action_advice", ""))
    with st.expander("复制全文", expanded=False):
        st.code(st.session_state.ai_result_text, language="text")


def show_result_block(res, question_text):
    orig = res["orig_hex"]
    chg = res["chg_hex"]
    moving = res["moving"]
    rule_name = res["rule_name"]
    rule_text = res["rule_text"]
    guaci = res.get("guaci", "")
    main_yaoci = res.get("main_yaoci", "")
    secondary_yaoci = res.get("secondary_yaoci", "")

    st.markdown("---")
    if res.get("note"):
        st.caption(res["note"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(hex_card_html(orig, res["orig_l"], moving, "本卦"), unsafe_allow_html=True)
    with col2:
        if chg:
            st.markdown(hex_card_html(chg, res["chg_l"], [], "之卦"), unsafe_allow_html=True)
        else:
            st.markdown('<div class="soft-box" style="text-align:center;color:#999;">无之卦</div>', unsafe_allow_html=True)

    st.markdown("### 朱熹法取用")
    st.markdown(f'<div class="rule-box"><b>{rule_name}</b><br><br>{rule_text}</div>', unsafe_allow_html=True)

    st.markdown("### 卦辞与爻辞")
    with st.expander("📜 本卦卦辞", expanded=True):
        st.markdown(f'<div class="guaci-box"><b>{orig["name"]}卦：</b><br>{guaci}</div>', unsafe_allow_html=True)
    if main_yaoci:
        with st.expander("🔴 主断爻辞", expanded=True):
            st.markdown(f'<div class="yaoci-box yaoci-main"><b>{main_yaoci}</b></div>', unsafe_allow_html=True)
    if secondary_yaoci:
        with st.expander("🟡 辅助爻辞", expanded=False):
            st.markdown(f'<div class="yaoci-box yaoci-secondary"><b>{secondary_yaoci}</b></div>', unsafe_allow_html=True)

    st.markdown("### AI 解读")
    if not question_text.strip():
        st.caption("请先输入所问之事，再生成解读。")
        show_ai_result()
        return

    if st.button("生成结构化解读", type="primary", use_container_width=True):
        with st.spinner("解读中..."):
            ai_data, err = ai_structured(question_text, orig, chg, moving, rule_name, rule_text, guaci, main_yaoci, secondary_yaoci)
        if err:
            st.error(err)
        else:
            st.session_state.ai_result_data = ai_data
            st.session_state.ai_result_text = (
                f"【起卦结果概览】\n{ai_data['result_overview']}\n\n"
                f"【朱熹法取用说明】\n{ai_data['zhuxi_method']}\n\n"
                f"【对问题的解读】\n{ai_data['interpretation']}\n\n"
                f"【可参考的行动方向】\n{ai_data['action_advice']}"
            )

    show_ai_result()


def render_header(title, subtitle, show_image=False):
    if show_image:
        render_cover_image()
        st.markdown("")
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def cast_by_number(question, upper_n, lower_n, move_n):
    upper_name, upper_rem = num_to_trigram(int(upper_n))
    lower_name, lower_rem = num_to_trigram(int(lower_n))
    moving = [moving_from_sum(int(move_n))]
    orig_hex = find_hexagram(upper_name, lower_name)
    orig_lines, chg_lines, chg_hex = get_changed_hex(upper_name, lower_name, moving)
    rule_name, rule_text, guaci, main_yaoci, secondary_yaoci = zhuxi(orig_hex, chg_hex, moving)
    note = f"上卦：{upper_name}（{int(upper_n)}÷8余{upper_rem}）　下卦：{lower_name}（{int(lower_n)}÷8余{lower_rem}）　动爻：第{moving[0]}爻"
    res = build_result_record(question, "数字起卦", orig_hex, chg_hex, orig_lines, chg_lines, moving, rule_name, rule_text, guaci, main_yaoci, secondary_yaoci, note)
    st.session_state.div_result = res
    reset_ai_result()
    save_history(res)


def finalize_coin_result(question, lines, details, method_name, note=""):
    moving = [d["line"] for d in details if d["moving"]]
    lower_name = lines_to_trigram(lines[:3])
    upper_name = lines_to_trigram(lines[3:])
    orig_hex = find_hexagram(upper_name, lower_name)
    orig_lines, chg_lines, chg_hex = get_changed_hex(upper_name, lower_name, moving)
    rule_name, rule_text, guaci, main_yaoci, secondary_yaoci = zhuxi(orig_hex, chg_hex, moving)
    res = build_result_record(question, method_name, orig_hex, chg_hex, orig_lines, chg_lines, moving, rule_name, rule_text, guaci, main_yaoci, secondary_yaoci, note)
    st.session_state.div_result = res
    reset_ai_result()
    save_history(res)


def render_cast_page():
    render_header("易经 · 朱熹解卦", "一阴一阳之谓道", show_image=True)

    question = st.text_input(
        "",
        placeholder="在此输入所问之事（如：事业、学业）",
        label_visibility="collapsed",
        key="question_input",
    )

    center = st.columns([1.2, 1.3, 1.2])[1]
    with center:
        is_number = st.session_state.method == "数字起卦"
        st.markdown(
            f"""
            <div class="pill-row">
                <span class="{'pill-active' if is_number else 'pill-inactive'}">数字起卦</span>
                <span class="{'pill-active' if not is_number else 'pill-inactive'}">金钱起卦</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("数字起卦", use_container_width=True):
            st.session_state.method = "数字起卦"
            st.session_state.div_result = None
            reset_ai_result()
            st.rerun()
        if c2.button("金钱起卦", use_container_width=True):
            st.session_state.method = "金钱起卦"
            st.session_state.div_result = None
            reset_coin()
            st.rerun()

    if st.session_state.method == "数字起卦":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("上卦")
            upper_n = st.number_input("上卦数字", min_value=1, value=6, step=1, label_visibility="collapsed")
        with c2:
            st.caption("下卦")
            lower_n = st.number_input("下卦数字", min_value=1, value=3, step=1, label_visibility="collapsed")
        with c3:
            st.caption("变爻")
            move_n = st.number_input("变爻数字", min_value=1, value=9, step=1, label_visibility="collapsed")
        if st.button("立即占卦", type="primary", use_container_width=True):
            cast_by_number(question, upper_n, lower_n, move_n)
    else:
        mode = st.radio("金钱卦方式", ["模拟掷币", "手动录入"], horizontal=True)
        if mode == "模拟掷币":
            done = len(st.session_state.coin_lines)
            line_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
            if done < 6:
                st.markdown(
                    f"""
                    <div class="soft-box" style="text-align:center;">
                        <div style="font-size:2rem;">🪙</div>
                        <div class="muted">诚心默念，模拟六次掷币</div>
                        <div class="muted">当前：第 {done+1} 爻（{line_names[done]}）</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(int(done / 6 * 100), text=f"已投 {done} / 6 爻")
                t1, t2 = st.columns(2)
                if t1.button(f"掷出第 {done+1} 爻", type="primary", use_container_width=True):
                    toss = [random.randint(0, 1) for _ in range(3)]
                    value, moving, label = coin_to_line(toss)
                    st.session_state.coin_lines.append(value)
                    st.session_state.coin_details.append({
                        "line": done + 1,
                        "toss": toss,
                        "label": label,
                        "value": value,
                        "moving": moving,
                    })
                    st.rerun()
                if t2.button("重新起卦", use_container_width=True):
                    reset_coin()
                    st.rerun()
            if st.session_state.coin_details:
                st.markdown("### 当前结果")
                for d in st.session_state.coin_details:
                    faces = " · ".join(["正" if x == 1 else "反" for x in d["toss"]])
                    tag = "　**← 动爻**" if d["moving"] else ""
                    st.write(f"第 {d['line']} 爻：{faces}　→　{d['label']}{tag}")
            if len(st.session_state.coin_lines) == 6 and not st.session_state.div_result:
                finalize_coin_result(question, st.session_state.coin_lines, st.session_state.coin_details, "金钱起卦-模拟掷币")
        else:
            st.caption("从初爻到上爻依次输入。1=正，0=反。三枚都输完后自动判定该爻。")
            manual_rounds = []
            for i in range(1, 7):
                st.markdown(f"**第 {i} 爻**")
                cols = st.columns(3)
                toss = []
                for j in range(3):
                    toss.append(
                        cols[j].selectbox(
                            f"第{i}爻 第{j+1}枚",
                            [1, 0],
                            format_func=lambda x: "正" if x == 1 else "反",
                            key=f"manual_coin_{i}_{j}",
                        )
                    )
                manual_rounds.append(toss)
            if st.button("根据手动结果起卦", type="primary", use_container_width=True):
                lines = []
                details = []
                for i, toss in enumerate(manual_rounds, start=1):
                    value, moving, label = coin_to_line(toss)
                    lines.append(value)
                    details.append({"line": i, "toss": toss, "label": label, "value": value, "moving": moving})
                note = "；".join([f"第{d['line']}爻:{''.join(['正' if x == 1 else '反' for x in d['toss']])}->{d['label']}" for d in details])
                finalize_coin_result(question, lines, details, "金钱起卦-手动录入", note)

    if st.session_state.div_result:
        show_result_block(st.session_state.div_result, question)


def render_history_page():
    render_header("占卦历史", "保存在 data/history.json 中")
    history = st.session_state.history
    if not history:
        st.info("目前还没有历史记录。先完成一次起卦后，这里会显示。")
        return

    top1, top2 = st.columns(2)
    if top1.button("清空全部历史", use_container_width=True):
        st.session_state.history = []
        save_history_to_disk([])
        st.rerun()
    if top2.button("返回起卦", use_container_width=True):
        st.session_state.view = "起卦"
        st.rerun()

    st.markdown(f"共 {len(history)} 条记录")
    for idx, item in enumerate(history):
        title = f"{item['time']}｜{item['method']}｜第{item['orig_hex_no']}卦 {item['orig_hex_name']}"
        if item.get("chg_hex_name"):
            title += f" → 第{item['chg_hex_no']}卦 {item['chg_hex_name']}"
        with st.expander(title, expanded=(idx == 0)):
            d1, d2 = st.columns([1, 3])
            if d1.button("删除此条", key=f"del_{idx}", use_container_width=True):
                delete_history(idx)
                st.rerun()
            if d2.button("载入为当前结果", key=f"load_{idx}", use_container_width=True):
                st.session_state.div_result = item
                reset_ai_result()
                st.session_state.view = "起卦"
                st.rerun()
            st.markdown(f"**问题：** {item['question'] or '未填写'}")
            st.markdown(f"**动爻：** {'、'.join([f'第{m}爻' for m in item['moving']]) if item['moving'] else '无'}")
            st.markdown(f"**朱熹法：** {item['rule_name']}")
            st.markdown(f"**取用说明：** {item['rule_text']}")
            if item.get("guaci"):
                st.markdown(f"**卦辞：** {item['guaci']}")
            if item.get("main_yaoci"):
                st.markdown(f"**主断爻辞：** {item['main_yaoci']}")
            if item.get("secondary_yaoci"):
                st.markdown(f"**辅助爻辞：** {item['secondary_yaoci']}")
            if item.get("note"):
                st.caption(item["note"])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(hex_card_html(item["orig_hex"], item["orig_l"], item["moving"], "本卦"), unsafe_allow_html=True)
            with c2:
                if item["chg_hex"]:
                    st.markdown(hex_card_html(item["chg_hex"], item["chg_l"], [], "之卦"), unsafe_allow_html=True)


def search_hexagrams(query):
    query = query.strip()
    if not query:
        return []
    results = []
    for h in HEXAGRAMS:
        blob = f"{h['no']} {h['name']} {h['upper']} {h['lower']} {h['summary']}"
        if query in blob:
            results.append(h)
    return results


def display_hexagram_detail(h):
    lines = hex_lines(h["upper"], h["lower"])
    st.markdown(hex_card_html(h, lines, [], "卦象"), unsafe_allow_html=True)

    upper = TRIGRAMS[h["upper"]]
    lower = TRIGRAMS[h["lower"]]

    with st.expander("基础说明", expanded=True):
        st.markdown(f"**卦号：** 第 {h['no']} 卦")
        st.markdown(f"**卦名：** {h['name']}")
        st.markdown(f"**上卦：** {upper['symbol']} {h['upper']}（{upper['nature']}）— {upper['meaning']}")
        st.markdown(f"**下卦：** {lower['symbol']} {h['lower']}（{lower['nature']}）— {lower['meaning']}")
        st.markdown(f"**简述：** {h['summary']}")

    with st.expander("卦辞 / 解读摘要", expanded=True):
        st.markdown(f'<div class="guaci-box"><b>{h["name"]}卦：</b><br>{h["summary"]}</div>', unsafe_allow_html=True)

    lines_data = h.get("lines", [])
    if lines_data:
        with st.expander("六爻爻辞", expanded=True):
            for item in lines_data:
                st.markdown(f'<div class="yaoci-box"><b>{item}</b></div>', unsafe_allow_html=True)
    else:
        with st.expander("六爻爻辞", expanded=False):
            st.info("此增强版保留了 64 卦查询，但当前仅内置部分卦的完整爻辞。其余卦可先查看卦象结构与摘要。")

    use_text = h.get("use", "")
    if use_text:
        with st.expander("用辞", expanded=True):
            st.markdown(f'<div class="yaoci-box yaoci-main"><b>{use_text}</b></div>', unsafe_allow_html=True)



def render_hexagram_grid():
    st.markdown("### 六十四卦总览")
    cols = st.columns(4)
    for idx, h in enumerate(HEXAGRAMS):
        with cols[idx % 4]:
            if st.button(f"{h['no']:02d} {h['name']}", key=f"hex_btn_{h['no']}", use_container_width=True):
                st.session_state.current_hex_in_search = h["no"]



def render_search_page():
    render_header("64卦搜寻", "搜寻个别卦、上下卦组合、六十四卦总览", show_image=True)

    tab1, tab2, tab3 = st.tabs(["搜寻个别卦", "上下卦组合", "全部卦列表"])

    with tab1:
        q1, q2 = st.columns([2, 1])
        with q1:
            query = st.text_input("输入卦名、卦号、上卦、下卦或关键字", value=st.session_state.search_query, key="search_query_input")
        with q2:
            pick_no = st.selectbox("快速选择卦号", [h["no"] for h in HEXAGRAMS], index=max(0, st.session_state.current_hex_in_search - 1))

        b1, b2 = st.columns(2)
        if b1.button("搜寻", type="primary", use_container_width=True):
            st.session_state.search_query = query.strip()
        if b2.button("打开所选号", use_container_width=True):
            st.session_state.current_hex_in_search = pick_no

        if st.session_state.search_query:
            results = search_hexagrams(st.session_state.search_query)
            if results:
                st.success(f"找到 {len(results)} 个结果")
                for h in results:
                    with st.expander(f"第 {h['no']} 卦 {h['name']}", expanded=(h['no'] == results[0]['no'])):
                        display_hexagram_detail(h)
            else:
                st.warning("未找到匹配结果。可尝试输入卦名、数字、上卦或下卦。")

        st.markdown("### 当前选中卦")
        current = HEXAGRAM_BY_NO.get(st.session_state.current_hex_in_search, HEXAGRAMS[0])
        display_hexagram_detail(current)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            upper_sel = st.selectbox("上卦", list(TRIGRAMS.keys()), key="search_upper")
        with c2:
            lower_sel = st.selectbox("下卦", list(TRIGRAMS.keys()), key="search_lower")
        if st.button("查询组合", type="primary", use_container_width=True):
            st.session_state.current_hex_in_search = find_hexagram(upper_sel, lower_sel)["no"]
        target = HEXAGRAM_BY_NO[st.session_state.current_hex_in_search]
        st.success(f"组合结果：第 {target['no']} 卦 {target['name']}")
        display_hexagram_detail(target)

    with tab3:
        render_hexagram_grid()
        st.markdown("### 已选中卦")
        display_hexagram_detail(HEXAGRAM_BY_NO[st.session_state.current_hex_in_search])


def render_sidebar():
    st.sidebar.title("易经八卦")
    nav = st.sidebar.radio("页面", ["起卦", "历史记录", "64卦搜寻"], index=["起卦", "历史记录", "64卦搜寻"].index(st.session_state.view))
    st.session_state.view = nav

    st.sidebar.markdown("---")
    st.sidebar.caption("已加入 sidebar 的“64卦搜寻”。")
    st.sidebar.caption("已加入 assets/yinyang_wuxing.jpg 自动读取显示。")
    st.sidebar.caption("已修正 AI 结果重新展开时可能未定义的问题。")
    st.sidebar.caption("历史记录保存在 data/history.json。")

    image_path = load_asset_image()
    if image_path:
        st.sidebar.image(image_path, use_container_width=True)
    else:
        st.sidebar.info("缺少图片：assets/yinyang_wuxing.jpg")


def main():
    init_state()
    render_sidebar()
    if st.session_state.view == "起卦":
        render_cast_page()
    elif st.session_state.view == "历史记录":
        render_history_page()
    else:
        render_search_page()


if __name__ == "__main__":
    main()
