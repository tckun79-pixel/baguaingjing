import streamlit as st
import os
import random
from openai import OpenAI

st.set_page_config(
    page_title="易经·朱熹解卦",
    page_icon="☯",
    layout="centered"
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'PingFang SC', 'Noto Sans SC', sans-serif;
    }
    .main {background: #f5f4ef;}
    .block-container {
        max-width: 680px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .card {
        background: white;
        border-radius: 20px;
        padding: 36px 32px;
        margin-bottom: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 0.15em;
        color: #1a1a1a;
        margin-bottom: 4px;
    }
    .sub-title {
        text-align: center;
        font-style: italic;
        font-size: 1rem;
        color: #888;
        margin-bottom: 28px;
    }
    .divider {
        border: none;
        border-top: 1px solid #e8e8e8;
        margin: 18px 0;
    }
    .method-btn-row {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 18px 0 24px 0;
    }
    .num-card {
        background: #f5f4ef;
        border-radius: 16px;
        text-align: center;
        padding: 18px 0 12px 0;
    }
    .num-label {
        font-size: 0.8rem;
        color: #aaa;
        margin-bottom: 6px;
    }
    .num-value {
        font-size: 2.2rem;
        font-weight: 500;
        color: #1a1a1a;
    }
    .coin-area {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 32px 0 20px 0;
    }
    .coin-circle {
        width: 72px; height: 72px;
        border-radius: 50%;
        background: #e8e8e8;
        margin-bottom: 14px;
    }
    .coin-hint {
        color: #aaa;
        font-size: 0.95rem;
    }
    .cast-btn {
        width: 100%;
        background: #1a1a1a !important;
        color: white !important;
        border-radius: 16px !important;
        font-size: 1.1rem !important;
        padding: 14px 0 !important;
        border: none !important;
        margin-top: 10px;
    }
    .hexagram-card {
        background: #f5f4ef;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
    }
    .hex-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 6px;
    }
    .hex-sub {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 10px;
    }
    .hex-summary {
        font-size: 0.9rem;
        color: #555;
        margin-top: 8px;
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
    .line-row {
        display: flex;
        align-items: center;
        margin: 5px 0;
    }
    .line-yang {
        height: 10px;
        background: #1a1a1a;
        border-radius: 3px;
        flex: 1;
        margin: 2px 0;
    }
    .line-yin-l {
        height: 10px;
        background: #1a1a1a;
        border-radius: 3px;
        flex: 0.45;
    }
    .line-yin-r {
        height: 10px;
        background: #1a1a1a;
        border-radius: 3px;
        flex: 0.45;
        margin-left: auto;
    }
    .moving-tag {
        color: #c0392b;
        font-size: 0.75rem;
        margin-left: 6px;
        font-weight: bold;
    }
    .toss-line-result {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 0.9rem;
    }
    .dot {
        width: 30px; height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .dot-yang { background: #1a1a1a; color: white; }
    .dot-yin  { background: #f0f0f0; color: #555; }
    .stButton > button {
        border-radius: 12px;
        font-size: 1rem;
        padding: 10px 24px;
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

TRIGRAM_MAP = {1: "乾", 2: "兑", 3: "离", 4: "震", 5: "巽", 6: "坎", 7: "艮", 8: "坤"}
TRIGRAMS = {
    "乾": {"symbol": "☰", "lines": [1,1,1], "nature": "天", "meaning": "刚健、创造、主动"},
    "兑": {"symbol": "☱", "lines": [1,1,0], "nature": "泽", "meaning": "喜悦、交流、和悦"},
    "离": {"symbol": "☲", "lines": [1,0,1], "nature": "火", "meaning": "光明、依附、明辨"},
    "震": {"symbol": "☳", "lines": [1,0,0], "nature": "雷", "meaning": "发动、惊醒、开端"},
    "巽": {"symbol": "☴", "lines": [0,1,1], "nature": "风", "meaning": "进入、渗透、柔顺"},
    "坎": {"symbol": "☵", "lines": [0,1,0], "nature": "水", "meaning": "险陷、流动、智慧"},
    "艮": {"symbol": "☶", "lines": [0,0,1], "nature": "山", "meaning": "止、界限、沉静"},
    "坤": {"symbol": "☷", "lines": [0,0,0], "nature": "地", "meaning": "柔顺、承载、包容"},
}
HEXAGRAMS = [
    {"no":1,"name":"乾","upper":"乾","lower":"乾","summary":"元亨利贞，象征创造与刚健。",
     "lines":["初九：潜龙勿用。","九二：见龙在田，利见大人。","九三：君子终日乾乾，夕惕若厉，无咎。","九四：或跃在渊，无咎。","九五：飞龙在天，利见大人。","上九：亢龙有悔。"],"use":"用九：见群龙无首，吉。"},
    {"no":2,"name":"坤","upper":"坤","lower":"坤","summary":"厚德载物，象征承载与包容。",
     "lines":["初六：履霜，坚冰至。","六二：直、方、大，不习无不利。","六三：含章可贞，或从王事，无成有终。","六四：括囊，无咎无誉。","六五：黄裳，元吉。","上六：龙战于野，其血玄黄。"],"use":"用六：利永贞。"},
    {"no":3,"name":"屯","upper":"坎","lower":"震","summary":"万事开头难，重在建立秩序。"},
    {"no":4,"name":"蒙","upper":"艮","lower":"坎","summary":"启蒙求知，强调教育与学习。"},
    {"no":5,"name":"需","upper":"坎","lower":"乾","summary":"等待时机，强调准备与耐心。"},
    {"no":6,"name":"讼","upper":"乾","lower":"坎","summary":"争议与辨析，提醒审慎处理冲突。"},
    {"no":7,"name":"师","upper":"坤","lower":"坎","summary":"组织与纪律，强调群体协作。"},
    {"no":8,"name":"比","upper":"坎","lower":"坤","summary":"亲比合作，重视关系与团结。"},
    {"no":9,"name":"小畜","upper":"巽","lower":"乾","summary":"小有积蓄，宜渐进推进。"},
    {"no":10,"name":"履","upper":"乾","lower":"兑","summary":"履行规范，重视礼与分寸。"},
    {"no":11,"name":"泰","upper":"坤","lower":"乾","summary":"通泰和顺，象征顺畅与协调。"},
    {"no":12,"name":"否","upper":"乾","lower":"坤","summary":"闭塞不通，提醒调整结构。"},
    {"no":13,"name":"同人","upper":"乾","lower":"离","summary":"与人协作，强调共识与合作。"},
    {"no":14,"name":"大有","upper":"离","lower":"乾","summary":"丰盛充实，重在守成与明辨。"},
    {"no":15,"name":"谦","upper":"坤","lower":"艮","summary":"谦逊有节，利于长久发展。"},
    {"no":16,"name":"豫","upper":"震","lower":"坤","summary":"喜悦奋发，但需防松散。"},
    {"no":17,"name":"随","upper":"兑","lower":"震","summary":"随顺而动，强调适应与跟进。"},
    {"no":18,"name":"蛊","upper":"艮","lower":"巽","summary":"整顿积弊，重在修正与治理。"},
    {"no":19,"name":"临","upper":"坤","lower":"兑","summary":"临事而治，重视责任与接近。"},
    {"no":20,"name":"观","upper":"巽","lower":"坤","summary":"观察反思，强调审视与体察。"},
    {"no":21,"name":"噬嗑","upper":"离","lower":"震","summary":"明辨与执行并重，处理阻碍。"},
    {"no":22,"name":"贲","upper":"艮","lower":"离","summary":"文饰与形式，提醒内外平衡。"},
    {"no":23,"name":"剥","upper":"艮","lower":"坤","summary":"剥落衰减，宜守正待时。"},
    {"no":24,"name":"复","upper":"坤","lower":"震","summary":"返回起点，意味着重启与修复。"},
    {"no":25,"name":"无妄","upper":"乾","lower":"震","summary":"自然真实，强调不妄为。"},
    {"no":26,"name":"大畜","upper":"艮","lower":"乾","summary":"积蓄力量，宜厚积薄发。"},
    {"no":27,"name":"颐","upper":"艮","lower":"震","summary":"养正其本，强调滋养与言行。"},
    {"no":28,"name":"大过","upper":"兑","lower":"巽","summary":"承压过重，需调整支撑结构。"},
    {"no":29,"name":"坎","upper":"坎","lower":"坎","summary":"重险之中，重在谨慎与智慧。"},
    {"no":30,"name":"离","upper":"离","lower":"离","summary":"光明相继，强调认知与文明。"},
    {"no":31,"name":"咸","upper":"兑","lower":"艮","summary":"感应相通，强调互动与影响。"},
    {"no":32,"name":"恒","upper":"震","lower":"巽","summary":"持久有常，强调稳定与坚持。"},
    {"no":33,"name":"遁","upper":"乾","lower":"艮","summary":"适时退避，也是一种智慧。"},
    {"no":34,"name":"大壮","upper":"震","lower":"乾","summary":"力量增长，宜守正不躁进。"},
    {"no":35,"name":"晋","upper":"离","lower":"坤","summary":"前进上升，强调光明与进展。"},
    {"no":36,"name":"明夷","upper":"坤","lower":"离","summary":"光明受伤，宜内守与审势。"},
    {"no":37,"name":"家人","upper":"巽","lower":"离","summary":"家内秩序，强调责任与角色。"},
    {"no":38,"name":"睽","upper":"离","lower":"兑","summary":"差异与背离，重在求同存异。"},
    {"no":39,"name":"蹇","upper":"坎","lower":"艮","summary":"行进艰难，宜求助与调整。"},
    {"no":40,"name":"解","upper":"震","lower":"坎","summary":"缓解释放，适合解除压力。"},
    {"no":41,"name":"损","upper":"艮","lower":"兑","summary":"有所减损，以求整体平衡。"},
    {"no":42,"name":"益","upper":"巽","lower":"震","summary":"增益发展，重在有益于整体。"},
    {"no":43,"name":"夬","upper":"兑","lower":"乾","summary":"决断行动，但须防偏激。"},
    {"no":44,"name":"姤","upper":"乾","lower":"巽","summary":"相遇之机，需辨别轻重。"},
    {"no":45,"name":"萃","upper":"兑","lower":"坤","summary":"会聚集合，利于凝聚资源。"},
    {"no":46,"name":"升","upper":"坤","lower":"巽","summary":"逐步上升，重在积累与耐心。"},
    {"no":47,"name":"困","upper":"兑","lower":"坎","summary":"处困之时，重在守志。"},
    {"no":48,"name":"井","upper":"坎","lower":"巽","summary":"井养众人，强调基础资源。"},
    {"no":49,"name":"革","upper":"兑","lower":"离","summary":"改革变更，需把握时机。"},
    {"no":50,"name":"鼎","upper":"离","lower":"巽","summary":"器物更新，象征文化与转化。"},
    {"no":51,"name":"震","upper":"震","lower":"震","summary":"震动惊醒，推动新的开始。"},
    {"no":52,"name":"艮","upper":"艮","lower":"艮","summary":"止而后定，强调静与界限。"},
    {"no":53,"name":"渐","upper":"巽","lower":"艮","summary":"循序渐进，贵在稳步前行。"},
    {"no":54,"name":"归妹","upper":"震","lower":"兑","summary":"关系安排，提醒辨位与分寸。"},
    {"no":55,"name":"丰","upper":"震","lower":"离","summary":"丰盛明亮，亦需防过满。"},
    {"no":56,"name":"旅","upper":"离","lower":"艮","summary":"旅途变动，宜谨慎与自持。"},
    {"no":57,"name":"巽","upper":"巽","lower":"巽","summary":"柔顺深入，强调渗透与影响。"},
    {"no":58,"name":"兑","upper":"兑","lower":"兑","summary":"喜悦交流，贵在真诚沟通。"},
    {"no":59,"name":"涣","upper":"巽","lower":"坎","summary":"涣散之后，重在重新凝聚。"},
    {"no":60,"name":"节","upper":"坎","lower":"兑","summary":"节制有度，强调规则与边界。"},
    {"no":61,"name":"中孚","upper":"巽","lower":"兑","summary":"诚信感通，重视真实与信任。"},
    {"no":62,"name":"小过","upper":"震","lower":"艮","summary":"小事可行，大事宜慎。"},
    {"no":63,"name":"既济","upper":"坎","lower":"离","summary":"事情初成，仍需保持谨慎。"},
    {"no":64,"name":"未济","upper":"离","lower":"坎","summary":"尚未完成，强调继续调整。"},
]

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
    for n, t in TRIGRAMS.items():
        if t["lines"] == l3:
            return n
    return "乾"

def hex_lines(upper, lower):
    return TRIGRAMS[lower]["lines"] + TRIGRAMS[upper]["lines"]

def get_changed_hex(upper, lower, moving):
    orig = hex_lines(upper, lower)
    chg = orig[:]
    for m in moving:
        chg[m-1] ^= 1
    ln = lines_to_trigram(chg[:3])
    un = lines_to_trigram(chg[3:])
    return orig, chg, find_hexagram(un, ln)

def render_hex_svg(lines, moving=None, width=120):
    moving = moving or []
    h = width
    lh = 11
    gap = 8
    total_h = 6 * (lh + gap) + 16
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_h}">']
    for i, (line_no, v) in enumerate(reversed(list(enumerate(lines, 1)))):
        y = 8 + i * (lh + gap)
        mv = line_no in moving
        color = "#c0392b" if mv else "#1a1a1a"
        if v == 1:
            parts.append(f'<rect x="4" y="{y}" width="{width-8}" height="{lh}" rx="3" fill="{color}"/>')
        else:
            hw = (width - 18) // 2
            parts.append(f'<rect x="4" y="{y}" width="{hw}" height="{lh}" rx="3" fill="{color}"/>')
            parts.append(f'<rect x="{width - 4 - hw}" y="{y}" width="{hw}" height="{lh}" rx="3" fill="{color}"/>')
        if mv:
            parts.append(f'<text x="{width//2}" y="{y+9}" text-anchor="middle" font-size="8" fill="#c0392b">{"○" if v==1 else "×"}</text>')
    parts.append('</svg>')
    return "".join(parts)

def hex_card_html(h, lines, moving=None, label=""):
    moving = moving or []
    svg = render_hex_svg(lines, moving, 110)
    u = TRIGRAMS.get(h.get("upper","乾"), {})
    l = TRIGRAMS.get(h.get("lower","乾"), {})
    moving_str = ""
    if moving:
        moving_str = f'<div style="font-size:0.75rem;color:#c0392b;margin-top:4px;">动爻：{" ".join([str(m)+"爻" for m in sorted(moving)])}</div>'
    return f"""
<div style="background:#f5f4ef;border-radius:16px;padding:20px 16px;text-align:center;">
  <div style="font-size:0.75rem;color:#aaa;margin-bottom:4px;">{label}</div>
  <div style="font-size:1.3rem;font-weight:bold;color:#1a1a1a;">第 {h['no']} 卦　{h['name']}</div>
  <div style="margin:12px auto;width:fit-content;">{svg}</div>
  <div style="font-size:0.78rem;color:#888;">
    {u.get('symbol','')} {h.get('upper','')}（{u.get('nature','')}）／{l.get('symbol','')} {h.get('lower','')}（{l.get('nature','')}）
  </div>
  <div style="font-size:0.88rem;color:#555;margin-top:8px;">{h['summary']}</div>
  {moving_str}
</div>"""

def zhuxi(orig, chg, moving):
    c = len(moving)
    s = sorted(moving)

    def orig_line(n):
        t = orig.get("lines", [])
        return t[n-1] if 1 <= n <= len(t) else f"第{n}爻：请对读《周易本义》原书。"

    def chg_line(n):
        t = chg.get("lines", []) if chg else []
        return t[n-1] if 1 <= n <= len(t) else f"第{n}爻：请对读《周易本义》原书。"

    if c == 0:
        return "六爻不变", f"以本卦卦辞为主：{orig['summary']}"
    if c == 1:
        return "一爻变，以本卦变爻爻辞为主", orig_line(s[0])
    if c == 2:
        return "两爻变，以上位变爻爻辞为主", orig_line(max(s))
    if c == 3:
        return "三爻变，兼看本卦与之卦卦辞", f"本卦：{orig['summary']}　之卦：{chg['summary'] if chg else '未知'}"
    if c == 4:
        unchanged = [i for i in range(1,7) if i not in s]
        return "四爻变，以之卦下位不变爻爻辞为主", chg_line(min(unchanged))
    if c == 5:
        unchanged = [i for i in range(1,7) if i not in s]
        return "五爻变，以之卦唯一不变爻爻辞为主", chg_line(unchanged[0] if unchanged else 1)
    if c == 6:
        if orig["name"] == "乾":
            return "六爻皆变（乾）", orig.get("use","用九：见群龙无首，吉。")
        if orig["name"] == "坤":
            return "六爻皆变（坤）", orig.get("use","用六：利永贞。")
        return "六爻皆变，以之卦卦辞为主", chg["summary"] if chg else "未知"
    return "—", ""

def do_ai(question, orig, chg, moving, rule_name, rule_text):
    api_key = get_secret("OPENROUTER_API_KEY","")
    if not api_key:
        return None, "未配置 OPENROUTER_API_KEY"
    model = get_secret("MODEL_NAME","google/gemini-2.5-flash-lite")
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    prompt = f"""你是一名中文易经学习助手。

问题：{question}
本卦：第{orig['no']}卦 {orig['name']}（{orig['summary']}）
之卦：{chg['name']+'（'+chg['summary']+'）' if chg else '无'}
动爻：{moving if moving else '无'}
朱熹法取用：{rule_name} — {rule_text}

请用简体中文按以下结构输出：
1. 起卦结果概览
2. 朱熹法取用说明
3. 对问题的解读
4. 可参考的行动方向

语言自然、克制，不用神秘化，不用"必定""百分之百"措辞。"""
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":"你是一个清晰、克制的中文助手。"},
                      {"role":"user","content":prompt}],
            temperature=0.6
        )
        return r.choices[0].message.content, ""
    except Exception as e:
        return None, str(e)

def coin_to_line(three):
    h = sum(three)
    if h == 3: return 1, True,  "老阳 ○"
    if h == 2: return 1, False, "少阳"
    if h == 1: return 0, False, "少阴"
    return 0, True, "老阴 ×"

def num_to_trigram(n):
    r = n % 8
    return TRIGRAM_MAP[r if r else 8], (r if r else 8)

def moving_from_sum(t):
    r = t % 6
    return r if r else 6

# ─── 主页面 ─────────────────────────────────────────────────────────

st.markdown('<div class="main-title">易经 · 朱熹解卦</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">一阴一阳之谓道</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── 问题输入 ──────────────────────────────────────────────
question = st.text_input("", placeholder="在此输入所问之事（如：事业、学业）",
                         label_visibility="collapsed", key="question_input")

st.markdown("")

# ── 起卦方式切换 ──────────────────────────────────────────
if "method" not in st.session_state:
    st.session_state.method = "数字起卦"

col_m1, col_m2, col_m3 = st.columns([1.2, 1, 1.2])
with col_m2:
    cols = st.columns(2)
    if cols[0].button("数字起卦",
                      type="primary" if st.session_state.method == "数字起卦" else "secondary",
                      use_container_width=True):
        st.session_state.method = "数字起卦"
        if "div_result" in st.session_state:
            del st.session_state.div_result
        st.rerun()
    if cols[1].button("金钱起卦",
                      type="primary" if st.session_state.method == "金钱起卦" else "secondary",
                      use_container_width=True):
        st.session_state.method = "金钱起卦"
        if "div_result" in st.session_state:
            del st.session_state.div_result
        if "coin_lines" in st.session_state:
            del st.session_state.coin_lines
        if "coin_details" in st.session_state:
            del st.session_state.coin_details
        st.rerun()

st.markdown("")

# ══════════════════════════════════════════════════════
#  数字起卦
# ══════════════════════════════════════════════════════
if st.session_state.method == "数字起卦":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="num-label" style="text-align:center">上卦</div>', unsafe_allow_html=True)
        upper_n = st.number_input("上卦数字", min_value=1, value=6,
                                  step=1, label_visibility="collapsed", key="n_upper")
    with c2:
        st.markdown('<div class="num-label" style="text-align:center">下卦</div>', unsafe_allow_html=True)
        lower_n = st.number_input("下卦数字", min_value=1, value=3,
                                  step=1, label_visibility="collapsed", key="n_lower")
    with c3:
        st.markdown('<div class="num-label" style="text-align:center">变爻</div>', unsafe_allow_html=True)
        move_n  = st.number_input("变爻数字", min_value=1, value=9,
                                  step=1, label_visibility="collapsed", key="n_move")

    st.markdown("")
    if st.button("立即占卦", type="primary", use_container_width=True, key="cast_num"):
        un, ur = num_to_trigram(int(upper_n))
        ln, lr = num_to_trigram(int(lower_n))
        mv = moving_from_sum(int(move_n))
        moving = [mv]
        orig_hex = find_hexagram(un, ln)
        orig_l, chg_l, chg_hex = get_changed_hex(un, ln, moving)
        rule_name, rule_text = zhuxi(orig_hex, chg_hex, moving)
        st.session_state.div_result = {
            "orig_hex": orig_hex, "chg_hex": chg_hex,
            "orig_l": orig_l, "chg_l": chg_l,
            "moving": moving, "rule_name": rule_name, "rule_text": rule_text,
            "note": f"上卦：{un}（{int(upper_n)}÷8余{ur}）　下卦：{ln}（{int(lower_n)}÷8余{lr}）　动爻：第{mv}爻（{int(move_n)}÷6余{mv}）"
        }

# ══════════════════════════════════════════════════════
#  金钱起卦
# ══════════════════════════════════════════════════════
else:
    if "coin_lines" not in st.session_state:
        st.session_state.coin_lines = []
        st.session_state.coin_details = []

    done = len(st.session_state.coin_lines)
    remain = 6 - done
    line_names = ["初爻","二爻","三爻","四爻","五爻","上爻"]

    if done < 6:
        st.markdown(
            f'<div style="text-align:center;padding:28px 0 8px 0;">'
            f'<div style="width:68px;height:68px;border-radius:50%;background:#e8e8e8;'
            f'margin:0 auto 14px auto;display:flex;align-items:center;justify-content:center;'
            f'font-size:1.8rem;">🪙</div>'
            f'<div style="color:#aaa;font-size:0.95rem;">诚心默念，模拟六次掷币</div>'
            f'<div style="color:#888;font-size:0.85rem;margin-top:4px;">当前：第 {done+1} 爻（{line_names[done]}）</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.progress(int(done / 6 * 100), text=f"已投 {done} / 6 爻")
        st.markdown("")

        col_toss, col_reset = st.columns(2)
        if col_toss.button(f"掷出第 {done+1} 爻", type="primary", use_container_width=True):
            toss = [random.randint(0,1) for _ in range(3)]
            val, mv, label = coin_to_line(toss)
            st.session_state.coin_lines.append(val)
            st.session_state.coin_details.append({
                "line": done+1, "toss": toss,
                "label": label, "value": val, "moving": mv
            })
            st.rerun()
        if col_reset.button("重新起卦", use_container_width=True):
            st.session_state.coin_lines = []
            st.session_state.coin_details = []
            if "div_result" in st.session_state:
                del st.session_state.div_result
            st.rerun()

    if st.session_state.coin_details:
        st.markdown("")
        for d in st.session_state.coin_details:
            faces = " · ".join(["正" if x==1 else "反" for x in d["toss"]])
            mv_tag = "　**← 动爻**" if d["moving"] else ""
            st.write(f"第 {d['line']} 爻（{line_names[d['line']-1]}）：{faces}　→　{d['label']}{mv_tag}")

    if done == 6:
        if "div_result" not in st.session_state:
            lines = st.session_state.coin_lines
            moving = [d["line"] for d in st.session_state.coin_details if d["moving"]]
            ln_name = lines_to_trigram(lines[:3])
            un_name = lines_to_trigram(lines[3:])
            orig_hex = find_hexagram(un_name, ln_name)
            orig_l, chg_l, chg_hex = get_changed_hex(un_name, ln_name, moving)
            rule_name, rule_text = zhuxi(orig_hex, chg_hex, moving)
            st.session_state.div_result = {
                "orig_hex": orig_hex, "chg_hex": chg_hex,
                "orig_l": orig_l, "chg_l": chg_l,
                "moving": moving, "rule_name": rule_name, "rule_text": rule_text, "note": None
            }
        st.markdown("")
        if st.button("重新起卦", use_container_width=True, key="reset_coin_done"):
            st.session_state.coin_lines = []
            st.session_state.coin_details = []
            if "div_result" in st.session_state:
                del st.session_state.div_result
            st.rerun()

# ══════════════════════════════════════════════════════
#  卦象结果
# ══════════════════════════════════════════════════════
if "div_result" in st.session_state:
    res = st.session_state.div_result
    orig = res["orig_hex"]
    chg  = res["chg_hex"]
    moving = res["moving"]
    rule_name = res["rule_name"]
    rule_text = res["rule_text"]

    st.markdown("---")

    if res.get("note"):
        st.caption(res["note"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(hex_card_html(orig, res["orig_l"], moving, "本　卦"), unsafe_allow_html=True)
    with col2:
        if chg:
            st.markdown(hex_card_html(chg, res["chg_l"], [], "之　卦"), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="background:#f5f4ef;border-radius:16px;padding:20px;text-align:center;color:#aaa;height:100%;">无之卦</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 朱熹法取用")
    st.markdown(
        f'<div class="rule-box"><b>{rule_name}</b><br><br>{rule_text}</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### AI 解读")
    if not question.strip():
        st.caption("请在页面顶部输入所问之事，再生成解读。")
    else:
        if st.button("生成解读", type="primary", use_container_width=True):
            with st.spinner("解读中..."):
                ai_text, err = do_ai(question, orig, chg, moving, rule_name, rule_text)
            if err:
                st.error(err)
            else:
                st.write(ai_text)
