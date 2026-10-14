import json, random, time
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Equipment Reliability – MCQ Quiz", layout="centered")
BASE = Path(__file__).parent
QUESTIONS = json.loads((BASE / "questions.json").read_text(encoding="utf-8"))
TOPICS = sorted({q["topic"] for q in QUESTIONS}, key=[q["topic"] for q in QUESTIONS].index)
LETTERS = "ABCD"

import base64

# ---------------- THEME (Day / Night) ----------------
# The app has its own theme toggle and ignores the phone/browser dark mode.
ss = st.session_state
ss.setdefault("stage", "start")
ss.setdefault("dark", False)

LIGHT = dict(bg="#f2f2f2", card="#ffffff", text="#111111", muted="#555555", border="#c8c8c8",
             ok_bg="#ebebeb", no_bg="#ffffff", no_style="dashed", scheme="light")
DARK = dict(bg="#101010", card="#1c1c1c", text="#f2f2f2", muted="#aaaaaa", border="#444444",
            ok_bg="#262626", no_bg="#101010", no_style="dashed", scheme="dark")

def apply_theme(dark):
    t = DARK if dark else LIGHT
    st.markdown(f"""
<style>
.stApp{{--bg:{t['bg']};--card:{t['card']};--text:{t['text']};--muted:{t['muted']};--border:{t['border']};color-scheme:{t['scheme']}}}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:var(--bg)!important}}
[data-testid="stHeader"]{{background:transparent!important}}
.block-container{{max-width:760px;padding-top:1.2rem}}

/* text */
.stApp :is(p,li,label,h1,h2,h3,h4,h5,h6,summary,span,div[data-testid="stMarkdownContainer"]){{color:var(--text)}}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] *{{color:var(--muted)!important}}

/* header card: fixed colours, never affected by Day/Night */
.hdr{{background:#fff;border-bottom:5px solid #000;border-radius:18px;padding:14px;text-align:center;box-shadow:0 2px 10px #0001}}
.stApp .hdr h1{{font-size:1.5rem;margin:6px 0 2px;color:#111!important}}
.stApp .hdr p{{margin:0;color:#555!important;font-size:.85rem}}
.stApp .hdr .pill{{display:inline-block;padding:5px 16px;border-radius:99px;color:#fff!important;font-weight:600;font-size:.85rem;margin:8px 4px 0}}
.stApp .hdr .pill-white{{color:#111!important;border:1.5px solid #111}}

/* Night-mode switch: fixed colours too */
.st-key-dark{{background:#fff;border:1px solid #c8c8c8;border-radius:99px;padding:4px 12px;width:fit-content;margin-left:auto}}
.st-key-dark label,.st-key-dark label *{{color:#111!important;font-weight:600}}
.st-key-dark [data-baseweb="checkbox"]>div:first-child{{background:#888!important}}
.st-key-dark [data-baseweb="checkbox"]:has(input:checked)>div:first-child{{background:#000!important}}
.st-key-dark [data-baseweb="checkbox"]>div:first-child>div{{background:#fff!important}}

/* feedback boxes */
.fb-ok{{background:{t['ok_bg']};border-left:5px solid var(--text);padding:10px 14px;border-radius:10px}}
.fb-no{{background:{t['no_bg']};border:1px solid var(--border);border-left:5px {t['no_style']} var(--text);padding:10px 14px;border-radius:10px}}
.stApp .fb-ok,.stApp .fb-ok *,.stApp .fb-no,.stApp .fb-no *{{color:var(--text)}}

/* buttons */
.stApp [data-testid="stBaseButton-primary"]{{background:var(--text);border-color:var(--text)}}
.stApp [data-testid="stBaseButton-primary"],.stApp [data-testid="stBaseButton-primary"] *{{color:var(--bg)!important}}
.stApp [data-testid="stBaseButton-primary"]:hover{{opacity:.85}}
.stApp [data-testid="stBaseButton-primary"]:disabled{{opacity:.45}}
.stApp [data-testid="stBaseButton-secondary"],.stApp [data-testid="stDownloadButton"] button{{background:var(--card);border:1px solid var(--border)}}
.stApp [data-testid="stBaseButton-secondary"] *,.stApp [data-testid="stDownloadButton"] button *{{color:var(--text)!important}}

/* inputs */
.stApp [data-baseweb="select"]>div{{background:var(--card);border-color:var(--border)}}
.stApp [data-baseweb="select"] input,.stApp [data-baseweb="select"] svg{{color:var(--text);fill:var(--text)}}
.stApp [data-testid="stSliderTickBarMin"],.stApp [data-testid="stSliderTickBarMax"],.stApp [data-testid="stSliderThumbValue"]{{color:var(--text)}}
.stApp [data-testid="stRadio"] label,.stApp [data-testid="stRadio"] label *{{color:var(--text)!important;opacity:1}}
.stApp [data-testid="stCheckbox"] label *,.stApp [data-testid="stToggle"] label *{{color:var(--text)!important}}

/* other blocks */
.stApp [data-testid="stExpander"] details{{background:var(--card);border:1px solid var(--border);border-radius:10px}}
.stApp [data-testid="stAlert"]{{background:var(--card);border:1px solid var(--border)}}
.stApp [data-testid="stAlert"] *{{color:var(--text)!important}}
.stApp [data-testid="stProgress"] *{{color:var(--text)}}
.stApp [data-testid="stVegaLiteChart"],.stApp [data-testid="stArrowVegaLiteChart"]{{background:#fff;border-radius:12px;padding:8px}}
.big{{font-size:3.2rem;font-weight:800;color:var(--text)!important;text-align:center;line-height:1.1}}
/* black & white accents */
.stApp [data-testid="stSlider"] [role="slider"]{{background:var(--text)!important;border-color:var(--text)!important}}
.stApp [data-baseweb="tag"]{{background:var(--text)!important}}
.stApp [data-baseweb="tag"] *{{color:var(--bg)!important}}
.stApp [data-baseweb="radio"]>div:first-child{{border-color:var(--text)!important}}
</style>""", unsafe_allow_html=True)

