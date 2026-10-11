import json, random, time
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Equipment Reliability – MCQ Quiz", page_icon="⚙️", layout="centered")
BASE = Path(__file__).parent
QUESTIONS = json.loads((BASE / "questions.json").read_text(encoding="utf-8"))
TOPICS = sorted({q["topic"] for q in QUESTIONS}, key=[q["topic"] for q in QUESTIONS].index)
LETTERS = "ABCD"

st.markdown("""
<style>
.block-container{max-width:760px;padding-top:1.2rem}
.hdr{background:#fff;border-bottom:5px solid #2f8483;border-radius:18px;padding:14px;text-align:center;box-shadow:0 2px 10px #0001}
.hdr h1{font-size:1.5rem;margin:6px 0 2px;color:#18283f}.hdr p{margin:0;color:#5b6b7d;font-size:.85rem}
.pill{display:inline-block;padding:5px 16px;border-radius:99px;color:#fff;font-weight:600;font-size:.85rem;margin:8px 4px 0}
.fb-ok{background:#e6f4ec;border-left:5px solid #2e8b57;padding:10px 14px;border-radius:10px}
.fb-no{background:#f9e8e8;border-left:5px solid #b84343;padding:10px 14px;border-radius:10px}
[data-testid="stBaseButton-primary"]{background:#2f8483;border-color:#2f8483;color:#fff}
[data-testid="stBaseButton-primary"]:hover{background:#246a69;border-color:#246a69}
.stApp{background:#f1f5f7}
.big{font-size:3.2rem;font-weight:800;color:#2f8483;text-align:center;line-height:1.1}
</style>""", unsafe_allow_html=True)

import base64
LOGO = base64.b64encode((BASE / "logo.png").read_bytes()).decode()

def header():
    st.markdown(f"""<div class="hdr"><img src="data:image/png;base64,{LOGO}" style="height:58px;max-width:100%">
    <h1>Equipment Reliability — MCQ Quiz</h1>
    <p>Fundamentals • Failure Analysis • Metrics • Maintenance • Improvement</p>
    <span class="pill" style="background:#18283f">Aris</span><span class="pill" style="background:#2f8483">Lama</span>
    <span class="pill" style="background:#d09d4b;color:#18283f">Abeer Mqbaul</span></div>""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("stage", "start")

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
    if st.button("Start quiz ▶", type="primary", use_container_width=True, disabled=not pool):
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
        if r["correct"]: st.markdown(f'<div class="fb-ok">✅ <b>Correct!</b> {r["explanation"]}</div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="fb-no">❌ <b>Not quite.</b> Correct answer: <b>{r["correct_answer"]}</b><br>{r["explanation"]}</div>', unsafe_allow_html=True)
        last = i == len(qs) - 1
        if st.button("See results ▶" if last else "Next question ▶", type="primary", use_container_width=True):
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
    msg = "Excellent! 🌟" if pct >= .9 else "Great job! 👏" if pct >= .7 else "Good effort — review the explanations below." if pct >= .5 else "Keep practising — review the presentation and try again."
    (st.balloons() if pct >= .9 else None); st.info(msg)

    st.subheader("Score by topic")
    bt = res.groupby("topic", sort=False).correct.mean().mul(100).round(0)
    st.bar_chart(bt, horizontal=True)

    st.subheader("Review")
    for n, r in res.iterrows():
        with st.expander(f"{'✅' if r.correct else '❌'}  {n+1}. {r.question}"):
            st.write(f"**Your answer:** {r.your}")
            if not r.correct: st.write(f"**Correct answer:** {r.correct_answer}")
            st.caption(r.explanation)

    c1, c2 = st.columns(2)
    wrong = [q for q in QUESTIONS if q["q"] in set(res[~res.correct].question)]
    if c1.button("Retry wrong questions", use_container_width=True, disabled=not wrong):
        start(wrong, len(wrong), True, True); st.rerun()
    if c2.button("New quiz", type="primary", use_container_width=True):
        ss.stage = "start"; st.rerun()
    st.download_button("⬇ Download results (CSV)", res.to_csv(index=False).encode("utf-8-sig"),
                       "quiz_results.csv", "text/csv", use_container_width=True)
