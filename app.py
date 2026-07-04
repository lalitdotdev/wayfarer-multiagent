import os
import re
import io
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage
from main import app

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

st.set_page_config(
    page_title="Wayfarer — AI Travel Concierge",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
#  Route-map palette — every agent is a different "line" that converges
#  into a single boarding pass at the end.
#    bg / surface   → night-sky navy
#    --blue          flight line     #4f8ff7
#    --amber         hotel line      #ffb454
#    --violet        itinerary line  #b18cff
#    --teal          final / arrival #34d1b8
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root{
  --bg:#05080d;
  --bg-soft:#080d15;
  --surface:#0c141f;
  --surface-2:#101b29;
  --border:#1c2c40;
  --border-soft:#152234;
  --text:#eef4fb;
  --text-dim:#93a8c2;
  --text-faint:#54687f;

  --blue:#4f8ff7;    --blue-dim:#1c3357;
  --amber:#ffb454;   --amber-dim:#4a3110;
  --violet:#b18cff;  --violet-dim:#332a55;
  --teal:#34d1b8;    --teal-dim:#123832;

  --font-display:'Space Grotesk', sans-serif;
  --font-body:'Inter', sans-serif;
  --font-mono:'JetBrains Mono', monospace;
}

@media (prefers-reduced-motion: reduce){
  *{ animation-duration:0.01ms !important; animation-iteration-count:1 !important; transition-duration:0.01ms !important; }
}

html, body, .stApp{
  font-family: var(--font-body);
  background:var(--bg) !important;
  color:var(--text);
}

/* ── ambient aurora background ── */
.stApp::before{
  content:"";
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(ellipse 700px 420px at 12% -8%, rgba(79,143,247,0.16), transparent 60%),
    radial-gradient(ellipse 640px 400px at 92% 6%, rgba(177,140,255,0.13), transparent 60%),
    radial-gradient(ellipse 600px 500px at 50% 105%, rgba(52,209,184,0.09), transparent 60%);
  animation:auroraDrift 24s ease-in-out infinite alternate;
}
@keyframes auroraDrift{
  0%{ opacity:0.85; transform:translateY(0px); }
  100%{ opacity:1; transform:translateY(14px); }
}
.stApp::after{
  content:"";
  position:fixed; inset:0; z-index:0; pointer-events:none; opacity:0.035;
  background-image:radial-gradient(rgba(255,255,255,0.9) 0.6px, transparent 0.6px);
  background-size:26px 26px;
}
.main .block-container{ position:relative; z-index:1; max-width:1180px; padding-top:1.6rem; }

/* ── custom scrollbar ── */
::-webkit-scrollbar{ width:10px; height:10px; }
::-webkit-scrollbar-track{ background:var(--bg); }
::-webkit-scrollbar-thumb{ background:#1e3350; border-radius:6px; border:2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover{ background:var(--blue); }

/* ══════════════ HERO — departure board ══════════════ */
.hero{
  position:relative;
  border:1px solid var(--border);
  border-radius:20px;
  padding:2.4rem 2.6rem 2.1rem;
  margin-bottom:1.6rem;
  background:
    linear-gradient(155deg, rgba(79,143,247,0.09), rgba(177,140,255,0.05) 55%, transparent),
    var(--surface);
  overflow:hidden;
}
.hero::before{
  content:"";
  position:absolute; top:-40%; right:-10%; width:380px; height:380px;
  background:radial-gradient(circle, rgba(79,143,247,0.22), transparent 70%);
  filter:blur(10px);
  animation:pulseGlow 6s ease-in-out infinite;
}
@keyframes pulseGlow{
  0%,100%{ opacity:0.6; transform:scale(1); }
  50%{ opacity:1; transform:scale(1.08); }
}
.hero-eyebrow{
  font-family:var(--font-mono);
  font-size:0.72rem; font-weight:600; letter-spacing:0.22em; text-transform:uppercase;
  color:var(--blue); display:flex; align-items:center; gap:0.5rem; margin-bottom:0.9rem;
}
.hero-eyebrow .dot{ width:6px; height:6px; border-radius:50%; background:var(--teal); box-shadow:0 0 8px var(--teal); animation:blink 2s ease-in-out infinite; }
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:0.25;} }
.hero-title{
  font-family:var(--font-display);
  font-size:2.7rem; font-weight:700; letter-spacing:-0.02em;
  color:var(--text); margin:0 0 0.55rem; line-height:1.08;
}
.hero-title .accent{ color:var(--blue); }
.hero-sub{ color:var(--text-dim); font-size:1rem; max-width:600px; line-height:1.6; }
.hero-route{
  display:flex; align-items:center; gap:0.6rem; margin-top:1.4rem;
  font-family:var(--font-mono); font-size:0.78rem; color:var(--text-faint);
}
.hero-route .seg{ flex:1; height:1px; background:repeating-linear-gradient(90deg, var(--border) 0 6px, transparent 6px 12px); position:relative; }
.hero-route .plane{ font-size:0.9rem; }

