import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


st.set_page_config(
    page_title="易经·朱熹解卦",
    page_icon="☯",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    }
    .main {
        background: #f5f4ef;
    }
    .block-container {
        max-width: 860px;
        padding-top: 1.3rem;
        padding-bottom: 3rem;
    }
    .main-title {
        text-align: center;
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        color: #1a1a1a;
        margin-bottom: 4px;
    }
    .sub-title {
        text-align: center;
        font-style: italic;
        font-size: 0.98rem;
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
    .yaoci-main {
        border-left: 4px solid #c0392b;
    }
    .yaoci-secondary {
        border-left: 4px solid #d4a017;
    }
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
    .tiny {
        color: #999;
        font-size: 0.82rem;
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
FULL_HEX_FILE = os.path.join(DATA_DIR, "hexagrams_full.json")
YINYANG_IMAGE = os.path.join(ASSETS_DIR, "yinyang_wuxing.jpg")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


TRIGRAM_MAP = {
    1: "乾",
    2: "兑",
    3: "离",
    4: "震",
    5: "巽",
    6: "坎",
    7: "艮",
    8: "坤",
}

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


BASE_HEXAGRAMS = [
    {"no": 1, "name": "乾", "upper": "乾", "lower": "乾", "summary": "元亨利贞。", "lines": ["初九：潜龙勿用。", "九二：见龙在田，利见大人。", "九三：君子终日乾乾，夕惕若厉，无咎。", "九四：或跃在渊，无咎。", "九五：飞龙在天，利见大人。", "上九：亢龙有悔。"], "use": "用九：见群龙无首，吉。"},
    {"no": 2, "name": "坤", "upper": "坤", "lower": "坤", "summary": "元亨，利牝马之贞。", "lines": ["初六：履霜，坚冰至。", "六二：直方大，不习无不利。", "六三：含章可贞。或从王事，无成有终。", "六四：括囊，无咎无誉。", "六五：黄裳，元吉。", "上六：龙战于野，其血玄黄。"], "use": "用六：利永贞。"},
    {"no": 3, "name": "屯", "upper": "坎", "lower": "震", "summary": "元亨利贞。勿用有攸往，利建侯。", "lines": ["初九：磐桓，利居贞，利建侯。", "六二：屯如邅如，乘马班如。匪寇，婚媾；女子贞不字，十年乃字。", "六三：即鹿无虞，惟入于林中；君子几，不如舍，往吝。", "六四：乘马班如，求婚媾，往吉，无不利。", "九五：屯其膏，小贞吉，大贞凶。", "上六：乘马班如，泣血涟如。"]},
    {"no": 4, "name": "蒙", "upper": "艮", "lower": "坎", "summary": "亨。匪我求童蒙，童蒙求我。初筮告，再三渎，渎则不告。利贞。", "lines": ["初六：发蒙，利用刑人，用说桎梏；以往吝。", "九二：包蒙吉；纳妇吉；子克家。", "六三：勿用取女；见金夫，不有躬，无攸利。", "六四：困蒙，吝。", "六五：童蒙，吉。", "上九：击蒙；不利为寇，利御寇。"]},
    {"no": 5, "name": "需", "upper": "坎", "lower": "乾", "summary": "有孚，光亨，贞吉。利涉大川。"},
    {"no": 6, "name": "讼", "upper": "乾", "lower": "坎", "summary": "有孚，窒惕，中吉，终凶。利见大人，不利涉大川。"},
    {"no": 7, "name": "师", "upper": "坤", "lower": "坎", "summary": "贞，丈人吉，无咎。"},
    {"no": 8, "name": "比", "upper": "坎", "lower": "坤", "summary": "吉。原筮，元永贞，无咎。不宁方来，后夫凶。"},
    {"no": 9, "name": "小畜", "upper": "巽", "lower": "乾", "summary": "亨。密云不雨，自我西郊。"},
    {"no": 10, "name": "履", "upper": "乾", "lower": "兑", "summary": "履虎尾，不咥人，亨。"},
    {"no": 11, "name": "泰", "upper": "坤", "lower": "乾", "summary": "小往大来，吉亨。"},
    {"no": 12, "name": "否", "upper": "乾", "lower": "坤", "summary": "否之匪人，不利君子贞，大往小来。"},
    {"no": 13, "name": "同人", "upper": "乾", "lower": "离", "summary": "同人于野，亨。利涉大川，利君子贞。"},
    {"no": 14, "name": "大有", "upper": "离", "lower": "乾", "summary": "元亨。"},
    {"no": 15, "name": "谦", "upper": "坤", "lower": "艮", "summary": "亨，君子有终。"},
    {"no": 16, "name": "豫", "upper": "震", "lower": "坤", "summary": "利建侯行师。"},
    {"no": 17, "name": "随", "upper": "兑", "lower": "震", "summary": "元亨利贞，无咎。"},
    {"no": 18, "name": "蛊", "upper": "艮", "lower": "巽", "summary": "元亨。利涉大川。先甲三日，后甲三日。"},
    {"no": 19, "name": "临", "upper": "坤", "lower": "兑", "summary": "元亨利贞。至于八月有凶。"},
    {"no": 20, "name": "观", "upper": "巽", "lower": "坤", "summary": "盥而不荐，有孚颙若。"},
    {"no": 21, "name": "噬嗑", "upper": "离", "lower": "震", "summary": "亨。利用狱。"},
    {"no": 22, "name": "贲", "upper": "艮", "lower": "离", "summary": "亨。小利有攸往。"},
    {"no": 23, "name": "剥", "upper": "艮", "lower": "坤", "summary": "不利有攸往。"},
    {"no": 24, "name": "复", "upper": "坤", "lower": "震", "summary": "亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。"},
    {"no": 25, "name": "无妄", "upper": "乾", "lower": "震", "summary": "元亨利贞。其匪正有眚，不利有攸往。"},
    {"no": 26, "name": "大畜", "upper": "艮", "lower": "乾", "summary": "利贞。不家食吉，利涉大川。"},
    {"no": 27, "name": "颐", "upper": "艮", "lower": "震", "summary": "贞吉。观颐，自求口实。"},
    {"no": 28, "name": "大过", "upper": "兑", "lower": "巽", "summary": "栋桡，利有攸往，亨。"},
    {"no": 29, "name": "坎", "upper": "坎", "lower": "坎", "summary": "习坎，有孚，维心亨，行有尚。"},
    {"no": 30, "name": "离", "upper": "离", "lower": "离", "summary": "利贞，亨。畜牝牛，吉。"},
    {"no": 31, "name": "咸", "upper": "兑", "lower": "艮", "summary": "亨，利贞，取女吉。"},
    {"no": 32, "name": "恒", "upper": "震", "lower": "巽", "summary": "亨，无咎，利贞，利有攸往。"},
    {"no": 33, "name": "遁", "upper": "乾", "lower": "艮", "summary": "亨，小利贞。"},
    {"no": 34, "name": "大壮", "upper": "震", "lower": "乾", "summary": "利贞。"},
    {"no": 35, "name": "晋", "upper": "离", "lower": "坤", "summary": "康侯用锡马蕃庶，昼日三接。"},
    {"no": 36, "name": "明夷", "upper": "坤", "lower": "离", "summary": "利艰贞。"},
    {"no": 37, "name": "家人", "upper": "巽", "lower": "离", "summary": "利女贞。"},
    {"no": 38, "name": "睽", "upper": "离", "lower": "兑", "summary": "小事吉。"},
    {"no": 39, "name": "蹇", "upper": "坎", "lower": "艮", "summary": "利西南，不利东北。利见大人，贞吉。"},
    {"no": 40, "name": "解", "upper": "震", "lower": "坎", "summary": "利西南。无所往，其来复吉。有攸往，夙吉。"},
    {"no": 41, "name": "损", "upper": "艮", "lower": "兑", "summary": "有孚，元吉，无咎，可贞，利有攸往。曷之用？二簋可用享。"},
    {"no": 42, "name": "益", "upper": "巽", "lower": "震", "summary": "利有攸往，利涉大川。"},
    {"no": 43, "name": "夬", "upper": "兑", "lower": "乾", "summary": "扬于王庭，孚号有厉。告自邑，不利即戎，利有攸往。"},
    {"no": 44, "name": "姤", "upper": "乾", "lower": "巽", "summary": "女壮，勿用取女。"},
    {"no": 45, "name": "萃", "upper": "兑", "lower": "坤", "summary": "亨。王假有庙。利见大人，亨，利贞。用大牲吉，利有攸往。"},
    {"no": 46, "name": "升", "upper": "坤", "lower": "巽", "summary": "元亨，用见大人，勿恤，南征吉。"},
    {"no": 47, "name": "困", "upper": "兑", "lower": "坎", "summary": "亨，贞，大人吉，无咎。有言不信。"},
    {"no": 48, "name": "井", "upper": "坎", "lower": "巽", "summary": "改邑不改井，无丧无得。往来井井。汔至亦未繘井，羸其瓶，凶。"},
    {"no": 49, "name": "革", "upper": "兑", "lower": "离", "summary": "己日乃孚。元亨利贞。悔亡。"},
    {"no": 50, "name": "鼎", "upper": "离", "lower": "巽", "summary": "元吉，亨。"},
    {"no": 51, "name": "震", "upper": "震", "lower": "震", "summary": "亨。震来虩虩，笑言哑哑。震惊百里，不丧匕鬯。"},
    {"no": 52, "name": "艮", "upper": "艮", "lower": "艮", "summary": "艮其背，不获其身，行其庭，不见其人，无咎。"},
    {"no": 53, "name": "渐", "upper": "巽", "lower": "艮", "summary": "女归吉，利贞。"},
    {"no": 54, "name": "归妹", "upper": "震", "lower": "兑", "summary": "征凶，无攸利。"},
    {"no": 55, "name": "丰", "upper": "震", "lower": "离", "summary": "亨。王假之。勿忧，宜日中。"},
    {"no": 56, "name": "旅", "upper": "离", "lower": "艮", "summary": "小亨，旅贞吉。"},
    {"no": 57, "name": "巽", "upper": "巽", "lower": "巽", "summary": "小亨。利有攸往，利见大人。"},
    {"no": 58, "name": "兑", "upper": "兑", "lower": "兑", "summary": "亨，利贞。"},
    {"no": 59, "name": "涣", "upper": "巽", "lower": "坎", "summary": "亨。王假有庙。利涉大川，利贞。"},
    {"no": 60, "name": "节", "upper": "坎", "lower": "兑", "summary": "亨。苦节不可贞。"},
    {"no": 61, "name": "中孚", "upper": "巽", "lower": "兑", "summary": "豚鱼吉，利涉大川，利贞。"},
    {"no": 62, "name": "小过", "upper": "震", "lower": "艮", "summary": "亨，利贞。可小事，不可大事。飞鸟遗之音，不宜上宜下，大吉。"},
    {"no": 63, "name": "既济", "upper": "坎", "lower": "离", "summary": "亨，小利贞。初吉终乱。"},
    {"no": 64, "name": "未济", "upper": "离", "lower": "坎", "summary": "亨。小狐汔济，濡其尾，无攸利。"},
]


def load_history() -> List[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_history_to_disk(history: List[dict]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(history, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)


def normalize_hexagram_item(item: dict) -> dict:
    required = ["no", "name", "upper", "lower", "summary"]
    for k in required:
        if k not in item:
            raise ValueError(f"缺少字段: {k}")

    no = int(item["no"])
    upper = str(item["upper"])
    lower = str(item["lower"])

    if upper not in TRIGRAMS or lower not in TRIGRAMS:
        raise ValueError(f"上下卦非法: {item.get('name', no)}")

    lines = item.get("lines", [])
    if lines and (not isinstance(lines, list) or len(lines) != 6):
        raise ValueError(f"lines 必须为空或正好 6 条: {item.get('name', no)}")

    return {
        "no": no,
        "name": str(item["name"]),
        "upper": upper,
        "lower": lower,
        "summary": str(item["summary"]),
        "lines": [str(x) for x in lines] if lines else [],
        "use": str(item.get("use", "")),
    }


def merge_base_and_full(full_data: List[dict]) -> List[dict]:
    base_map = {h["no"]: h for h in BASE_HEXAGRAMS}
    for item in full_data:
        base_map[item["no"]] = {**base_map.get(item["no"], {}), **item}
    result = [base_map[i] for i in range(1, 65)]
    return result


def load_hexagrams() -> List[dict]:
    if os.path.exists(FULL_HEX_FILE):
        try:
            with open(FULL_HEX_FILE, "r", encoding="utf-8") as fh:
                full_data = json.load(fh)
            if isinstance(full_data, list):
                normalized = [normalize_hexagram_item(x) for x in full_data]
                nos = sorted([x["no"] for x in normalized])
                if nos == list(range(1, 65)):
                    return merge_base_and_full(normalized)
        except Exception:
            pass
    return BASE_HEXAGRAMS


def init_state() -> None:
    defaults = {
        "method": "数字起卦",
        "view": "起卦",
        "div_result": None,
        "coin_lines": [],
        "coin_details": [],
        "history": load_history(),
        "ai_result_text": "",
        "ai_result_data": None,
        "search_query": "",
        "current_hex_in_search": 1,
        "hexagrams_data": load_hexagrams(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_hexagrams() -> List[dict]:
    return st.session_state.hexagrams_data


def hex_by_no() -> Dict[int, dict]:
    return {h["no"]: h for h in get_hexagrams()}


def hex_by_name() -> Dict[str, dict]:
    return {h["name"]: h for h in get_hexagrams()}


def find_hexagram(upper: str, lower: str) -> dict:
    for h in get_hexagrams():
        if h["upper"] == upper and h["lower"] == lower:
            return h
    return get_hexagrams()[0]


def lines_to_trigram(lines3: List[int]) -> str:
    for name, tri in TRIGRAMS.items():
        if tri["lines"] == lines3:
            return name
    return "乾"


def hex_lines(upper: str, lower: str) -> List[int]:
    return TRIGRAMS[lower]["lines"] + TRIGRAMS[upper]["lines"]


def get_changed_hex(upper: str, lower: str, moving: List[int]) -> Tuple[List[int], List[int], dict]:
    origin = hex_lines(upper, lower)
    changed = origin[:]
    for m in moving:
        if 1 <= m <= 6:
            changed[m - 1] ^= 1
    lower_name = lines_to_trigram(changed[:3])
    upper_name = lines_to_trigram(changed[3:])
    return origin, changed, find_hexagram(upper_name, lower_name)


def render_hex_svg(lines: List[int], moving: Optional[List[int]] = None, width: int = 130) -> str:
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
            parts.append(f'<rect x="4" y="{y}" width="{width - 8}" height="{line_h}" rx="3" fill="{color}"/>')
        else:
            half_w = (width - 18) // 2
            parts.append(f'<rect x="4" y="{y}" width="{half_w}" height="{line_h}" rx="3" fill="{color}"/>')
            parts.append(f'<rect x="{width - 4 - half_w}" y="{y}" width="{half_w}" height="{line_h}" rx="3" fill="{color}"/>')

        if is_moving:
            mark = "○" if value == 1 else "×"
            parts.append(f'<text x="{width // 2}" y="{y + 9}" text-anchor="middle" font-size="8" fill="#c0392b">{mark}</text>')

    parts.append("</svg>")
    return "".join(parts)


def hex_card_html(h: dict, lines: List[int], moving: Optional[List[int]] = None, label: str = "") -> str:
    moving = moving or []
    upper = TRIGRAMS[h["upper"]]
    lower = TRIGRAMS[h["lower"]]
    svg = render_hex_svg(lines, moving, 120)

    moving_text = ""
    if moving:
        moving_text = f'<div style="font-size:0.75rem;color:#c0392b;margin-top:4px;">动爻：{"、".join([f"第{m}爻" for m in sorted(moving)])}</div>'

    return f"""
    <div style="background:#f5f4ef;border-radius:16px;padding:20px 16px;text-align:center;border:1px solid #ece7db;">
      <div style="font-size:0.75rem;color:#aaa;margin-bottom:4px;">{label}</div>
      <div style="font-size:1.18rem;font-weight:bold;color:#1a1a1a;">第 {h['no']} 卦　{h['name']}</div>
      <div style="margin:12px auto;width:fit-content;">{svg}</div>
      <div style="font-size:0.78rem;color:#888;">
        {upper['symbol']} {h['upper']}（{upper['nature']}）／{lower['symbol']} {h['lower']}（{lower['nature']}）
      </div>
      <div style="font-size:0.88rem;color:#555;margin-top:8px;">{h['summary']}</div>
      {moving_text}
    </div>
    """


def load_asset_image() -> Optional[str]:
    return YINYANG_IMAGE if os.path.exists(YINYANG_IMAGE) else None


def render_cover_image() -> None:
    image_path = load_asset_image()
    if image_path:
        st.image(image_path, use_container_width=True)
    else:
        st.info("尚未找到图片文件，请将图片放到 assets/yinyang_wuxing.jpg")


def line_text_from_hex(h: Optional[dict], line_no: int) -> str:
    if not h:
        return f"第{line_no}爻：当前数据未提供。"
    lines = h.get("lines", [])
    if isinstance(lines, list) and len(lines) == 6 and 1 <= line_no <= 6:
        return lines[line_no - 1]
    return f"第{line_no}爻：当前数据未提供。"


def zhuxi_rule(orig: dict, changed: Optional[dict], moving: List[int]) -> Tuple[str, str, str, str, str]:
    count = len(moving)
    sorted_moving = sorted(moving)
    guaci = orig.get("summary", "")

    if count == 0:
        return "六爻不变", f"以本卦卦辞为主：{orig['summary']}", guaci, "", ""

    if count == 1:
        main = line_text_from_hex(orig, sorted_moving[0])
        return "一爻变，以本卦变爻爻辞为主", main, guaci, main, ""

    if count == 2:
        main = line_text_from_hex(orig, max(sorted_moving))
        secondary = line_text_from_hex(orig, min(sorted_moving))
        return "两爻变，以上位变爻爻辞为主", main, guaci, main, secondary

    if count == 3:
        text = f"本卦：{orig['summary']}　之卦：{changed['summary'] if changed else '未知'}"
        return "三爻变，兼看本卦与之卦卦辞", text, guaci, "", ""

    if count == 4:
        unchanged = [i for i in range(1, 7) if i not in sorted_moving]
        main = line_text_from_hex(changed, min(unchanged))
        return "四爻变，以之卦下位不变爻爻辞为主", main, guaci, main, ""

    if count == 5:
        unchanged = [i for i in range(1, 7) if i not in sorted_moving]
        main = line_text_from_hex(changed, unchanged[0] if unchanged else 1)
        return "五爻变，以之卦唯一不变爻爻辞为主", main, guaci, main, ""

    if count == 6:
        if orig["name"] == "乾":
            use_text = orig.get("use", "用九：见群龙无首，吉。")
            return "六爻皆变（乾）", use_text, guaci, use_text, ""
        if orig["name"] == "坤":
            use_text = orig.get("use", "用六：利永贞。")
            return "六爻皆变（坤）", use_text, guaci, use_text, ""
        text = changed["summary"] if changed else "未知"
        return "六爻皆变，以之卦卦辞为主", text, guaci, text, ""

    return "—", "", guaci, "", ""


def coin_to_line(three: List[int]) -> Tuple[int, bool, str]:
    heads = sum(three)
    if heads == 3:
        return 1, True, "老阳 ○"
    if heads == 2:
        return 1, False, "少阳"
    if heads == 1:
        return 0, False, "少阴"
    return 0, True, "老阴 ×"


def num_to_trigram(n: int) -> Tuple[str, int]:
    remainder = n % 8
    actual = remainder if remainder else 8
    return TRIGRAM_MAP[actual], actual


def moving_from_sum(total: int) -> int:
    remainder = total % 6
    return remainder if remainder else 6


def save_history(record: dict) -> None:
    history = st.session_state.history
    history.insert(0, record)
    st.session_state.history = history[:100]
    save_history_to_disk(st.session_state.history)


def delete_history(idx: int) -> None:
    history = st.session_state.history
    if 0 <= idx < len(history):
        history.pop(idx)
        st.session_state.history = history
        save_history_to_disk(history)


def build_result_record(
    question: str,
    method: str,
    orig_hex: dict,
    changed_hex: Optional[dict],
    orig_lines: List[int],
    changed_lines: List[int],
    moving: List[int],
    rule_name: str,
    rule_text: str,
    guaci: str,
    main_yaoci: str,
    secondary_yaoci: str,
    note: str = "",
) -> dict:
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question.strip(),
        "method": method,
        "orig_hex_name": orig_hex["name"],
        "orig_hex_no": orig_hex["no"],
        "chg_hex_name": changed_hex["name"] if changed_hex else "",
        "chg_hex_no": changed_hex["no"] if changed_hex else "",
        "moving": moving,
        "rule_name": rule_name,
        "rule_text": rule_text,
        "guaci": guaci,
        "main_yaoci": main_yaoci,
        "secondary_yaoci": secondary_yaoci,
        "note": note,
        "orig_hex": orig_hex,
        "chg_hex": changed_hex,
        "orig_l": orig_lines,
        "chg_l": changed_lines,
    }


def ai_structured(
    question: str,
    orig: dict,
    changed: Optional[dict],
    moving: List[int],
    rule_name: str,
    rule_text: str,
    guaci: str,
    main_yaoci: str,
    secondary_yaoci: str,
) -> Tuple[Optional[dict], str]:
    if OpenAI is None:
        return None, "未安装 openai 包，请先执行：pip install openai"

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
之卦：{changed['name'] + '（' + changed['summary'] + '）' if changed else '无'}
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


def reset_coin() -> None:
    st.session_state.coin_lines = []
    st.session_state.coin_details = []
    st.session_state.div_result = None
    st.session_state.ai_result_text = ""
    st.session_state.ai_result_data = None


def reset_ai_result() -> None:
    st.session_state.ai_result_text = ""
    st.session_state.ai_result_data = None


def show_ai_result() -> None:
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


def show_result_block(res: dict, question_text: str) -> None:
    orig = res["orig_hex"]
    changed = res["chg_hex"]
    moving = res["moving"]

    st.markdown("---")
    if res.get("note"):
        st.caption(res["note"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(hex_card_html(orig, res["orig_l"], moving, "本卦"), unsafe_allow_html=True)
    with c2:
        if changed:
            st.markdown(hex_card_html(changed, res["chg_l"], [], "之卦"), unsafe_allow_html=True)
        else:
            st.markdown('<div class="soft-box" style="text-align:center;color:#999;">无之卦</div>', unsafe_allow_html=True)

    st.markdown("### 朱熹法取用")
    st.markdown(f'<div class="rule-box"><b>{res["rule_name"]}</b><br><br>{res["rule_text"]}</div>', unsafe_allow_html=True)

    st.markdown("### 卦辞与爻辞")
    with st.expander("📜 本卦卦辞", expanded=True):
        st.markdown(f'<div class="guaci-box"><b>{orig["name"]}卦：</b><br>{res.get("guaci", "")}</div>', unsafe_allow_html=True)

    if res.get("main_yaoci"):
        with st.expander("🔴 主断爻辞", expanded=True):
            st.markdown(f'<div class="yaoci-box yaoci-main"><b>{res["main_yaoci"]}</b></div>', unsafe_allow_html=True)

    if res.get("secondary_yaoci"):
        with st.expander("🟡 辅助爻辞", expanded=False):
            st.markdown(f'<div class="yaoci-box yaoci-secondary"><b>{res["secondary_yaoci"]}</b></div>', unsafe_allow_html=True)

    st.markdown("### AI 解读")
    if not question_text.strip():
        st.caption("请先输入所问之事，再生成解读。")
        show_ai_result()
        return

    if st.button("生成结构化解读", type="primary", use_container_width=True):
        with st.spinner("解读中..."):
            ai_data, err = ai_structured(
                question_text,
                orig,
                changed,
                moving,
                res["rule_name"],
                res["rule_text"],
                res.get("guaci", ""),
                res.get("main_yaoci", ""),
                res.get("secondary_yaoci", ""),
            )
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


def render_header(title: str, subtitle: str, show_image: bool = False) -> None:
    if show_image:
        render_cover_image()
        st.markdown("")
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def cast_by_number(question: str, upper_n: int, lower_n: int, move_n: int) -> None:
    upper_name, upper_rem = num_to_trigram(int(upper_n))
    lower_name, lower_rem = num_to_trigram(int(lower_n))
    moving = [moving_from_sum(int(move_n))]

    orig_hex = find_hexagram(upper_name, lower_name)
    orig_lines, changed_lines, changed_hex = get_changed_hex(upper_name, lower_name, moving)
    rule_name, rule_text, guaci, main_yaoci, secondary_yaoci = zhuxi_rule(orig_hex, changed_hex, moving)

    note = f"上卦：{upper_name}（{int(upper_n)}÷8余{upper_rem}）　下卦：{lower_name}（{int(lower_n)}÷8余{lower_rem}）　动爻：第{moving[0]}爻"

    res = build_result_record(
        question,
        "数字起卦",
        orig_hex,
        changed_hex,
        orig_lines,
        changed_lines,
        moving,
        rule_name,
        rule_text,
        guaci,
        main_yaoci,
        secondary_yaoci,
        note,
    )
    st.session_state.div_result = res
    reset_ai_result()
    save_history(res)


def finalize_coin_result(question: str, lines: List[int], details: List[dict], method_name: str, note: str = "") -> None:
    moving = [d["line"] for d in details if d["moving"]]
    lower_name = lines_to_trigram(lines[:3])
    upper_name = lines_to_trigram(lines[3:])

    orig_hex = find_hexagram(upper_name, lower_name)
    orig_lines, changed_lines, changed_hex = get_changed_hex(upper_name, lower_name, moving)
    rule_name, rule_text, guaci, main_yaoci, secondary_yaoci = zhuxi_rule(orig_hex, changed_hex, moving)

    res = build_result_record(
        question,
        method_name,
        orig_hex,
        changed_hex,
        orig_lines,
        changed_lines,
        moving,
        rule_name,
        rule_text,
        guaci,
        main_yaoci,
        secondary_yaoci,
        note,
    )
    st.session_state.div_result = res
    reset_ai_result()
    save_history(res)


def render_cast_page() -> None:
    render_header("易经 · 朱熹解卦", "一阴一阳之谓道", show_image=True)

    question = st.text_input(
        "",
        placeholder="在此输入所问之事（如：事业、学业、合作、求职）",
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
                        <div class="muted">当前：第 {done + 1} 爻（{line_names[done]}）</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(int(done / 6 * 100), text=f"已投 {done} / 6 爻")

                t1, t2 = st.columns(2)
                if t1.button(f"掷出第 {done + 1} 爻", type="primary", use_container_width=True):
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
                finalize_coin_result(
                    question,
                    st.session_state.coin_lines,
                    st.session_state.coin_details,
                    "金钱起卦-模拟掷币"
                )

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
                            f"第{i}爻 第{j + 1}枚",
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
                    details.append({
                        "line": i,
                        "toss": toss,
                        "label": label,
                        "value": value,
                        "moving": moving,
                    })

                note = "；".join(
                    [f"第{d['line']}爻:{''.join(['正' if x == 1 else '反' for x in d['toss']])}->{d['label']}" for d in details]
                )
                finalize_coin_result(question, lines, details, "金钱起卦-手动录入", note)

    if st.session_state.div_result:
        show_result_block(st.session_state.div_result, question)


def render_history_page() -> None:
    render_header("占卦历史", "保存在 data/history.json 中")

    history = st.session_state.history
    if not history:
        st.info("目前还没有历史记录。先完成一次起卦后，这里会显示。")
        return

    t1, t2 = st.columns(2)
    if t1.button("清空全部历史", use_container_width=True):
        st.session_state.history = []
        save_history_to_disk([])
        st.rerun()

    if t2.button("返回起卦", use_container_width=True):
        st.session_state.view = "起卦"
        st.rerun()

    st.markdown(f"共 {len(history)} 条记录")

    for idx, item in enumerate(history):
        title = f"{item['time']}｜{item['method']}｜第{item['orig_hex_no']}卦 {item['orig_hex_name']}"
        if item.get("chg_hex_name"):
            title += f" → 第{item['chg_hex_no']}卦 {item['chg_hex_name']}"

        with st.expander(title, expanded=(idx == 0)):
            c1, c2 = st.columns([1, 3])

            if c1.button("删除此条", key=f"del_{idx}", use_container_width=True):
                delete_history(idx)
                st.rerun()

            if c2.button("载入为当前结果", key=f"load_{idx}", use_container_width=True):
                st.session_state.div_result = item
                reset_ai_result()
                st.session_state.view = "起卦"
                st.rerun()

            st.markdown(f"**问题：** {item.get('question') or '未填写'}")
            st.markdown(f"**动爻：** {'、'.join([f'第{m}爻' for m in item.get('moving', [])]) if item.get('moving') else '无'}")
            st.markdown(f"**朱熹法：** {item.get('rule_name', '')}")
            st.markdown(f"**取用说明：** {item.get('rule_text', '')}")

            if item.get("guaci"):
                st.markdown(f"**卦辞：** {item['guaci']}")
            if item.get("main_yaoci"):
                st.markdown(f"**主断爻辞：** {item['main_yaoci']}")
            if item.get("secondary_yaoci"):
                st.markdown(f"**辅助爻辞：** {item['secondary_yaoci']}")
            if item.get("note"):
                st.caption(item["note"])

            x1, x2 = st.columns(2)
            with x1:
                st.markdown(hex_card_html(item["orig_hex"], item["orig_l"], item.get("moving", []), "本卦"), unsafe_allow_html=True)
            with x2:
                if item.get("chg_hex"):
                    st.markdown(hex_card_html(item["chg_hex"], item["chg_l"], [], "之卦"), unsafe_allow_html=True)


def search_hexagrams(query: str) -> List[dict]:
    q = query.strip()
    if not q:
        return []

    results = []
    for h in get_hexagrams():
        blob = f"{h['no']} {h['name']} {h['upper']} {h['lower']} {h['summary']}"
        if q in blob:
            results.append(h)
    return results


def display_hexagram_detail(h: dict) -> None:
    lines = hex_lines(h["upper"], h["lower"])
    st.markdown(hex_card_html(h, lines, [], "卦象"), unsafe_allow_html=True)

    upper = TRIGRAMS[h["upper"]]
    lower = TRIGRAMS[h["lower"]]

    with st.expander("基础说明", expanded=True):
        st.markdown(f"**卦号：** 第 {h['no']} 卦")
        st.markdown(f"**卦名：** {h['name']}")
        st.markdown(f"**上卦：** {upper['symbol']} {h['upper']}（{upper['nature']}）— {upper['meaning']}")
        st.markdown(f"**下卦：** {lower['symbol']} {h['lower']}（{lower['nature']}）— {lower['meaning']}")
        st.markdown(f"**卦辞：** {h['summary']}")

    with st.expander("六爻爻辞", expanded=True):
        lines_data = h.get("lines", [])
        if lines_data and len(lines_data) == 6:
            for item in lines_data:
                st.markdown(f'<div class="yaoci-box"><b>{item}</b></div>', unsafe_allow_html=True)
        else:
            st.info("当前数据未提供该卦完整六爻；可后续补充 data/hexagrams_full.json。")

    use_text = h.get("use", "")
    if use_text:
        with st.expander("用辞", expanded=False):
            st.markdown(f'<div class="yaoci-box yaoci-main"><b>{use_text}</b></div>', unsafe_allow_html=True)


def render_hexagram_grid() -> None:
    st.markdown("### 六十四卦总览")
    cols = st.columns(4)
    for idx, h in enumerate(get_hexagrams()):
        with cols[idx % 4]:
            if st.button(f"{h['no']:02d} {h['name']}", key=f"hex_btn_{h['no']}", use_container_width=True):
                st.session_state.current_hex_in_search = h["no"]


def render_search_page() -> None:
    render_header("64卦搜寻", "搜寻个别卦、上下卦组合、六十四卦总览", show_image=True)

    tab1, tab2, tab3 = st.tabs(["搜寻个别卦", "上下卦组合", "全部卦列表"])

    with tab1:
        a1, a2 = st.columns([2, 1])
        with a1:
            query = st.text_input("输入卦名、卦号、上卦、下卦或关键字", value=st.session_state.search_query, key="search_query_input")
        with a2:
            pick_no = st.selectbox("快速选择卦号", [h["no"] for h in get_hexagrams()], index=max(0, st.session_state.current_hex_in_search - 1))

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
                    with st.expander(f"第 {h['no']} 卦 {h['name']}", expanded=(h["no"] == results[0]["no"])):
                        display_hexagram_detail(h)
            else:
                st.warning("未找到匹配结果。")

        st.markdown("### 当前选中卦")
        current = hex_by_no().get(st.session_state.current_hex_in_search, get_hexagrams()[0])
        display_hexagram_detail(current)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            upper_sel = st.selectbox("上卦", list(TRIGRAMS.keys()), key="search_upper")
        with c2:
            lower_sel = st.selectbox("下卦", list(TRIGRAMS.keys()), key="search_lower")

        if st.button("查询组合", type="primary", use_container_width=True):
            st.session_state.current_hex_in_search = find_hexagram(upper_sel, lower_sel)["no"]

        target = hex_by_no()[st.session_state.current_hex_in_search]
        st.success(f"组合结果：第 {target['no']} 卦 {target['name']}")
        display_hexagram_detail(target)

    with tab3:
        render_hexagram_grid()
        st.markdown("### 已选中卦")
        display_hexagram_detail(hex_by_no()[st.session_state.current_hex_in_search])


def render_sidebar() -> None:
    st.sidebar.title("易经八卦")
    nav = st.sidebar.radio(
        "页面",
        ["起卦", "历史记录", "64卦搜寻"],
        index=["起卦", "历史记录", "64卦搜寻"].index(st.session_state.view),
    )
    st.session_state.view = nav

    st.sidebar.markdown("---")
    st.sidebar.caption("图片路径：assets/yinyang_wuxing.jpg")
    st.sidebar.caption("完整数据路径：data/hexagrams_full.json")
    st.sidebar.caption("历史记录路径：data/history.json")

    image_path = load_asset_image()
    if image_path:
        st.sidebar.image(image_path, use_container_width=True)
    else:
        st.sidebar.info("缺少图片：assets/yinyang_wuxing.jpg")

    with st.sidebar.expander("完整数据说明", expanded=False):
        st.write("如放入 data/hexagrams_full.json，程序会优先读取完整 64 卦数据。")
        st.write("JSON 每项建议包含：no、name、upper、lower、summary、lines、use。")
        st.write("其中 lines 应为 6 条爻辞。")


def main() -> None:
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