apply_theme(ss.dark)

_, tcol = st.columns([3, 1])
tcol.toggle("Night mode", key="dark")

_logo = BASE / "logo.png"
LOGO = base64.b64encode(_logo.read_bytes()).decode() if _logo.exists() else ""
LOGO_TAG = f'<img src="data:image/png;base64,{LOGO}" style="height:58px;max-width:100%">' if LOGO else ""

def header():
    st.markdown(f"""<div class="hdr">{LOGO_TAG}
    <h1>Equipment Reliability — MCQ Quiz</h1>
    <p>Fundamentals • Failure Analysis • Metrics • Maintenance • Improvement</p>
    <span class="pill" style="background:#000">Aris</span><span class="pill" style="background:#444">Lama</span>
    <span class="pill pill-white" style="background:#fff">Abeer Mqbaul</span></div>""", unsafe_allow_html=True)

def start(pool, n, shuffle_q, shuffle_o):
    pool = [dict(q, options=list(q["options"])) for q in pool]
    if shuffle_q: random.shuffle(pool)
    pool = pool[:n]
    for q in pool:
        if shuffle_o:
            correct = q["options"][q["answer"]]
            random.shuffle(q["options"]); q["answer"] = q["options"].index(correct)
    ss.update(stage="quiz", qs=pool, i=0, results=[], checked=False, t0=time.time(), run=ss.get("run", 0) + 1)

def pick(i, key):
    return ss.get(key)

header()