/* ══════════════ destination strip ══════════════ */
.dest-strip{ display:flex; gap:0.7rem; margin:0 0 1.7rem; }
.dest-card{
  flex:1; position:relative; border-radius:14px; overflow:hidden; height:96px;
  border:1px solid var(--border-soft); transition:transform 0.25s ease, border-color 0.25s ease;
}
.dest-card:hover{ transform:translateY(-3px); border-color:var(--blue); }
.dest-card img{ width:100%; height:100%; object-fit:cover; filter:brightness(0.5) saturate(1.05); }
.dest-card .tag{
  position:absolute; bottom:8px; left:10px; color:#fff; font-size:0.78rem; font-weight:600;
  font-family:var(--font-body); text-shadow:0 1px 6px rgba(0,0,0,0.6);
}

/* ══════════════ input card ══════════════ */
.input-label{
  font-family:var(--font-mono); color:var(--blue); font-size:0.75rem; font-weight:600;
  letter-spacing:0.14em; text-transform:uppercase; margin-bottom:0.55rem;
}
.stTextArea textarea{
  background:var(--surface) !important; border:1px solid var(--border) !important;
  border-radius:14px !important; color:var(--text) !important; font-size:0.97rem !important;
  font-family:var(--font-body) !important; resize:none !important; padding:1rem !important;
}
.stTextArea textarea:focus{ border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(79,143,247,0.16) !important; }
.stTextArea textarea::placeholder{ color:var(--text-faint) !important; }

/* quick chips (gate buttons) */
div[data-testid="column"] .stButton > button{
  background:var(--surface) !important; color:var(--text-dim) !important;
  border:1px solid var(--border) !important; border-radius:20px !important;
  padding:0.4rem 1rem !important; font-size:0.82rem !important; font-weight:500 !important;
  box-shadow:none !important; transition:all 0.2s ease !important;
}
div[data-testid="column"] .stButton > button:hover{
  border-color:var(--blue) !important; color:var(--text) !important;
  background:var(--blue-dim) !important; transform:translateY(-1px) !important;
}

