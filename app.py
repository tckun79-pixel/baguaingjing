import streamlit as st
import json
import os
import random
import time
from datetime import datetime
from openai import OpenAI

try:
    from supabase import create_client
except Exception:
    create_client = None

st.set_page_config(
    page_title="易经八卦",
    page_icon="☯",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
WUXING_IMAGE = os.path.join(ASSETS_DIR, "yinyang_wuxing.jpg")
BAGUA_IMAGE = os.path.join(ASSETS_DIR, "bagua.jpeg")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

TRIGRAM_NUMBER_MAP = {
    1: "乾",
    2: "兑",
    3: "离",
    4: "震",
    5: "巽",
    6: "坎",
    7: "艮",
    8: "坤"
}

TRIGRAMS = {
    "乾": {"symbol": "☰", "lines": [1, 1, 1], "nature": "天", "meaning": "刚健、创造、主动", "desc": "乾卦象征天，常用来表示创造力、进取心与领导性。"},
    "兑": {"symbol": "☱", "lines": [1, 1, 0], "nature": "泽", "meaning": "喜悦、交流、和悦", "desc": "兑卦象征泽，强调表达、沟通、愉悦与互动。"},
    "离": {"symbol": "☲", "lines": [1, 0, 1], "nature": "火", "meaning": "光明、依附、明辨", "desc": "离卦象征火，常联系到光明、认知、判断与文明。"},
    "震": {"symbol": "☳", "lines": [1, 0, 0], "nature": "雷", "meaning": "发动、惊醒、开端", "desc": "震卦象征雷，强调行动、启动与变化的开端。"},
    "巽": {"symbol": "☴", "lines": [0, 1, 1], "nature": "风", "meaning": "进入、渗透、柔顺", "desc": "巽卦象征风，也可联系木，强调渐进影响与柔和进入。"},
    "坎": {"symbol": "☵", "lines": [0, 1, 0], "nature": "水", "meaning": "险陷、流动、智慧", "desc": "坎卦象征水，常联系困难、流动、谨慎与应变能力。"},
    "艮": {"symbol": "☶", "lines": [0, 0, 1], "nature": "山", "meaning": "止、界限、沉静", "desc": "艮卦象征山，强调停止、节制、边界与反思。"},
    "坤": {"symbol": "☷", "lines": [0, 0, 0], "nature": "地", "meaning": "柔顺、承载、包容", "desc": "坤卦象征地，强调承载、配合、滋养与稳定。"}
}

# line_texts 仅作显示占位，不是完整《周易本义》原文
HEXAGRAMS = [
    {"no": 1, "name": "乾", "upper": "乾", "lower": "乾", "summary": "元亨利贞，象征创造与刚健。",
     "line_texts": ["初九：潜龙勿用。", "九二：见龙在田，利见大人。", "九三：君子终日乾乾。", "九四：或跃在渊。", "九五：飞龙在天。", "上九：亢龙有悔。"],
     "use_text": "用九：见群龙无首，吉。"},
    {"no": 2, "name": "坤", "upper": "坤", "lower": "坤", "summary": "厚德载物，象征承载与包容。",
     "line_texts": ["初六：履霜，坚冰至。", "六二：直方大。", "六三：含章可贞。", "六四：括囊。", "六五：黄裳元吉。", "上六：龙战于野。"],
     "use_text": "用六：利永贞。"},
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

def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)

def get_supabase():
    if create_client is None:
        return None
    url = get_secret("SUPABASE_URL", "")
    key = get_secret("SUPABASE_KEY", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

def load_local_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_local_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_notes():
    supabase = get_supabase()
    if supabase:
        try:
            res = supabase.table("notes").select("*").order("created_at", desc=True).execute()
            data = res.data or []
            normalized = []
            for row in data:
                normalized.append({
                    "id": row.get("id"),
                    "title": row.get("title", ""),
                    "related": row.get("related", ""),
                    "content": row.get("content", ""),
                    "time": row.get("created_at", "")
                })
            return normalized
        except Exception:
            pass
    return load_local_notes()

def save_note(title, related, content):
    supabase = get_supabase()
    if supabase:
        payload = {
            "title": title.strip(),
            "related": related.strip(),
            "content": content.strip()
        }
        supabase.table("notes").insert(payload).execute()
        return

    notes = load_local_notes()
    record = {
        "title": title.strip(),
        "related": related.strip(),
        "content": content.strip(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    notes.insert(0, record)
    save_local_notes(notes)

def trigram_lines_to_text(lines):
    result = []
    for line in lines:
        result.append("──────" if line == 1 else "──  ──")
    return "\n".join(result[::-1])

def hexagram_lines(upper, lower):
    return TRIGRAMS[lower]["lines"] + TRIGRAMS[upper]["lines"]

def lines_to_display(lines, moving_lines=None):
    moving_lines = moving_lines or []
    arr = []
    for idx, v in enumerate(lines[::-1], start=1):
        actual_index = 7 - idx
        base = "──────" if v == 1 else "──  ──"
        if actual_index in moving_lines:
            base += "  ○动" if v == 1 else "  ×动"
        arr.append(base)
    return "\n".join(arr)

def find_hexagram(upper, lower):
    for h in HEXAGRAMS:
        if h["upper"] == upper and h["lower"] == lower:
            return h
    return None

def transform_hexagram(lines, moving_lines):
    changed = lines[:]
    for moving_line in moving_lines:
        idx = moving_line - 1
        changed[idx] = 0 if changed[idx] == 1 else 1
    return changed

def lines_to_trigram_name(lines3):
    for name, info in TRIGRAMS.items():
        if info["lines"] == lines3:
            return name
    return None

def changed_hexagram_from_moves(upper, lower, moving_lines):
    original = hexagram_lines(upper, lower)
    changed = transform_hexagram(original, moving_lines)
    lower_changed = changed[:3]
    upper_changed = changed[3:]
    lower_name = lines_to_trigram_name(lower_changed)
    upper_name = lines_to_trigram_name(upper_changed)
    result_hex = find_hexagram(upper_name, lower_name)
    return original, changed, upper_name, lower_name, result_hex

def number_to_trigram(n):
    remainder = n % 8
    if remainder == 0:
        remainder = 8
    return TRIGRAM_NUMBER_MAP[remainder], remainder

def moving_line_from_sum(total):
    remainder = total % 6
    if remainder == 0:
        remainder = 6
    return remainder

def get_hexagram_line_text(hexagram, line_no):
    texts = hexagram.get("line_texts", [])
    if 1 <= line_no <= len(texts):
        return texts[line_no - 1]
    return f"第 {line_no} 爻：当前版本未内置该爻全文，请以《周易本义》原书对读。"

def zhuxi_rule_explanation(original_hex, changed_hex, moving_lines):
    count = len(moving_lines)
    lines_sorted = sorted(moving_lines)

    if count == 0:
        return {
            "rule": "六爻不变",
            "main_text": f"以本卦卦辞为主：第 {original_hex['no']} 卦《{original_hex['name']}》。",
            "detail": f"本卦要点：{original_hex['summary']}"
        }

    if count == 1:
        line_no = lines_sorted[0]
        return {
            "rule": "一爻变",
            "main_text": f"以本卦变爻爻辞为主：第 {line_no} 爻。",
            "detail": get_hexagram_line_text(original_hex, line_no)
        }

    if count == 2:
        upper_line = max(lines_sorted)
        return {
            "rule": "两爻变",
            "main_text": f"以本卦两变爻爻辞参看，通常以上面的变爻为主：第 {upper_line} 爻。",
            "detail": get_hexagram_line_text(original_hex, upper_line)
        }

    if count == 3:
        return {
            "rule": "三爻变",
            "main_text": f"兼看本卦与之卦卦辞，以本卦为主；本卦《{original_hex['name']}》，之卦《{changed_hex['name']}》。",
            "detail": f"本卦：{original_hex['summary']}　之卦：{changed_hex['summary']}"
        }

    if count == 4:
        unchanged = [i for i in range(1, 7) if i not in lines_sorted]
        lower_unchanged = min(unchanged)
        return {
            "rule": "四爻变",
            "main_text": f"以之卦两个不变爻参看，通常以下面的不变爻为主：第 {lower_unchanged} 爻。",
            "detail": get_hexagram_line_text(changed_hex, lower_unchanged)
        }

    if count == 5:
        unchanged = [i for i in range(1, 7) if i not in lines_sorted][0]
        return {
            "rule": "五爻变",
            "main_text": f"以之卦唯一不变爻为主：第 {unchanged} 爻。",
            "detail": get_hexagram_line_text(changed_hex, unchanged)
        }

    if count == 6:
        if original_hex["name"] == "乾":
            return {
                "rule": "六爻皆变",
                "main_text": "乾卦六爻皆变，以用九为主。",
                "detail": original_hex.get("use_text", "用九：当前版本未内置全文。")
            }
        if original_hex["name"] == "坤":
            return {
                "rule": "六爻皆变",
                "main_text": "坤卦六爻皆变，以用六为主。",
                "detail": original_hex.get("use_text", "用六：当前版本未内置全文。")
            }
        return {
            "rule": "六爻皆变",
            "main_text": f"其余诸卦六爻皆变，以之卦卦辞为主：第 {changed_hex['no']} 卦《{changed_hex['name']}》。",
            "detail": changed_hex["summary"]
        }

    return {
        "rule": "未识别",
        "main_text": "未识别当前变爻情况。",
        "detail": ""
    }

def add_history_record(title):
    if "history" not in st.session_state:
        st.session_state.history = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.insert(0, f"{ts} - {title}")
    st.session_state.history = st.session_state.history[:20]

def get_openrouter_client():
    api_key = get_secret("OPENROUTER_API_KEY", "")
    if not api_key:
        return None, "未找到 OPENROUTER_API_KEY。请在 .streamlit/secrets.toml 或环境变量中设置。"
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    return client, ""

def get_model_name():
    return get_secret("MODEL_NAME", "google/gemini-2.5-flash-lite")

def ai_interpret(question, original_hex, changed_hex, moving_lines, rule_result, method_name):
    client, err = get_openrouter_client()
    if err:
        return None, err

    model_name = get_model_name()
    changed_name = changed_hex["name"] if changed_hex else "未知"

    prompt = f"""
你是一名中文易经学习助手。
本次起卦方式：{method_name}
用户问题：{question}

本卦：
- 卦名：{original_hex['name']}
- 卦序：{original_hex['no']}
- 上卦：{original_hex['upper']}
- 下卦：{original_hex['lower']}
- 简释：{original_hex['summary']}

之卦：
- 卦名：{changed_name}
- 简释：{changed_hex['summary'] if changed_hex else '暂无'}

动爻：
{moving_lines if moving_lines else '无'}

朱熹法取用：
- 规则：{rule_result['rule']}
- 主看：{rule_result['main_text']}
- 说明：{rule_result['detail']}

请按以下结构输出简体中文：
1. 起卦结果概览
2. 依朱熹法应如何取用
3. 对这个问题的解读
4. 可参考的行动方向

要求：
- 语气自然
- 重点放在理解、判断、取舍、时机、节奏
- 不要使用夸张迷信措辞
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个客观、清晰、克制的中文助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content, ""
    except Exception as e:
        return None, f"调用 AI 失败：{e}"

def simulate_number_divination(a, b):
    upper_name, upper_num = number_to_trigram(a)
    lower_name, lower_num = number_to_trigram(b)
    move = moving_line_from_sum(a + b)
    return {
        "method": "数字卦",
        "a": a,
        "b": b,
        "upper_name": upper_name,
        "lower_name": lower_name,
        "upper_num": upper_num,
        "lower_num": lower_num,
        "moving_lines": [move]
    }

def coin_to_line(three):
    heads = sum(three)
    # 这里约定：正面=1，反面=0
    # 三正=老阳(动)；两正一反=少阳；一正两反=少阴；三反=老阴(动)
    if heads == 3:
        return 1, True, "老阳"
    if heads == 2:
        return 1, False, "少阳"
    if heads == 1:
        return 0, False, "少阴"
    return 0, True, "老阴"

def simulate_coin_divination(rounds):
    lines = []
    moving_lines = []
    detail = []

    for i, toss in enumerate(rounds, start=1):
        val, moving, label = coin_to_line(toss)
        lines.append(val)
        if moving:
            moving_lines.append(i)
        faces = ["正" if x == 1 else "反" for x in toss]
        detail.append({
            "line": i,
            "faces": faces,
            "label": label,
            "value": val,
            "moving": moving
        })

    lower_lines = lines[:3]
    upper_lines = lines[3:]
    lower_name = lines_to_trigram_name(lower_lines)
    upper_name = lines_to_trigram_name(upper_lines)

    return {
        "method": "铜钱卦",
        "lines": lines,
        "detail": detail,
        "upper_name": upper_name,
        "lower_name": lower_name,
        "moving_lines": moving_lines
    }

def render_home():
    add_history_record("浏览：首页")
    st.title("☯ 易经八卦")
    st.subheader("数字卦、铜钱卦、卦象推演与学习解读")

    if os.path.exists(WUXING_IMAGE):
        st.image(WUXING_IMAGE, caption="阴阳五行图", width="stretch")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
### 项目简介
本应用聚焦于：
- 数字卦与铜钱卦
- 八卦与六十四卦结构
- 变卦推演
- 朱熹法取用说明
- AI辅助解读
- 学习笔记整理
        """)
    with col2:
        daily = random.choice(HEXAGRAMS)
        st.markdown("### 今日一卦")
        st.write(f"**第 {daily['no']} 卦：{daily['name']}**")
        st.write(f"上卦：{daily['upper']}　下卦：{daily['lower']}")
        st.write(daily["summary"])

def render_theory_image():
    add_history_record("浏览：理论图解")
    st.title("理论图解")

    st.markdown("""
### 阴阳与五行
阴阳与五行是传统文化中常见的关系框架，可用于理解变化、平衡、制约与生成。

### 八卦结构
八卦由三个爻组成，两个八卦上下组合，形成六十四卦。
    """)

    if os.path.exists(WUXING_IMAGE):
        st.image(WUXING_IMAGE, caption="阴阳五行图", width="stretch")
    else:
        st.warning("尚未找到图片文件：assets/yinyang_wuxing.jpg")

    if os.path.exists(BAGUA_IMAGE):
        st.image(BAGUA_IMAGE, caption="八卦图", width="stretch")
    else:
        st.warning("尚未找到图片文件：assets/bagua.jpeg")

def render_basics():
    add_history_record("浏览：基础说明")
    st.title("基础说明")
    st.markdown("""
### 数字卦
当前版本采用常见数字起卦法：两数分别除八取上卦、下卦，两数之和除六取动爻。

### 铜钱卦
当前版本采用三枚铜钱连掷六次的方法：三正为老阳、两正一反为少阳、一正两反为少阴、三反为老阴。老阳与老阴视为动爻。

### 朱熹法
当前版本的“取用规则”按常见朱熹法整理：依据动爻数量决定主看本卦、爻辞或之卦。
    """)

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

def show_divination_result(method_name, original_hex, changed_hex, original_lines, changed_lines, moving_lines, rule_result, extra_info=None):
    st.markdown("### 起卦结果")

    if extra_info:
        st.info(extra_info)

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**本卦：** 第 {original_hex['no']} 卦 {original_hex['name']}")
        st.write(f"上卦：{original_hex['upper']}　下卦：{original_hex['lower']}")
        st.write(original_hex["summary"])
        st.code(lines_to_display(original_lines, moving_lines))
    with c2:
        st.write(f"**之卦：** 第 {changed_hex['no']} 卦 {changed_hex['name']}")
        st.write(f"上卦：{changed_hex['upper']}　下卦：{changed_hex['lower']}")
        st.write(changed_hex["summary"])
        st.code(lines_to_display(changed_lines))

    st.markdown("### 朱熹法取用")
    st.write(f"**规则：** {rule_result['rule']}")
    st.write(f"**主看：** {rule_result['main_text']}")
    st.write(f"**说明：** {rule_result['detail']}")

def render_number_divination():
    add_history_record("浏览：数字卦")
    st.title("数字卦")

    question = st.text_area("请输入你想问的问题", placeholder="例如：这件事情适合现在推进吗？")
    a = st.number_input("输入第一个数字（取上卦）", min_value=1, value=8, step=1)
    b = st.number_input("输入第二个数字（取下卦）", min_value=1, value=8, step=1)

    if st.button("生成数字卦", type="primary"):
        result = simulate_number_divination(int(a), int(b))
        upper = result["upper_name"]
        lower = result["lower_name"]
        moving_lines = result["moving_lines"]

        original_hex = find_hexagram(upper, lower)
        original_lines, changed_lines, upper_name2, lower_name2, changed_hex = changed_hexagram_from_moves(upper, lower, moving_lines)
        rule_result = zhuxi_rule_explanation(original_hex, changed_hex, moving_lines)

        extra = f"取数结果：上卦 {upper}（余 {result['upper_num']}），下卦 {lower}（余 {result['lower_num']}），动爻 第 {moving_lines[0]} 爻。"
        show_divination_result("数字卦", original_hex, changed_hex, original_lines, changed_lines, moving_lines, rule_result, extra)

        if question.strip():
            with st.spinner("AI 正在生成解读..."):
                ai_text, err = ai_interpret(question, original_hex, changed_hex, moving_lines, rule_result, "数字卦")
            if err:
                st.error(err)
            else:
                st.markdown("### AI 解读")
                st.write(ai_text)

def render_coin_divination():
    add_history_record("浏览：铜钱卦")
    st.title("铜钱卦")

    question = st.text_area("请输入你想问的问题", key="coin_question", placeholder="例如：当前这次选择是否合适？")
    mode = st.radio("铜钱输入方式", ["随机掷卦", "手动输入六次结果"], horizontal=True)

    rounds = []

    if mode == "随机掷卦":
        if st.button("随机生成铜钱卦", type="primary"):
            for _ in range(6):
                toss = [random.randint(0, 1) for _ in range(3)]
                rounds.append(toss)
            st.session_state["coin_rounds"] = rounds
    else:
        st.write("每一爻输入三个面，正=1，反=0；从初爻到上爻。")
        manual_rounds = []
        for i in range(1, 7):
            cols = st.columns(3)
            vals = []
            for j in range(3):
                val = cols[j].selectbox(f"第{i}爻 第{j+1}枚", [1, 0], key=f"coin_{i}_{j}", format_func=lambda x: "正" if x == 1 else "反")
                vals.append(val)
            manual_rounds.append(vals)
        if st.button("生成手动铜钱卦", type="primary"):
            st.session_state["coin_rounds"] = manual_rounds

    rounds = st.session_state.get("coin_rounds", [])

    if rounds:
        result = simulate_coin_divination(rounds)
        upper = result["upper_name"]
        lower = result["lower_name"]
        moving_lines = result["moving_lines"]

        original_hex = find_hexagram(upper, lower)
        original_lines, changed_lines, upper_name2, lower_name2, changed_hex = changed_hexagram_from_moves(upper, lower, moving_lines)
        rule_result = zhuxi_rule_explanation(original_hex, changed_hex, moving_lines)

        detail_text = []
        for d in result["detail"]:
            detail_text.append(f"第{d['line']}爻：{' '.join(d['faces'])} → {d['label']}")
        extra = "；".join(detail_text)

        show_divination_result("铜钱卦", original_hex, changed_hex, original_lines, changed_lines, moving_lines, rule_result, extra)

        if question.strip():
            with st.spinner("AI 正在生成解读..."):
                ai_text, err = ai_interpret(question, original_hex, changed_hex, moving_lines, rule_result, "铜钱卦")
            if err:
                st.error(err)
            else:
                st.markdown("### AI 解读")
                st.write(ai_text)

def render_animation_page():
    add_history_record("浏览：动画起卦")
    st.title("动画页面")

    anim_type = st.radio("动画类型", ["数字卦动画", "铜钱卦动画"], horizontal=True)

    placeholder = st.empty()
    progress = st.progress(0, text="准备开始")

    if anim_type == "数字卦动画":
        a = st.number_input("数字A", min_value=1, value=12, step=1, key="anim_a")
        b = st.number_input("数字B", min_value=1, value=27, step=1, key="anim_b")

        if st.button("播放数字卦动画"):
            steps = [
                "读取第一个数字",
                "读取第二个数字",
                "第一个数字除八取上卦",
                "第二个数字除八取下卦",
                "两数相加除六取动爻",
                "生成本卦与之卦"
            ]
            for i, step in enumerate(steps, start=1):
                progress.progress(int(i / len(steps) * 100), text=step)
                with placeholder.container():
                    st.markdown(f"### {step}")
                    if i >= 1:
                        st.write(f"数字A：{a}")
                    if i >= 2:
                        st.write(f"数字B：{b}")
                    if i >= 3:
                        upper_name, upper_num = number_to_trigram(int(a))
                        st.write(f"上卦：{upper_name}（余数 {upper_num}）")
                    if i >= 4:
                        lower_name, lower_num = number_to_trigram(int(b))
                        st.write(f"下卦：{lower_name}（余数 {lower_num}）")
                    if i >= 5:
                        mv = moving_line_from_sum(int(a) + int(b))
                        st.write(f"动爻：第 {mv} 爻")
                    if i >= 6:
                        original_hex = find_hexagram(upper_name, lower_name)
                        original_lines, changed_lines, _, _, changed_hex = changed_hexagram_from_moves(upper_name, lower_name, [mv])
                        st.write(f"本卦：第 {original_hex['no']} 卦 {original_hex['name']}")
                        st.code(lines_to_display(original_lines, [mv]))
                        st.write(f"之卦：第 {changed_hex['no']} 卦 {changed_hex['name']}")
                        st.code(lines_to_display(changed_lines))
                time.sleep(0.4)
            progress.progress(100, text="完成")

    else:
        if st.button("播放铜钱卦动画"):
            rounds = []
            for _ in range(6):
                rounds.append([random.randint(0, 1) for _ in range(3)])

            for i, toss in enumerate(rounds, start=1):
                progress.progress(int(i / 6 * 100), text=f"第 {i} 次掷钱")
                val, moving, label = coin_to_line(toss)
                with placeholder.container():
                    st.markdown(f"### 第 {i} 次掷钱")
                    st.write("结果：", " ".join(["正" if x == 1 else "反" for x in toss]))
                    st.write(f"判定：{label}")
                    if moving:
                        st.write("此爻为动爻")
                time.sleep(0.45)

            result = simulate_coin_divination(rounds)
            upper = result["upper_name"]
            lower = result["lower_name"]
            moving_lines = result["moving_lines"]
            original_hex = find_hexagram(upper, lower)
            original_lines, changed_lines, _, _, changed_hex = changed_hexagram_from_moves(upper, lower, moving_lines)

            with placeholder.container():
                st.markdown("### 铜钱卦结果")
                st.write(f"本卦：第 {original_hex['no']} 卦 {original_hex['name']}")
                st.code(lines_to_display(original_lines, moving_lines))
                st.write(f"之卦：第 {changed_hex['no']} 卦 {changed_hex['name']}")
                st.code(lines_to_display(changed_lines))
            progress.progress(100, text="完成")

def render_notes():
    add_history_record("浏览：学习笔记")
    st.title("学习笔记")

    supabase_enabled = get_supabase() is not None
    st.caption("当前存储：Supabase" if supabase_enabled else "当前存储：本地 JSON（data/notes.json）")

    notes = load_notes()

    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("标题")
        related = st.text_input("关联卦名或主题")
        content = st.text_area("写下你的学习心得")
        submitted = st.form_submit_button("保存笔记")

    if submitted:
        if title.strip() and content.strip():
            try:
                save_note(title, related, content)
                st.success("笔记已保存。")
                st.rerun()
            except Exception as e:
                st.error(f"保存失败：{e}")
        else:
            st.warning("请至少填写标题和内容。")

    st.markdown("### 已保存笔记")
    if notes:
        for i, note in enumerate(notes[:50], start=1):
            with st.expander(f"{i}. {note.get('title', '')}｜{note.get('time', '')}"):
                st.write(f"**关联主题：** {note.get('related', '') or '无'}")
                st.write(note.get("content", ""))
    else:
        st.write("目前还没有笔记。")

def main():
    st.sidebar.title("导航菜单")
    page = st.sidebar.radio(
        "请选择页面",
        [
            "首页",
            "理论图解",
            "基础说明",
            "八卦图谱",
            "六十四卦",
            "数字卦",
            "铜钱卦",
            "动画页面",
            "学习笔记"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("易经八卦互动应用")

    if page == "首页":
        render_home()
    elif page == "理论图解":
        render_theory_image()
    elif page == "基础说明":
        render_basics()
    elif page == "八卦图谱":
        render_trigrams()
    elif page == "六十四卦":
        render_hexagrams()
    elif page == "数字卦":
        render_number_divination()
    elif page == "铜钱卦":
        render_coin_divination()
    elif page == "动画页面":
        render_animation_page()
    elif page == "学习笔记":
        render_notes()

if __name__ == "__main__":
    main()