# ---------------- START ----------------
if ss.stage == "start":
    st.subheader("Quiz settings")
    sel = st.multiselect("Topics", TOPICS, default=TOPICS)
    pool = [q for q in QUESTIONS if q["topic"] in sel]
    n = st.slider("Number of questions", 1, max(1, len(pool)), len(pool)) if pool else 0
    c1, c2 = st.columns(2)
    sq = c1.toggle("Shuffle questions", True)
    so = c2.toggle("Shuffle answer options", True)
    st.caption(f"{len(pool)} questions available in the selected topics.")
    if st.button("Start quiz →", type="primary", use_container_width=True, disabled=not pool):
        start(pool, n, sq, so); st.rerun()

# ---------------- QUIZ ----------------
elif ss.stage == "quiz":
    qs, i = ss.qs, ss.i
    q = qs[i]
    st.progress(i / len(qs), text=f"Question {i+1} of {len(qs)}  •  Score: {sum(r['correct'] for r in ss.results)}")
    st.caption(f"Topic: {q['topic']}")
    st.markdown(f"### {i+1}. {q['q']}")
    key = f"ans_{ss.run}_{i}"
    labels = [f"{LETTERS[k]}.  {t}" for k, t in enumerate(q["options"])]
    choice = st.radio("Choose one answer", labels, index=None, key=key, disabled=ss.checked, label_visibility="collapsed")
    if not ss.checked:
        if st.button("Check answer", type="primary", use_container_width=True, disabled=choice is None):
            k = labels.index(choice)
            ss.results.append(dict(topic=q["topic"], question=q["q"], your=q["options"][k],
                                   correct_answer=q["options"][q["answer"]], correct=k == q["answer"], explanation=q["explanation"]))
            ss.checked = True; st.rerun()
    else:
        r = ss.results[-1]
        if r["correct"]: st.markdown(f'<div class="fb-ok">✓ <b>Correct!</b> {r["explanation"]}</div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="fb-no">✗ <b>Not quite.</b> Correct answer: <b>{r["correct_answer"]}</b><br>{r["explanation"]}</div>', unsafe_allow_html=True)
        last = i == len(qs) - 1
        if st.button("See results →" if last else "Next question →", type="primary", use_container_width=True):
            if last: ss.stage, ss.elapsed = "end", time.time() - ss.t0
            else: ss.i += 1; ss.checked = False
            st.rerun()
    if st.button("Quit quiz", type="secondary"):
        ss.stage = "start"; st.rerun()

# ---------------- END ----------------
else:
    res = pd.DataFrame(ss.results)
    score, total = int(res.correct.sum()), len(res)
    pct = score / total
    st.markdown(f'<div class="big">{score} / {total}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center'>{pct:.0%} • Time: {int(ss.elapsed//60)}m {int(ss.elapsed%60)}s</p>", unsafe_allow_html=True)
    msg = "Excellent!" if pct >= .9 else "Great job!" if pct >= .7 else "Good effort — review the explanations below." if pct >= .5 else "Keep practising — review the presentation and try again."
    st.info(msg)

    st.subheader("Score by topic")
    bt = res.groupby("topic", sort=False).correct.mean().mul(100).round(0)
    st.bar_chart(bt, horizontal=True, color="#000000")

    st.subheader("Review")
    for n, r in res.iterrows():
        with st.expander(f"{'✓' if r.correct else '✗'}  {n+1}. {r.question}"):
            st.write(f"**Your answer:** {r.your}")
            if not r.correct: st.write(f"**Correct answer:** {r.correct_answer}")
            st.caption(r.explanation)

    c1, c2 = st.columns(2)
    wrong = [q for q in QUESTIONS if q["q"] in set(res[~res.correct].question)]
    if c1.button("Retry wrong questions", use_container_width=True, disabled=not wrong):
        start(wrong, len(wrong), True, True); st.rerun()
    if c2.button("New quiz", type="primary", use_container_width=True):
        ss.stage = "start"; st.rerun()
    st.download_button("↓ Download results (CSV)", res.to_csv(index=False).encode("utf-8-sig"),
                       "quiz_results.csv", "text/csv", use_container_width=True)