/* primary generate button — the one full-width button */
div[data-testid="stButton"]:has(button[kind="secondaryFormSubmit"]),
.generate-btn div[data-testid="stButton"] > button{ }
.generate-btn div[data-testid="stButton"] > button{
  background:linear-gradient(120deg, var(--blue) 0%, #2f66c9 55%, #1c3f8f 100%) !important;
  color:#fff !important; border:none !important; border-radius:14px !important;
  padding:0.95rem 2.5rem !important; font-size:1.04rem !important; font-weight:700 !important;
  letter-spacing:0.02em !important; width:100% !important; font-family:var(--font-display) !important;
  box-shadow:0 0 0 1px rgba(79,143,247,0.25), 0 8px 28px rgba(79,143,247,0.28) !important;
  transition:all 0.25s ease !important; position:relative; overflow:hidden;
}
.generate-btn div[data-testid="stButton"] > button:hover{
  box-shadow:0 0 0 1px rgba(79,143,247,0.4), 0 10px 36px rgba(79,143,247,0.45) !important;
  transform:translateY(-2px) !important;
}
.generate-btn div[data-testid="stButton"] > button:active{ transform:translateY(0) !important; }

/* ══════════════ route tracker (signature element) ══════════════ */
.tracker{ margin:0.4rem 0 1.8rem; padding:1.4rem 1.6rem; background:var(--surface);
  border:1px solid var(--border); border-radius:16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.tracker-label{ font-family:var(--font-mono); font-size:0.72rem; letter-spacing:0.16em;
  text-transform:uppercase; color:var(--text-faint); margin-bottom:1.1rem; }
.tracker-row{ display:flex; align-items:center; }
.tracker-node{ display:flex; flex-direction:column; align-items:center; gap:0.5rem; width:64px; flex-shrink:0; }
.tracker-node .ring{
  width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:1.1rem; background:var(--bg-soft); border:2px solid var(--border);
  color:var(--text-faint); transition:all 0.4s ease;
}
.tracker-node.done .ring{ border-color:var(--_c); color:#fff; background:var(--_c);
  box-shadow:0 0 16px var(--_c); animation:nodePop 0.5s ease; }
.tracker-node.active .ring{ border-color:var(--_c); color:var(--_c); background:var(--bg-soft);
  box-shadow:0 0 12px var(--_c); animation:pulseActive 1.5s infinite alternate; }
@keyframes pulseActive {
  0% { transform: scale(1); box-shadow: 0 0 8px var(--_c); }
  100% { transform: scale(1.08); box-shadow: 0 0 20px var(--_c); }
}
@keyframes nodePop{ 0%{ transform:scale(0.6); opacity:0; } 60%{ transform:scale(1.12); } 100%{ transform:scale(1); opacity:1; } }
.tracker-node .name{ font-size:0.68rem; color:var(--text-faint); text-align:center; font-weight:500; }
.tracker-node.done .name{ color:var(--text-dim); }
.tracker-node.active .name{ color:var(--text); font-weight:600; }
.tracker-line{ flex:1; height:2px; background:var(--border); margin:0 -6px 26px; position:relative; overflow:hidden; }
.tracker-line.done::after{
  content:""; position:absolute; inset:0; background:var(--_c); transform-origin:left;
  animation:fillLine 0.6s ease forwards;
}
.tracker-line.active::after{
  content:""; position:absolute; inset:0; background:linear-gradient(90deg, var(--_c), transparent);
  animation:pulseLine 1.5s infinite linear; transform-origin:left;
}
@keyframes fillLine{ from{ transform:scaleX(0); } to{ transform:scaleX(1); } }
@keyframes pulseLine {
  0% { transform: scaleX(0); opacity: 0.3; }
  50% { transform: scaleX(1); opacity: 0.8; }
  100% { transform: scaleX(1); opacity: 0; }
}

/* ══════════════ custom loader ══════════════ */
.loader-container {
  background: var(--surface);
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  padding: 2.2rem 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
  animation: cardIn 0.5s ease both;
}
.loader-container::before {
  content: ""; position: absolute; top: 0; left: -100%; width: 100%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--blue), transparent);
  animation: scanning 2.2s infinite linear;
}
@keyframes scanning {
  0% { left: -100%; }
  100% { left: 100%; }
}
.loader-spinner {
  width: 44px; height: 44px;
  border: 3px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  margin: 0 auto 1.2rem;
  animation: spin 1s infinite linear;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loader-text {
  font-family: var(--font-display);
  font-size: 1.15rem; font-weight: 600; color: var(--text);
  margin-bottom: 0.4rem;
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
}
.loader-sub {
  font-size: 0.86rem; color: var(--text-dim);
}

/* ══════════════ section headers ══════════════ */
.sec-head{ display:flex; align-items:center; gap:0.65rem; margin:2.1rem 0 0.9rem; }
.sec-head .bar{ width:3px; height:18px; background:var(--blue); border-radius:2px; }
.sec-head span{ font-family:var(--font-display); font-size:1.12rem; font-weight:600; color:var(--text); }

/* ══════════════ agent result cards ══════════════ */
.agent-card{
  background:var(--surface); border:1px solid var(--border-soft); border-left:4px solid var(--_c);
  border-radius:14px; padding:1.2rem 1.4rem 1.3rem; margin-bottom:1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  animation:cardIn 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes cardIn{ from{ opacity:0; transform:translateY(15px); } to{ opacity:1; transform:translateY(0); } }
.agent-card__head{ display:flex; align-items:center; gap:0.6rem; margin-bottom:0.7rem; }
.agent-card__icon{ font-size:1.25rem; }
.agent-card__label{ font-family:var(--font-display); font-weight:600; font-size:1.02rem; color:var(--text); flex:1; }
.agent-card__badge{ font-family:var(--font-mono); font-size:0.68rem; color:var(--_c); background:var(--_cd);
  padding:0.2rem 0.6rem; border-radius:6px; letter-spacing:0.06em; font-weight: 600; }
.agent-card__body{ color:#c7d6e8; font-size:0.94rem; line-height:1.72; }
.agent-card__body p{ margin:0 0 0.6rem; }
.agent-card__body ul{ margin:0 0 0.7rem; padding-left:1.25rem; }
.agent-card__body li{ margin-bottom:0.35rem; }
.agent-card__body h2,.agent-card__body h3,.agent-card__body h4{ font-family:var(--font-display); color:var(--text); margin:0.8rem 0 0.4rem; }
.agent-card__body strong{ color:var(--text); }

/* boarding lane state (before result arrives) */
.boarding-line{
  display:flex; align-items:center; gap:0.7rem; padding:0.9rem 1.2rem; background:var(--surface);
  border:1px dashed var(--border); border-radius:12px; color:var(--text-faint); font-family:var(--font-mono);
  font-size:0.83rem; margin-bottom:1rem;
}
.boarding-line .plane-fly{ display:inline-block; animation:flyAcross 1.6s ease-in-out infinite; }
@keyframes flyAcross{ 0%,100%{ transform:translateX(0); } 50%{ transform:translateX(6px); } }

/* ══════════════ metrics ══════════════ */
.metric-row{ display:flex; gap:1rem; margin:1.7rem 0; }
.metric-box{ flex:1; background:var(--surface); border:1px solid var(--border-soft); border-radius:14px;
  padding:1.1rem 1.2rem; text-align:center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.metric-val{ font-family:var(--font-display); font-size:1.9rem; font-weight:700; color:var(--blue); }
.metric-lbl{ font-family:var(--font-mono); font-size:0.7rem; color:var(--text-faint); margin-top:0.25rem;
  text-transform:uppercase; letter-spacing:0.1em; }

/* ══════════════ boarding pass — final ticket ══════════════ */
.ticket{
  position:relative; background:linear-gradient(155deg, #0e1e33 0%, #07101a 100%);
  border:1px solid var(--border); border-radius:20px; padding:0; overflow:hidden;
  box-shadow:0 24px 72px rgba(0,0,0,0.45);
}
.ticket-head{
  display:flex; justify-content:space-between; align-items:center; padding:1.4rem 1.8rem;
  background:linear-gradient(120deg, rgba(52,209,184,0.18), rgba(79,143,247,0.12));
}
.ticket-head .brand{ font-family:var(--font-display); font-weight:700; color:var(--text); letter-spacing:0.02em; }
.ticket-head .brand span{ color:var(--teal); }
.ticket-head .status{ font-family:var(--font-mono); font-size:0.72rem; color:var(--teal); letter-spacing:0.1em;
  border:1px solid var(--teal-dim); background:var(--teal-dim); padding:0.28rem 0.7rem; border-radius:20px;
  font-weight: 600; box-shadow: 0 0 10px rgba(52,209,184,0.2); }
.ticket-meta {
  display: flex; justify-content: space-between; padding: 1.1rem 1.8rem;
  font-family: var(--font-mono); font-size: 0.76rem; color: var(--text-dim);
  border-bottom: 1px dashed var(--border); background: rgba(255,255,255,0.01);
}
.ticket-meta strong { color: var(--blue); }
.ticket-perf{ position:relative; height:1px; background:repeating-linear-gradient(90deg, var(--border) 0 8px, transparent 8px 16px); margin:0 1.8rem; }
.ticket-perf::before,.ticket-perf::after{
  content:""; position:absolute; top:-9px; width:18px; height:18px; border-radius:50%; background:var(--bg);
}
.ticket-perf::before{ left:-1.8rem; } .ticket-perf::after{ right:-1.8rem; }
.ticket-body{ padding:1.6rem 2rem 2rem; color:#d3e0ef; font-size:0.98rem; line-height:1.78; }
.ticket-body p{ margin:0 0 0.75rem; } .ticket-body ul{ padding-left:1.3rem; margin:0 0 0.8rem; }
.ticket-body li{ margin-bottom:0.4rem; }
.ticket-body h2,.ticket-body h3,.ticket-body h4{ font-family:var(--font-display); color:#fff; margin:1rem 0 0.5rem; }
.ticket-body strong{ color:#fff; }
.ticket-barcode {
  display: flex; justify-content: center; align-items: center; gap: 2px;
  padding: 1.6rem 0; background: rgba(255,255,255,0.015); border-top: 1px dashed var(--border);
}
.ticket-barcode span {
  display: inline-block; height: 38px; background: var(--text-faint);
}

/* ══════════════ save bar ══════════════ */
.save-bar{
  background:var(--surface); border:1px solid var(--border-soft); border-radius:10px;
  padding:0.85rem 1.2rem; color:var(--text-dim); font-size:0.86rem; font-family:var(--font-mono);
  display:flex; align-items:center; height:100%;
}
.save-bar code{ color:var(--blue); background:var(--bg-soft); padding:0.1rem 0.35rem; border-radius:4px; }

/* download buttons */
div[data-testid="stDownloadButton"] > button{
  background:var(--surface-2) !important; color:var(--text) !important;
  border:1px solid var(--border) !important; border-radius:12px !important;
  font-weight:600 !important; transition:all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover{ border-color:var(--blue) !important; color:var(--blue) !important; }

/* ══════════════ sidebar — boarding-pass stub ══════════════ */
section[data-testid="stSidebar"]{ background:var(--bg-soft) !important; border-right:1px solid var(--border-soft) !important; }
.side-brand{ font-family:var(--font-display); font-weight:700; font-size:1.2rem; color:var(--text); margin:0.2rem 0 0.2rem; }
.side-brand span{ color:var(--blue); }
.side-tag{ font-family:var(--font-mono); font-size:0.7rem; color:var(--text-faint); letter-spacing:0.1em; margin-bottom:1.3rem; }
.side-title{ color:var(--text-dim); font-family:var(--font-mono); font-size:0.72rem; font-weight:600;
  text-transform:uppercase; letter-spacing:0.12em; margin:1.3rem 0 0.6rem; }
.stack-chip{ background:var(--surface); border:1px solid var(--border-soft); border-radius:8px;
  padding:0.5rem 0.8rem; margin-bottom:0.4rem; font-size:0.82rem; color:var(--text-dim); }

.pipe-item{ display:flex; align-items:center; gap:0.6rem; padding:0.5rem 0; position:relative; }
.pipe-item .num{ width:22px; height:22px; border-radius:50%; background:var(--surface); border:1px solid var(--border);
  color:var(--text-faint); font-family:var(--font-mono); font-size:0.68rem; display:flex; align-items:center;
  justify-content:center; flex-shrink:0; }
.pipe-item .label{ font-size:0.83rem; color:var(--text-dim); }
.pipe-item:not(:last-child)::after{
  content:""; position:absolute; left:11px; top:28px; width:1px; height:16px; background:var(--border);
}

section[data-testid="stSidebar"] input[type="text"]{
  background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:9px !important;
  color:var(--text) !important;
}
section[data-testid="stSidebar"] input[type="text"]:focus{ border-color:var(--blue) !important; }
section[data-testid="stSidebar"] label{ color:var(--blue) !important; font-size:0.75rem !important;
  font-weight:600 !important; letter-spacing:0.08em !important; font-family:var(--font-mono) !important; }

/* general */
.stAlert{ background:var(--surface) !important; border:1px solid var(--border-soft) !important; border-radius:12px !important; }
.stAlert p{ color:var(--text) !important; }
#MainMenu, footer, header{ visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ── tiny markdown → html (keeps result cards fully custom-styled) ──────────
def _esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _inline(t: str) -> str:
    t = _esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    return t

def md_to_html(md_text: str) -> str:
    if not md_text:
        return "<p>—</p>"
    out, in_list = [], False
    for raw in md_text.split("\n"):
        line = raw.strip()
        if not line:
            if in_list:
                out.append("</ul>"); in_list = False
            continue
        if line.startswith(("- ", "* ")):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>"); in_list = False
        if line.startswith("### "):
            out.append(f"<h4>{_inline(line[4:])}</h4>")
        elif line.startswith("## "):
            out.append(f"<h3>{_inline(line[3:])}</h3>")
        elif line.startswith("# "):
            out.append(f"<h2>{_inline(line[2:])}</h2>")
        else:
            out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


# ── PDF generation helpers (unchanged logic, palette aligned) ──────────────

def _inline_markdown_to_reportlab(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def markdown_to_flowables(md_text: str, styles) -> list:
    flowables = []
    if not md_text:
        return flowables
    lines = md_text.split("\n")
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line.strip():
            flowables.append(Spacer(1, 6))
            continue
        stripped = line.strip()
        if stripped.startswith("### "):
            flowables.append(Paragraph(_inline_markdown_to_reportlab(stripped[4:]), styles["H3"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(_inline_markdown_to_reportlab(stripped[3:]), styles["H2"]))
        elif stripped.startswith("# "):
            flowables.append(Paragraph(_inline_markdown_to_reportlab(stripped[2:]), styles["H1"]))
        elif stripped.startswith(("- ", "* ")):
            content = _inline_markdown_to_reportlab(stripped[2:])
            flowables.append(Paragraph(f"&bull;&nbsp;&nbsp;{content}", styles["Bullet"]))
        else:
            flowables.append(Paragraph(_inline_markdown_to_reportlab(stripped), styles["Body"]))
    return flowables


def build_pdf_styles():
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle("TitleCustom", parent=base["Title"], fontSize=22,
                                 textColor=colors.HexColor("#1c3f8f"), spaceAfter=4, alignment=TA_CENTER),
        "SubTitle": ParagraphStyle("SubTitleCustom", parent=base["Normal"], fontSize=10,
                                    textColor=colors.HexColor("#5a7a96"), spaceAfter=16, alignment=TA_CENTER),
        "Section": ParagraphStyle("SectionCustom", parent=base["Heading2"], fontSize=14,
                                   textColor=colors.HexColor("#1c3f8f"), spaceBefore=18, spaceAfter=8),
        "H1": ParagraphStyle("H1Custom", parent=base["Heading1"], fontSize=15,
                              textColor=colors.HexColor("#0e2a44"), spaceBefore=10, spaceAfter=6),
        "H2": ParagraphStyle("H2Custom", parent=base["Heading2"], fontSize=13,
                              textColor=colors.HexColor("#12395c"), spaceBefore=8, spaceAfter=6),
        "H3": ParagraphStyle("H3Custom", parent=base["Heading3"], fontSize=11.5,
                              textColor=colors.HexColor("#1a4a75"), spaceBefore=6, spaceAfter=4),
        "Body": ParagraphStyle("BodyCustom", parent=base["Normal"], fontSize=10, leading=15,
                                textColor=colors.HexColor("#1c1c1c"), spaceAfter=4),
        "Bullet": ParagraphStyle("BulletCustom", parent=base["Normal"], fontSize=10, leading=15,
                                  leftIndent=12, textColor=colors.HexColor("#1c1c1c"), spaceAfter=2),
        "MetaLabel": ParagraphStyle("MetaLabelCustom", parent=base["Normal"], fontSize=9,
                                     textColor=colors.HexColor("#5a7a96")),
        "MetaValue": ParagraphStyle("MetaValueCustom", parent=base["Normal"], fontSize=9,
                                     textColor=colors.HexColor("#1c1c1c")),
    }


def generate_travel_plan_pdf(user_query: str, thread_id: str, collected: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                             leftMargin=0.75 * inch, rightMargin=0.75 * inch, title="Wayfarer Travel Plan")
    styles = build_pdf_styles()
    story = [
        Paragraph("✦ Wayfarer", styles["Title"]),
        Paragraph("Your Generated Travel Plan", styles["SubTitle"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dce6f0"), spaceAfter=12),
    ]
    meta_data = [
        [Paragraph("Query", styles["MetaLabel"]), Paragraph(user_query or "N/A", styles["MetaValue"])],
        [Paragraph("Generated", styles["MetaLabel"]), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles["MetaValue"])],
        [Paragraph("User ID", styles["MetaLabel"]), Paragraph(thread_id or "N/A", styles["MetaValue"])],
    ]
    meta_table = Table(meta_data, colWidths=[1.2 * inch, 5.3 * inch])
    meta_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4)]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    sections = [
        ("✈ Flight Information", collected.get("flight_results", "")),
        ("🏨 Hotel Information", collected.get("hotel_results", "")),
        ("🗓 Itinerary", collected.get("itinerary", "")),
        ("🧠 Final Travel Plan", collected.get("final_response", "")),
    ]
    for heading, content in sections:
        story.append(Paragraph(heading, styles["Section"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5edf5"), spaceAfter=8))
        story.extend(markdown_to_flowables(content or "N/A", styles))
        story.append(Spacer(1, 8))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dce6f0"), spaceBefore=6, spaceAfter=6))
    story.append(Paragraph(f"LLM Calls: {collected.get('llm_calls', 0)}", styles["MetaLabel"]))
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ── waypoint config (the route-map motif) ───────────────────────────────────
WAYPOINTS = [
    ("flight_agent",    "✈",  "Flights",   "blue"),
    ("hotel_agent",     "🏨", "Stays",     "amber"),
    ("itinerary_agent", "🗺",  "Itinerary", "violet"),
    ("final_agent",     "✦",  "Boarding",  "teal"),
]
COLOR_HEX = {"blue": "#4f8ff7", "amber": "#ffb454", "violet": "#b18cff", "teal": "#34d1b8"}
COLOR_DIM = {"blue": "#1c3357", "amber": "#4a3110", "violet": "#332a55", "teal": "#123832"}


AGENT_LOADER_INFO = {
    "flight_agent": ("✈️", "Flight Agent", "Scouting aviation networks & real-time flight fares..."),
    "hotel_agent": ("🏨", "Hotel Agent", "Analyzing stay options, pricing, and guest reviews..."),
    "itinerary_agent": ("🗺️", "Itinerary Agent", "Crafting a day-by-day travel map & logistics pipeline..."),
    "final_agent": ("✦", "Final Concierge", "Stitching responses & issuing your digital boarding pass..."),
}


def render_loader(agent_key: str) -> str:
    if agent_key not in AGENT_LOADER_INFO:
        return ""
    icon, name, desc = AGENT_LOADER_INFO[agent_key]
    color = "blue"
    for k, _, _, col in WAYPOINTS:
        if k == agent_key:
            color = col
            break
    c = COLOR_HEX[color]
    return f"""
    <div class="loader-container" style="border-top: 3px solid {c};">
      <div class="loader-spinner" style="border-top-color: {c};"></div>
      <div class="loader-text"><span>{icon}</span> {name} is processing...</div>
      <div class="loader-sub">{desc}</div>
    </div>
    """


def render_barcode() -> str:
    import random
    widths = [1, 2, 3, 4]
    spans = []
    # Generates a pseudo-barcode
    random.seed(42)  # consistent barcode
    for _ in range(40):
        w = random.choice(widths)
        op = random.choice([0.15, 0.45, 0.75])
        spans.append(f'<span style="width:{w}px; opacity:{op};"></span>')
    return f'<div class="ticket-barcode">{"".join(spans)}</div>'


def render_tracker(done_keys: set) -> str:
    nodes_html = []
    # Find the active node key (first waypoint not done)
    active_key = None
    for key, _, _, _ in WAYPOINTS:
        if key not in done_keys:
            active_key = key
            break
            
    for i, (key, icon, name, color) in enumerate(WAYPOINTS):
        is_done = key in done_keys
        is_active = key == active_key and len(done_keys) < len(WAYPOINTS)
        c = COLOR_HEX[color]
        
        status_class = ""
        if is_done:
            status_class = "done"
        elif is_active:
            status_class = "active"
            
        nodes_html.append(
            f'<div class="tracker-node {status_class}" style="--_c:{c}">'
            f'<div class="ring">{icon}</div><div class="name">{name}</div></div>'
        )
        if i < len(WAYPOINTS) - 1:
            line_done = is_done
            line_active = is_active and not (WAYPOINTS[i+1][0] in done_keys)
            line_status = "done" if line_done else ("active" if line_active else "")
            nodes_html.append(f'<div class="tracker-line {line_status}" style="--_c:{c}"></div>')
            
    return (
        '<div class="tracker"><div class="tracker-label">Live agent route</div>'
        f'<div class="tracker-row">{"".join(nodes_html)}</div></div>'
    )


def render_agent_card(icon: str, label: str, badge: str, color: str, body_md: str, delay_ms: int = 0) -> str:
    c, cd = COLOR_HEX[color], COLOR_DIM[color]
    return (
        f'<div class="agent-card" style="--_c:{c}; --_cd:{cd}; animation-delay:{delay_ms}ms">'
        f'<div class="agent-card__head"><span class="agent-card__icon">{icon}</span>'
        f'<span class="agent-card__label">{label}</span>'
        f'<span class="agent-card__badge">{badge}</span></div>'
        f'<div class="agent-card__body">{md_to_html(body_md)}</div></div>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="side-brand">✦ <span>Wayfarer</span></div>'
        '<div class="side-tag">MULTI-AGENT TRAVEL CONCIERGE</div>',
        unsafe_allow_html=True,
    )

    thread_id = st.text_input("Passenger ID", value="lalitsharma_user",
                               help="Your session ID — keeps travel history across queries")

    st.markdown('<div class="side-title">Powered by</div>', unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='stack-chip'>{tech}</div>", unsafe_allow_html=True)

    st.markdown('<div class="side-title">Agent route</div>', unsafe_allow_html=True)
    pipe_html = "".join(
        f'<div class="pipe-item"><div class="num">{i+1}</div><div class="label">{icon} {name}</div></div>'
        for i, (_, icon, name, _) in enumerate(WAYPOINTS)
    )
    st.markdown(pipe_html, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow"><span class="dot"></span> Multi-agent system · live</div>
  <div class="hero-title">Plan a trip that feels<br><span class="accent">planned by someone who cares.</span></div>
  <div class="hero-sub">Four specialized agents work in parallel — searching flights, scouting stays,
  drafting your itinerary, and stitching it all into one boarding pass.</div>
  <div class="hero-route">
    <span>YOU</span><span class="seg"></span><span class="plane">✈</span><span class="seg"></span><span>ANYWHERE</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Destination strip ────────────────────────────────────────────────────
DESTINATIONS = [
    ("Tokyo",   "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("Paris",   "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("Rome",    "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("Dubai",   "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]
st.markdown(
    '<div class="dest-strip">' +
    "".join(f'<div class="dest-card"><img src="{u}"/><div class="tag">{n}</div></div>' for n, u in DESTINATIONS) +
    '</div>',
    unsafe_allow_html=True,
)

# ── Input ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-label">🗺 Describe your trip</div>', unsafe_allow_html=True)

QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
qcols = st.columns(len(QUICK))
quick_fill = ""
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}"):
            quick_fill = label

user_query = st.text_area(
    "Describe your trip",
    value=quick_fill,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    height=100,
    label_visibility="collapsed",
)

st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
generate = st.button("🚀  Generate My Travel Plan", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Agent pipeline ────────────────────────────────────────────────────────
if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first — where to, and what matters most to you.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {"flight_results": "", "hotel_results": "", "itinerary": "",
                     "final_response": "", "llm_calls": 0}
        done_keys = set()

        st.markdown("---")
        st.markdown('<div class="sec-head"><div class="bar"></div><span>Agent pipeline — live</span></div>',
                    unsafe_allow_html=True)

        tracker_slot = st.empty()
        tracker_slot.markdown(render_tracker(done_keys), unsafe_allow_html=True)

        boarding_slot = st.empty()
        boarding_slot.markdown(render_loader("flight_agent"), unsafe_allow_html=True)

        is_chitchat = False
        step = 0

        try:
            for chunk in app.stream(
                {
                    "messages": [HumanMessage(content=user_query)],
                    "user_query": user_query,
                    "flight_results": "",
                    "hotel_results": "",
                    "itinerary": "",
                    "llm_calls": 0,
                },
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    if "llm_calls" in state_update:
                        collected["llm_calls"] += state_update["llm_calls"]

                    if node_name == "router_agent":
                        continue

                    if node_name == "chitchat_agent":
                        is_chitchat = True
                        boarding_slot.empty()
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        st.markdown(
                            render_agent_card("💬", "Concierge", "chat", "blue", text, delay_ms=0),
                            unsafe_allow_html=True,
                        )
                        continue

                    boarding_slot.empty()
                    step += 1

                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text
                        done_keys.add("flight_agent")
                        st.markdown(render_agent_card("✈", "Flight Agent", "flights", "blue", text, step * 80), unsafe_allow_html=True)
                        boarding_slot.markdown(render_loader("hotel_agent"), unsafe_allow_html=True)

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text
                        done_keys.add("hotel_agent")
                        st.markdown(render_agent_card("🏨", "Hotel Agent", "stays", "amber", text, step * 80), unsafe_allow_html=True)
                        boarding_slot.markdown(render_loader("itinerary_agent"), unsafe_allow_html=True)

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        done_keys.add("itinerary_agent")
                        st.markdown(render_agent_card("🗺", "Itinerary Agent", "route", "violet", text, step * 80), unsafe_allow_html=True)
                        boarding_slot.markdown(render_loader("final_agent"), unsafe_allow_html=True)

                    elif node_name == "final_agent":
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        collected["final_response"] = text
                        done_keys.add("final_agent")

                    tracker_slot.markdown(render_tracker(done_keys), unsafe_allow_html=True)

            boarding_slot.empty()

            if is_chitchat:
                st.info("Ask me about flights, stays, or a full itinerary whenever you're ready to plan.")
            else:
                # Metrics
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents run</div></div>
                    <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM calls</div></div>
                    <div class="metric-box"><div class="metric-val">✓</div><div class="metric-lbl">Status</div></div>
                </div>
                """, unsafe_allow_html=True)

                # Boarding pass — final plan
                if collected["final_response"]:
                    st.markdown('<div class="sec-head"><div class="bar"></div><span>Your boarding pass</span></div>',
                                unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="ticket">
                      <div class="ticket-head">
                        <div class="brand">✦ WAYFARER <span>· ITINERARY</span></div>
                        <div class="status">READY FOR DEPARTURE</div>
                      </div>
                      <div class="ticket-meta">
                        <div class="t-meta-col"><strong>PASSENGER:</strong> {thread_id}</div>
                        <div class="t-meta-col"><strong>GATE:</strong> AGENT-04</div>
                        <div class="t-meta-col"><strong>DATE:</strong> {datetime.now().strftime("%d %b %Y")}</div>
                      </div>
                      <div class="ticket-perf"></div>
                      <div class="ticket-body">{md_to_html(collected['final_response'])}</div>
                      {render_barcode()}
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()

                    # Save markdown + PDF to disk (Success Scenario)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    md_filename = f"travel_plan_{timestamp}.md"
                    save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
                    os.makedirs(save_dir, exist_ok=True)

                    file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'N/A'}

---

## 🏨 Hotel Information
{collected['hotel_results'] or 'N/A'}

---

## 🗓️ Itinerary
{collected['itinerary'] or 'N/A'}

---

## 🧠 Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
                    with open(os.path.join(save_dir, md_filename), "w", encoding="utf-8") as f:
                        f.write(file_content)

                    pdf_filename = f"travel_plan_{timestamp}.pdf"
                    pdf_bytes = generate_travel_plan_pdf(user_query, thread_id, collected)
                    with open(os.path.join(save_dir, pdf_filename), "wb") as f:
                        f.write(pdf_bytes)

                    dl_col1, dl_col2, info_col = st.columns([1, 1, 2])
                    with dl_col1:
                        st.download_button("⬇ Download Markdown", data=file_content, file_name=md_filename,
                                            mime="text/markdown", use_container_width=True)
                    with dl_col2:
                        st.download_button("📄 Download PDF", data=pdf_bytes, file_name=pdf_filename,
                                            mime="application/pdf", use_container_width=True)
                    with info_col:
                        st.markdown(f"<div class='save-bar'>📁 Auto-saved → <code>travel_plans/{pdf_filename}</code></div>",
                                    unsafe_allow_html=True)

        except Exception as e:
            boarding_slot.empty()
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                st.error("API authentication failed. Please check your API keys in the .env file.")
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                st.error("Network connection error. Please check your internet connection and try again.")
            else:
                st.error(f"An unexpected error occurred: {error_msg}")
            st.info("💡 Troubleshooting tips:\n1. Verify your API keys are set correctly in .env\n2. Check your internet connection\n3. Try a simpler query to test the system\n4. Contact support if the issue persists")
