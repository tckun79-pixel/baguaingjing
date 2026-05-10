from __future__ import annotations

import json
import os
import random
from datetime import datetime
from pathlib import Path
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

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'PingFang SC', 'Noto Sans SC', sans-serif;
        }
        .main {background: #f5f4ef;}
        .block-container {
            max-width: 900px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }
        .main-title {
            text-align: center;
            font-size: 2.1rem;
            font-weight: 700;
            letter-spacing: 0.10em;
            color: #1a1a1a;
            margin-bottom: 6px;
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
        .soft-box {
            background: #faf8f2;
            border: 1px solid #ebe7dc;
            border-radius: 14px;
            padding: 14px 16px;
            margin: 10px 0;
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
        .guaci-box {
            background: #f0f4f0;
            border-left: 4px solid #2e7d32;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 6px 0;
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
        .muted { color: #6f6f6f; font-size: 0.93rem; }
        .pill-note {
            display: inline-block;
            border-radius: 18px;
            background: #f0efeb;
            padding: 5px 10px;
            font-size: 0.84rem;
            color: #555;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .hex-card {
            background: #fff;
            border: 1px solid #e8e7e2;
            border-radius: 14px;
            padding: 14px 16px;
            margin: 8px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.json"
HEXAGRAM_FILE = DATA_DIR / "hexagrams_full.json"

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
LINE_LABELS = {0: "初爻", 1: "二爻", 2: "三爻", 3: "四爻", 4: "五爻", 5: "上爻"}

FALLBACK_HEXAGRAMS = [
    {
        "no": 1,
        "name": "乾",
        "upper": "乾",
        "lower": "乾",
        "summary": "元亨利贞，象征创造与刚健。",
        "gua_ci": "乾：元亨利贞。",
        "lines": [
            "初九：潜龙勿用。",
            "九二：见龙在田，利见大人。",
            "九三：君子终日乾乾，夕惕若厉，无咎。",
            "九四：或跃在渊，无咎。",
            "九五：飞龙在天，利见大人。",
            "上九：亢龙有悔。",
        ],
        "use": "用九：见群龙无首，吉。",
    },
    {
        "no": 2,
        "name": "坤",
        "upper": "坤",
        "lower": "坤",
        "summary": "厚德载物，象征承载与包容。",
        "gua_ci": "坤：元亨，利牝马之贞。君子有攸往，先迷后得主。利西南得朋，东北丧朋。安贞吉。",
        "lines": [
            "初六：履霜，坚冰至。",
            "六二：直方大，不习无不利。",
            "六三：含章可贞。或从王事，无成有终。",
            "六四：括囊，无咎无誉。",
            "六五：黄裳，元吉。",
            "上六：龙战于野，其血玄黄。",
        ],
        "use": "用六：利永贞。",
    },
]


def read_json(path: Path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def atomic_save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


HEXAGRAMS: List[Dict] = read_json(HEXAGRAM_FILE, FALLBACK_HEXAGRAMS)
HEXAGRAM_BY_NO = {item["no"]: item for item in HEXAGRAMS}
HEXAGRAM_BY_NAME = {item["name"]: item for item in HEXAGRAMS}


@st.cache_resource
def get_openai_client():
    if OpenAI is None:
        return None
    api_key = None
    try:
        api_key = st.secrets.get("openai", {}).get("api_key")
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


client = get_openai_client()


def init_state() -> None:
    defaults = {
        "page": "起卦",
        "method": "数字起卦",
        "question": "",
        "div_result": None,
        "history": read_json(HISTORY_FILE, []),
        "ai_result_text": "",
        "lookup_no": 1,
        "lookup_name": list(HEXAGRAM_BY_NAME.keys())[0] if HEXAGRAM_BY_NAME else "乾",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def render_header() -> None:
    st.markdown('<div class="main-title">易经 · 朱熹解卦</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">稳定版 · 可直接运行 · 支持完整卦辞与爻辞原文</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if HEXAGRAM_FILE.exists() and len(HEXAGRAMS) >= 64:
        st.success("已加载完整六十四卦数据。")
    else:
        st.warning("当前未检测到完整 data/hexagrams_full.json，页面可运行，但仅内置少量示例卦。")


def line_visual(v: int) -> str:
    return "━━━━━━" if v == 1 else "━━  ━━"


def line_after_change(pair: Tuple[int, int]) -> int:
    a, b = pair
    return a if a == b else (1 - a)


def line_type_name(pair: Tuple[int, int]) -> str:
    a, b = pair
    if a == 1 and b == 1:
        return "少阳"
    if a == 0 and b == 0:
        return "少阴"
    if a == 1 and b == 0:
        return "老阳"
    return "老阴"


def trigram_name_from_lines(lines3: List[int]) -> str:
    for name, item in TRIGRAMS.items():
        if item["lines"] == lines3:
            return name
    raise ValueError(f"无法识别三爻：{lines3}")


def hexagram_lines(hexagram: Dict) -> List[int]:
    return TRIGRAMS[hexagram["lower"]]["lines"] + TRIGRAMS[hexagram["upper"]]["lines"]


def find_hexagram(upper: str, lower: str) -> Optional[Dict]:
    for item in HEXAGRAMS:
        if item.get("upper") == upper and item.get("lower") == lower:
            return item
    return None


def build_result_from_pairs(pairs: List[Tuple[int, int]], question: str, method: str) -> Dict:
    original_lines = [a for a, _ in pairs]
    changed_lines = [line_after_change(p) for p in pairs]
    moving = [i for i, p in enumerate(pairs) if p[0] != p[1]]

    lower = trigram_name_from_lines(original_lines[:3])
    upper = trigram_name_from_lines(original_lines[3:])
    main_hex = find_hexagram(upper, lower)
    if not main_hex:
        raise ValueError("未找到本卦")

    changed_lower = trigram_name_from_lines(changed_lines[:3])
    changed_upper = trigram_name_from_lines(changed_lines[3:])
    changed_hex = find_hexagram(changed_upper, changed_lower)

    return {
        "question": question.strip(),
        "method": method,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pairs": [[a, b] for a, b in pairs],
        "moving": moving,
        "original_lines": original_lines,
        "changed_lines": changed_lines,
        "hexagram_no": main_hex["no"],
        "changed_hexagram_no": changed_hex["no"] if changed_hex else None,
    }


def get_hex_by_result(result: Dict) -> Tuple[Dict, Optional[Dict]]:
    main_hex = HEXAGRAM_BY_NO[result["hexagram_no"]]
    changed_hex = HEXAGRAM_BY_NO.get(result.get("changed_hexagram_no"))
    return main_hex, changed_hex


def save_history_record(result: Dict) -> None:
    history = st.session_state.history[:]
    main_hex, changed_hex = get_hex_by_result(result)
    record = {
        "timestamp": result["timestamp"],
        "question": result.get("question", ""),
        "method": result.get("method", ""),
        "hexagram_no": main_hex["no"],
        "hexagram_name": main_hex["name"],
        "changed_hexagram_no": changed_hex["no"] if changed_hex else None,
        "changed_hexagram_name": changed_hex["name"] if changed_hex else None,
        "moving": result.get("moving", []),
        "pairs": result.get("pairs", []),
    }
    history.append(record)
    history = history[-200:]
    st.session_state.history = history
    atomic_save_json(HISTORY_FILE, history)


def render_trigram_badges(hexagram: Dict) -> None:
    upper = TRIGRAMS[hexagram["upper"]]
    lower = TRIGRAMS[hexagram["lower"]]
    st.markdown(
        f'<span class="pill-note">上卦：{upper["symbol"]} {hexagram["upper"]} · {upper["nature"]}</span>'
        f'<span class="pill-note">下卦：{lower["symbol"]} {hexagram["lower"]} · {lower["nature"]}</span>',
        unsafe_allow_html=True,
    )


def render_line_table(lines: List[int], moving: List[int], title: str) -> None:
    st.markdown(f"### {title}")
    rows = []
    for idx in range(5, -1, -1):
        rows.append({
            "爻位": LINE_LABELS[idx],
            "阴阳": "阳" if lines[idx] == 1 else "阴",
            "线形": line_visual(lines[idx]),
            "动静": "动" if idx in moving else "静",
        })
    st.table(rows)


def render_judgement(main_hex: Dict, changed_hex: Optional[Dict], moving: List[int]) -> None:
    st.markdown("## 朱熹法取用")
    count = len(moving)
    if count == 0:
        msg = "无动爻，以本卦卦辞为主断。"
    elif count == 1:
        msg = f"一爻变，以变爻爻辞为主。主断：{LINE_LABELS[moving[0]]}。"
    elif count == 2:
        msg = f"两爻变，以上位变爻爻辞为主。主断：{LINE_LABELS[max(moving)]}；辅助：{LINE_LABELS[min(moving)]}。"
    elif count == 3:
        extra = f"之卦为第{changed_hex['no']}卦《{changed_hex['name']}》。" if changed_hex else ""
        msg = f"三爻变，本卦与之卦并看，兼参两卦卦辞。{extra}"
    elif count == 4:
        remain = [i for i in range(6) if i not in moving]
        msg = f"四爻变，以之卦不变二爻为主，以下位不变爻为主断。主断：{LINE_LABELS[min(remain)]}。"
    elif count == 5:
        remain = [i for i in range(6) if i not in moving]
        msg = f"五爻变，以之卦唯一不变爻的爻辞为主。主断：{LINE_LABELS[remain[0]]}。"
    else:
        if main_hex["name"] == "乾":
            msg = "六爻皆变，乾卦取用九为主。"
        elif main_hex["name"] == "坤":
            msg = "六爻皆变，坤卦取用六为主。"
        else:
            extra = f"之卦为第{changed_hex['no']}卦《{changed_hex['name']}》。" if changed_hex else ""
            msg = f"六爻皆变，以之卦卦辞为主。{extra}"
    st.markdown(f"<div class='rule-box'>{msg}</div>", unsafe_allow_html=True)


def render_texts(main_hex: Dict, changed_hex: Optional[Dict], moving: List[int]) -> None:
    st.markdown("## 卦辞与爻辞")

    with st.expander("📜 本卦卦辞", expanded=True):
        st.markdown(
            f"<div class='guaci-box'><b>第{main_hex['no']}卦《{main_hex['name']}》</b><br>{main_hex.get('gua_ci', main_hex.get('summary', ''))}</div>",
            unsafe_allow_html=True,
        )
        if main_hex.get("summary"):
            st.markdown(f"<div class='muted'>{main_hex['summary']}</div>", unsafe_allow_html=True)

    if changed_hex and changed_hex["no"] != main_hex["no"]:
        with st.expander("🔁 之卦卦辞", expanded=False):
            st.markdown(
                f"<div class='guaci-box'><b>第{changed_hex['no']}卦《{changed_hex['name']}》</b><br>{changed_hex.get('gua_ci', changed_hex.get('summary', ''))}</div>",
                unsafe_allow_html=True,
            )

    with st.expander("🔴 主断爻辞", expanded=True):
        count = len(moving)
        if count == 0:
            st.markdown("<div class='yaoci-box yaoci-main'>本次无动爻，以本卦卦辞为主断。</div>", unsafe_allow_html=True)
        elif count == 1:
            idx = moving[0]
            st.markdown(f"<div class='yaoci-box yaoci-main'><b>{LINE_LABELS[idx]}：</b>{main_hex['lines'][idx]}</div>", unsafe_allow_html=True)
        elif count == 2:
            idx = max(moving)
            st.markdown(f"<div class='yaoci-box yaoci-main'><b>{LINE_LABELS[idx]}：</b>{main_hex['lines'][idx]}</div>", unsafe_allow_html=True)
        elif count == 4 and changed_hex:
            remain = [i for i in range(6) if i not in moving]
            idx = min(remain)
            st.markdown(f"<div class='yaoci-box yaoci-main'><b>之卦{LINE_LABELS[idx]}：</b>{changed_hex['lines'][idx]}</div>", unsafe_allow_html=True)
        elif count == 5 and changed_hex:
            remain = [i for i in range(6) if i not in moving]
            idx = remain[0]
            st.markdown(f"<div class='yaoci-box yaoci-main'><b>之卦{LINE_LABELS[idx]}：</b>{changed_hex['lines'][idx]}</div>", unsafe_allow_html=True)
        elif count == 6 and main_hex['name'] in ('乾', '坤') and main_hex.get('use'):
            st.markdown(f"<div class='yaoci-box yaoci-main'><b>{main_hex['use']}</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='yaoci-box yaoci-main'>本次以卦辞综合参断，请同时参考本卦与之卦。</div>", unsafe_allow_html=True)

    with st.expander("🟡 动爻原文", expanded=False):
        if not moving:
            st.markdown("<div class='yaoci-box'>无动爻。</div>", unsafe_allow_html=True)
        else:
            for idx in moving:
                st.markdown(f"<div class='yaoci-box yaoci-secondary'><b>{LINE_LABELS[idx]}：</b>{main_hex['lines'][idx]}</div>", unsafe_allow_html=True)

    with st.expander("📖 本卦六爻全览", expanded=False):
        for idx, line in enumerate(main_hex.get("lines", [])):
            css = "yaoci-main" if idx in moving else ""
            st.markdown(f"<div class='yaoci-box {css}'><b>{LINE_LABELS[idx]}：</b>{line}</div>", unsafe_allow_html=True)
        if main_hex.get("use"):
            st.markdown(f"<div class='yaoci-box'><b>{main_hex['use']}</b></div>", unsafe_allow_html=True)

    if changed_hex and changed_hex["no"] != main_hex["no"]:
        with st.expander("📘 之卦六爻全览", expanded=False):
            for idx, line in enumerate(changed_hex.get("lines", [])):
                st.markdown(f"<div class='yaoci-box'><b>{LINE_LABELS[idx]}：</b>{line}</div>", unsafe_allow_html=True)
            if changed_hex.get("use"):
                st.markdown(f"<div class='yaoci-box'><b>{changed_hex['use']}</b></div>", unsafe_allow_html=True)


def build_ai_prompt(result: Dict, main_hex: Dict, changed_hex: Optional[Dict]) -> str:
    moving_text = "、".join(LINE_LABELS[i] for i in result["moving"]) if result["moving"] else "无动爻"
    main_lines_text = "
".join([f"{LINE_LABELS[i]}：{main_hex['lines'][i]}" for i in range(6)])
    changed_text = ""
    if changed_hex:
        changed_lines_text = "
".join([f"{LINE_LABELS[i]}：{changed_hex['lines'][i]}" for i in range(6)])
        changed_text = f"
之卦：第{changed_hex['no']}卦《{changed_hex['name']}》
之卦卦辞：{changed_hex.get('gua_ci', '')}
之卦爻辞：
{changed_lines_text}
"
    return f"""
你是一位熟悉《周易》与朱熹《周易本义》的解卦者，请严格按朱熹法取用。
占问：{result.get('question') or '未填写'}
起卦方式：{result['method']}
本卦：第{main_hex['no']}卦《{main_hex['name']}》
本卦卦辞：{main_hex.get('gua_ci', '')}
本卦爻辞：
{main_lines_text}
动爻：{moving_text}
{changed_text}
请输出四部分：
1. 卦象判断
2. 朱熹法取用说明
3. 结合原文的解读
4. 简洁建议
要求：引用卦辞或爻辞原文，不要编造未给出的古文，语言清楚稳重。
"""


def render_ai_section(result: Dict, main_hex: Dict, changed_hex: Optional[Dict]) -> None:
    st.markdown("## AI 解卦")
    if client is None:
        st.info("未配置 OpenAI API Key，AI 解卦已关闭；基础起卦与原文查询仍可正常使用。")
        return
    if st.button("生成 AI 解卦", use_container_width=True):
        try:
            with st.spinner("正在生成解卦…"):
                prompt = build_ai_prompt(result, main_hex, changed_hex)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "你是研究周易与朱熹解卦法的学者。"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=1200,
                )
                st.session_state.ai_result_text = resp.choices[0].message.content
        except Exception as e:
            st.session_state.ai_result_text = f"AI 解卦失败：{e}"
    if st.session_state.ai_result_text:
        st.markdown(f"<div class='soft-box'>{st.session_state.ai_result_text}</div>", unsafe_allow_html=True)


def render_result(result: Dict) -> None:
    main_hex, changed_hex = get_hex_by_result(result)
    moving = result["moving"]

    st.markdown("## 卦象结果")
    if changed_hex and changed_hex["no"] != main_hex["no"]:
        title = f"本卦：第{main_hex['no']}卦《{main_hex['name']}》 → 之卦：第{changed_hex['no']}卦《{changed_hex['name']}》"
    else:
        title = f"本卦：第{main_hex['no']}卦《{main_hex['name']}》"
    st.markdown(f"<div class='hex-card'><b>{title}</b></div>", unsafe_allow_html=True)
    render_trigram_badges(main_hex)
    if result.get("question"):
        st.markdown(f"<div class='muted'>所问：{result['question']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='muted'>动爻：{'、'.join(LINE_LABELS[i] for i in moving) if moving else '无'}</div>",
        unsafe_allow_html=True,
    )

    render_line_table(result["original_lines"], moving, "本卦六爻")
    if changed_hex and result["changed_lines"] != result["original_lines"]:
        render_line_table(result["changed_lines"], [], "之卦六爻")

    render_judgement(main_hex, changed_hex, moving)
    render_texts(main_hex, changed_hex, moving)
    render_ai_section(result, main_hex, changed_hex)


def random_coin_pairs() -> List[Tuple[int, int]]:
    pairs = []
    for _ in range(6):
        faces = [random.randint(0, 1) for _ in range(3)]
        count = sum(faces)
        if count == 3:
            pairs.append((1, 0))
        elif count == 2:
            pairs.append((0, 0))
        elif count == 1:
            pairs.append((1, 1))
        else:
            pairs.append((0, 1))
    return pairs


def manual_pair(option: str) -> Tuple[int, int]:
    mapping = {
        "少阳（静阳）": (1, 1),
        "少阴（静阴）": (0, 0),
        "老阳（阳变阴）": (1, 0),
        "老阴（阴变阳）": (0, 1),
    }
    return mapping[option]


def number_divination(n1: int, n2: int, n3: int, question: str) -> Dict:
    upper_idx = n1 % 8 or 8
    lower_idx = n2 % 8 or 8
    move_idx = n3 % 6 or 6
    upper = TRIGRAM_MAP[upper_idx]
    lower = TRIGRAM_MAP[lower_idx]
    hexagram = find_hexagram(upper, lower)
    if not hexagram:
        raise ValueError("数字起卦未找到对应卦象。请确认 hexagrams_full.json 是否完整。")
    orig = hexagram_lines(hexagram)
    pairs = []
    for i, val in enumerate(orig, start=1):
        pairs.append((val, 1 - val) if i == move_idx else (val, val))
    return build_result_from_pairs(pairs, question, "数字起卦")


def page_divination() -> None:
    render_header()
    st.radio("起卦方式", ["数字起卦", "铜钱起卦"], key="method", horizontal=True)
    st.text_input("占问之事（可选）", key="question", placeholder="例如：工作去留、合作是否可行、关系发展……")

    if st.session_state.method == "数字起卦":
        st.markdown("<div class='rule-box'>数字起卦：第一个数字取上卦，第二个数字取下卦，第三个数字取动爻。</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            n1 = st.number_input("上卦数", min_value=1, max_value=9999, value=1, step=1)
        with c2:
            n2 = st.number_input("下卦数", min_value=1, max_value=9999, value=1, step=1)
        with c3:
            n3 = st.number_input("动爻数", min_value=1, max_value=9999, value=1, step=1)
        if st.button("生成数字卦", use_container_width=True):
            try:
                result = number_divination(int(n1), int(n2), int(n3), st.session_state.question)
                st.session_state.div_result = result
                st.session_state.ai_result_text = ""
                save_history_record(result)
            except Exception as e:
                st.error(str(e))

    else:
        st.markdown("<div class='rule-box'>铜钱法：三枚铜钱，六次成卦，自下而上记录。三正老阳，两正一反少阴，一正两反少阳，三反老阴。</div>", unsafe_allow_html=True)
        if st.button("随机投六次铜钱", use_container_width=True):
            try:
                result = build_result_from_pairs(random_coin_pairs(), st.session_state.question, "铜钱起卦")
                st.session_state.div_result = result
                st.session_state.ai_result_text = ""
                save_history_record(result)
            except Exception as e:
                st.error(str(e))

        with st.expander("手动输入六爻", expanded=True):
            options = ["少阳（静阳）", "少阴（静阴）", "老阳（阳变阴）", "老阴（阴变阳）"]
            picks = []
            c1, c2 = st.columns(2)
            for i in range(6):
                box = c1 if i % 2 == 0 else c2
                with box:
                    picks.append(st.selectbox(f"{LINE_LABELS[i]}", options, key=f"manual_{i}"))
            if st.button("按手动输入生成卦", use_container_width=True):
                try:
                    pairs = [manual_pair(x) for x in picks]
                    result = build_result_from_pairs(pairs, st.session_state.question, "铜钱起卦（手动）")
                    st.session_state.div_result = result
                    st.session_state.ai_result_text = ""
                    save_history_record(result)
                except Exception as e:
                    st.error(str(e))

    if st.session_state.div_result:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        render_result(st.session_state.div_result)


def page_lookup() -> None:
    render_header()
    st.markdown("## 卦象查询")
    tab1, tab2 = st.tabs(["按卦序", "按卦名"])

    with tab1:
        max_no = max(HEXAGRAM_BY_NO.keys()) if HEXAGRAM_BY_NO else 1
        no = st.number_input("卦序", min_value=1, max_value=max_no, value=min(st.session_state.lookup_no, max_no), step=1)
        st.session_state.lookup_no = int(no)
        hexagram = HEXAGRAM_BY_NO[int(no)]

    with tab2:
        names = list(HEXAGRAM_BY_NAME.keys())
        idx = names.index(st.session_state.lookup_name) if st.session_state.lookup_name in names else 0
        name = st.selectbox("卦名", names, index=idx)
        st.session_state.lookup_name = name
        hexagram = HEXAGRAM_BY_NAME[name]

    st.markdown(f"## 第{hexagram['no']}卦《{hexagram['name']}》")
    render_trigram_badges(hexagram)
    st.markdown(
        f"<div class='guaci-box'><b>卦辞</b><br>{hexagram.get('gua_ci', hexagram.get('summary', ''))}</div>",
        unsafe_allow_html=True,
    )
    with st.expander("查看六爻原文", expanded=True):
        for i, line in enumerate(hexagram.get("lines", [])):
            st.markdown(f"<div class='yaoci-box'><b>{LINE_LABELS[i]}：</b>{line}</div>", unsafe_allow_html=True)
        if hexagram.get("use"):
            st.markdown(f"<div class='yaoci-box'><b>{hexagram['use']}</b></div>", unsafe_allow_html=True)


def page_history() -> None:
    render_header()
    st.markdown("## 历史记录")
    if not st.session_state.history:
        st.info("暂无历史记录。")
        return
    if st.button("清空历史记录"):
        st.session_state.history = []
        atomic_save_json(HISTORY_FILE, [])
        st.rerun()
    for i, item in enumerate(reversed(st.session_state.history), start=1):
        changed_text = ""
        if item.get("changed_hexagram_no"):
            changed_text = f" → 第{item['changed_hexagram_no']}卦《{item.get('changed_hexagram_name', '')}》"
        title = f"{i}. {item.get('timestamp', '')} · 第{item.get('hexagram_no')}卦《{item.get('hexagram_name', '')}》{changed_text}"
        with st.expander(title, expanded=False):
            st.write(f"方式：{item.get('method', '')}")
            st.write(f"所问：{item.get('question') or '未填写'}")
            moving = item.get('moving', [])
            st.write(f"动爻：{'、'.join(LINE_LABELS[x] for x in moving) if moving else '无'}")
            pairs = item.get('pairs', [])
            if pairs:
                rows = []
                for idx, pair in enumerate(pairs):
                    rows.append({"爻位": LINE_LABELS[idx], "类型": line_type_name(tuple(pair))})
                st.table(rows)


def page_about() -> None:
    render_header()
    st.markdown("## 说明")
    st.markdown(
        """
        <div class='soft-box'>
        <b>本版特点</b><br>
        1. 完整可执行，不依赖前端脚本消息回传。<br>
        2. 未配置 OpenAI 时也能正常起卦、查卦、看爻辞。<br>
        3. 历史记录本地保存到 data/history.json。<br>
        4. 放入 data/hexagrams_full.json 后即可显示完整六十四卦原文。<br>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class='rule-box'>
        <b>目录建议</b><br>
        app.py<br>
        data/hexagrams_full.json<br>
        .streamlit/secrets.toml（可选）<br>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### 导航")
    st.radio("页面", ["起卦", "卦象查询", "历史记录", "说明"], key="page")
    st.markdown("---")
    st.caption("这是稳定版 app.py。若页面曾空白，通常是脚本报错或前端组件未正常返回。此版已移除高风险依赖。")

if st.session_state.page == "起卦":
    page_divination()
elif st.session_state.page == "卦象查询":
    page_lookup()
elif st.session_state.page == "历史记录":
    page_history()
else:
    page_about()
