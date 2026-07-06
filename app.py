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


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root{
  --bg:#030711;
  --bg-soft:#060c17;
  --surface:#0a1220;
  --surface-2:#0e1829;
  --surface-glass:rgba(10,18,32,0.65);
  --border:#162035;
  --border-soft:#12192d;
  --border-glow:rgba(79,143,247,0.12);
  --text:#eef4fb;
  --text-dim:#8da4c0;
  --text-faint:#4c6580;

  --blue:#4f8ff7;    --blue-dim:#122346;
  --amber:#ffb454;   --amber-dim:#3a2510;
  --violet:#b18cff;  --violet-dim:#251e42;
  --teal:#34d1b8;    --teal-dim:#0d2925;
  --rose:#f472b6;    --rose-dim:#3d1a2e;

  --font-display:'Space Grotesk', sans-serif;
  --font-body:'Inter', sans-serif;
  --font-mono:'JetBrains Mono', monospace;

  --radius-sm:10px;
  --radius-md:16px;
  --radius-lg:22px;
  --radius-xl:28px;

  --shadow-sm:0 2px 8px rgba(0,0,0,0.2);
  --shadow-md:0 8px 32px rgba(0,0,0,0.3);
  --shadow-lg:0 20px 60px rgba(0,0,0,0.4);
  --shadow-glow-blue:0 0 40px rgba(79,143,247,0.15);
  --shadow-glow-teal:0 0 40px rgba(52,209,184,0.12);
}

@media (prefers-reduced-motion: reduce){
  *{ animation-duration:0.01ms !important; animation-iteration-count:1 !important; transition-duration:0.01ms !important; }
}

/* ══════════════ BASE ══════════════ */
html, body, .stApp{
  font-family: var(--font-body);
  background:var(--bg) !important;
  color:var(--text);
}

/* ── multi-layer ambient background ── */
.stApp::before{
  content:"";
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(ellipse 800px 500px at 8% -12%, rgba(79,143,247,0.14), transparent 55%),
    radial-gradient(ellipse 700px 450px at 95% 3%, rgba(177,140,255,0.10), transparent 55%),
    radial-gradient(ellipse 650px 550px at 48% 108%, rgba(52,209,184,0.08), transparent 55%),
    radial-gradient(ellipse 400px 300px at 70% 50%, rgba(244,114,182,0.04), transparent 55%);
  animation:auroraDrift 20s ease-in-out infinite alternate;
}
@keyframes auroraDrift{
  0%{ opacity:0.8; transform:translateY(0) scale(1); }
  50%{ opacity:1; transform:translateY(8px) scale(1.01); }
  100%{ opacity:0.9; transform:translateY(-4px) scale(0.99); }
}

/* starfield dot grid */
.stApp::after{
  content:"";
  position:fixed; inset:0; z-index:0; pointer-events:none; opacity:0.025;
  background-image:radial-gradient(rgba(255,255,255,0.85) 0.5px, transparent 0.5px);
  background-size:24px 24px;
  animation: starShimmer 8s ease-in-out infinite alternate;
}
@keyframes starShimmer {
  0% { opacity: 0.02; }
  50% { opacity: 0.035; }
  100% { opacity: 0.02; }
}

.main .block-container{ position:relative; z-index:1; max-width:1160px; padding-top:1.2rem; }

/* ── glass scrollbar ── */
::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-track{ background:transparent; }
::-webkit-scrollbar-thumb{ background:rgba(79,143,247,0.2); border-radius:8px; border:2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover{ background:rgba(79,143,247,0.45); }

/* ══════════════ LOCK SCREEN ══════════════ */
/* ══════════════ LOCK GATE — FULL SCREEN IMMERSIVE ══════════════ */
.lock-fullscreen{
  position:relative;
  text-align:center;
  padding:2.5rem 1rem 1rem;
  min-height:50vh;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
}

/* ── floating travel particles ── */
.lock-particles{
  position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden;
}
.particle{
  position:absolute; font-size:1.2rem; opacity:0;
  animation: particleFloat linear infinite;
}
.p1{ left:8%;  top:15%; font-size:1.6rem; animation-duration:18s; animation-delay:0s; }
.p2{ left:85%; top:20%; font-size:1.4rem; animation-duration:22s; animation-delay:2s; }
.p3{ left:15%; top:70%; font-size:1.1rem; animation-duration:20s; animation-delay:4s; }
.p4{ left:70%; top:80%; font-size:0.9rem; animation-duration:16s; animation-delay:1s; }
.p5{ left:45%; top:10%; font-size:1.3rem; animation-duration:24s; animation-delay:3s; }
.p6{ left:92%; top:55%; font-size:1.5rem; animation-duration:19s; animation-delay:5s; }
.p7{ left:5%;  top:45%; font-size:1.0rem; animation-duration:21s; animation-delay:2.5s; }
.p8{ left:60%; top:5%;  font-size:1.4rem; animation-duration:17s; animation-delay:1.5s; }
.p9{ left:30%; top:85%; font-size:1.1rem; animation-duration:23s; animation-delay:4.5s; }
.p10{left:78%; top:40%; font-size:0.8rem; animation-duration:15s; animation-delay:0.5s; }
.p11{left:25%; top:30%; font-size:1.2rem; animation-duration:20s; animation-delay:6s; }
.p12{left:55%; top:65%; font-size:1.3rem; animation-duration:18s; animation-delay:3.5s; }

@keyframes particleFloat {
  0%   { opacity:0; transform:translateY(0) translateX(0) rotate(0deg) scale(0.7); }
  10%  { opacity:0.25; }
  50%  { opacity:0.15; transform:translateY(-120px) translateX(30px) rotate(180deg) scale(1); }
  90%  { opacity:0.2; }
  100% { opacity:0; transform:translateY(-250px) translateX(-20px) rotate(360deg) scale(0.8); }
}

/* ── card wrapper ── */
.lock-card-wrapper{
  position:relative; z-index:2;
  display:flex; flex-direction:column; align-items:center;
}

/* ── orbital rings ── */
.lock-orbit{
  position:absolute; border-radius:50%;
  border:1px solid transparent; pointer-events:none;
}
.lock-orbit-1{
  width:280px; height:280px; top:50%; left:50%; transform:translate(-50%,-50%);
  border-color:rgba(79,143,247,0.08);
  border-top-color:rgba(79,143,247,0.3);
  animation:orbitSpin1 8s linear infinite;
}
.lock-orbit-2{
  width:360px; height:360px; top:50%; left:50%; transform:translate(-50%,-50%);
  border-color:rgba(177,140,255,0.06);
  border-right-color:rgba(177,140,255,0.2);
  animation:orbitSpin2 12s linear infinite;
}
.lock-orbit-3{
  width:440px; height:440px; top:50%; left:50%; transform:translate(-50%,-50%);
  border-color:rgba(52,209,184,0.04);
  border-bottom-color:rgba(52,209,184,0.15);
  animation:orbitSpin3 16s linear infinite;
}
@keyframes orbitSpin1 { to { transform:translate(-50%,-50%) rotate(360deg); } }
@keyframes orbitSpin2 { to { transform:translate(-50%,-50%) rotate(-360deg); } }
@keyframes orbitSpin3 { to { transform:translate(-50%,-50%) rotate(360deg); } }

/* ── logo ── */
.lock-logo{
  position:relative; width:90px; height:90px; margin-bottom:1.8rem;
}
.lock-logo-inner{
  width:90px; height:90px; border-radius:22px;
  background:linear-gradient(135deg, var(--blue), #6366f1, var(--violet));
  display:flex; align-items:center; justify-content:center;
  font-size:2.4rem; color:#fff;
  box-shadow:
    0 0 50px rgba(79,143,247,0.35),
    0 0 100px rgba(177,140,255,0.15),
    0 20px 60px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(255,255,255,0.2);
  position:relative; z-index:2;
  animation: logoBreath 4s ease-in-out infinite;
}
@keyframes logoBreath {
  0%, 100% { transform:scale(1); box-shadow: 0 0 50px rgba(79,143,247,0.35), 0 0 100px rgba(177,140,255,0.15), 0 20px 60px rgba(0,0,0,0.4); }
  50% { transform:scale(1.05); box-shadow: 0 0 70px rgba(79,143,247,0.45), 0 0 120px rgba(177,140,255,0.25), 0 24px 70px rgba(0,0,0,0.4); }
}
.lock-logo-ring-1{
  position:absolute; inset:-8px; border-radius:26px;
  border:2px solid transparent;
  border-top-color:rgba(79,143,247,0.5); border-right-color:rgba(177,140,255,0.3);
  animation:lockSpin 4s linear infinite;
}
.lock-logo-ring-2{
  position:absolute; inset:-16px; border-radius:30px;
  border:1px solid transparent;
  border-bottom-color:rgba(52,209,184,0.3); border-left-color:rgba(79,143,247,0.15);
  animation:lockSpin 7s linear infinite reverse;
}
@keyframes lockSpin { to { transform:rotate(360deg); } }
.lock-logo-pulse{
  position:absolute; inset:-4px; border-radius:24px;
  background:linear-gradient(135deg, rgba(79,143,247,0.15), rgba(177,140,255,0.1));
  z-index:1;
  animation: logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse {
  0%, 100% { opacity:0.4; transform:scale(1); }
  50% { opacity:0.8; transform:scale(1.12); }
}

/* ── brand text ── */
.lock-brand{
  font-family:var(--font-display);
  font-size:2.8rem; font-weight:700;
  color:var(--text); margin:0 0 0.3rem;
  letter-spacing:-0.03em;
  animation: fadeInUp 0.8s ease both;
}
.lock-brand-accent{
  background:linear-gradient(135deg, var(--blue), #818cf8, var(--violet));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-size:200% 200%;
  animation: gradientShift 5s ease infinite;
}
.lock-tagline{
  font-family:var(--font-mono); font-size:0.72rem;
  color:var(--text-faint); letter-spacing:0.18em;
  text-transform:uppercase; margin:0 0 1.4rem;
  animation: fadeInUp 0.8s ease 0.15s both;
}

/* ── divider ── */
.lock-divider{
  display:flex; align-items:center; gap:0.8rem;
  margin-bottom:1.2rem; width:200px;
  animation: fadeInUp 0.8s ease 0.25s both;
}
.lock-divider-line{
  flex:1; height:1px;
  background:linear-gradient(90deg, transparent, var(--border), transparent);
}
.lock-divider-dot{
  width:5px; height:5px; border-radius:50%;
  background:var(--blue);
  box-shadow:0 0 8px var(--blue);
  animation:blink 2.5s ease-in-out infinite;
}

.lock-subtitle{
  color:var(--text-dim); font-size:0.88rem; line-height:1.7;
  max-width:380px; margin:0 0 1.6rem;
  animation: fadeInUp 0.8s ease 0.35s both;
}

/* ── route visualization ── */
.lock-route{
  display:flex; align-items:center; gap:0; margin-bottom:0.8rem;
  animation: fadeInUp 0.8s ease 0.45s both;
}
.lock-route-node{
  width:36px; height:36px; border-radius:10px;
  background:rgba(255,255,255,0.03); border:1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  font-size:0.9rem; transition:all 0.3s ease;
}
.lock-route-node:hover{
  border-color:var(--blue); background:rgba(79,143,247,0.06);
  box-shadow:0 0 16px rgba(79,143,247,0.15);
  transform:translateY(-2px);
}
.lock-route-line{
  width:50px; height:2px; background:var(--border);
  position:relative; overflow:hidden;
}
.lock-route-beam{
  position:absolute; inset:0;
  background:linear-gradient(90deg, transparent, var(--blue), transparent);
  animation:routeBeam 2.5s ease-in-out infinite;
}
@keyframes routeBeam {
  0%   { transform:translateX(-100%); }
  100% { transform:translateX(100%); }
}

@keyframes fadeInUp {
  from { opacity:0; transform:translateY(16px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ── input card glass ── */
.lock-input-card{
  background:rgba(10,18,32,0.6);
  backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
  border:1px solid var(--border);
  border-radius:var(--radius-lg);
  padding:1.6rem 1.8rem 1.2rem;
  box-shadow:
    0 20px 60px rgba(0,0,0,0.4),
    0 0 0 1px rgba(79,143,247,0.06),
    inset 0 1px 0 rgba(255,255,255,0.04);
  animation: fadeInUp 0.8s ease 0.5s both;
  position:relative; overflow:hidden;
}
.lock-input-card::before{
  content:""; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg, var(--blue), var(--violet), var(--teal));
  background-size:200% 200%;
  animation:gradientShift 4s ease infinite;
}
.lock-input-card label{
  font-family:var(--font-mono) !important; font-size:0.7rem !important;
  letter-spacing:0.14em !important; color:var(--blue) !important;
  font-weight:600 !important;
}
.lock-input-card input[type="password"]{
  background:var(--bg) !important; border:1px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; color:var(--text) !important;
  font-family:var(--font-body) !important; padding:0.7rem 1rem !important;
  font-size:0.95rem !important;
  transition:all 0.3s ease !important;
}
.lock-input-card input[type="password"]:focus{
  border-color:var(--blue) !important;
  box-shadow:0 0 0 3px rgba(79,143,247,0.12), 0 0 24px rgba(79,143,247,0.08) !important;
}
.lock-input-card input[type="password"]::placeholder{
  color:var(--text-faint) !important; font-size:0.88rem !important;
}

/* ── unlock button ── */
.lock-btn-wrap div[data-testid="stButton"] > button{
  background:linear-gradient(135deg, var(--blue) 0%, #6366f1 50%, var(--violet) 100%) !important;
  background-size:200% 200% !important;
  animation:gradientShift 4s ease infinite !important;
  color:#fff !important; border:none !important;
  border-radius:var(--radius-md) !important;
  padding:0.9rem 2rem !important; font-size:1rem !important;
  font-weight:700 !important; font-family:var(--font-display) !important;
  letter-spacing:0.02em !important;
  box-shadow:
    0 0 0 1px rgba(79,143,247,0.2),
    0 8px 30px rgba(79,143,247,0.3),
    0 16px 50px rgba(99,102,241,0.15),
    inset 0 1px 0 rgba(255,255,255,0.15) !important;
  transition:all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
  position:relative !important;
}
.lock-btn-wrap div[data-testid="stButton"] > button:hover{
  transform:translateY(-3px) !important;
  box-shadow:
    0 0 0 1px rgba(79,143,247,0.35),
    0 12px 40px rgba(79,143,247,0.4),
    0 20px 60px rgba(99,102,241,0.2),
    inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
.lock-btn-wrap div[data-testid="stButton"] > button:active{
  transform:translateY(0) !important;
}

/* ── footer badge ── */
.lock-footer{
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  font-family:var(--font-mono); font-size:0.66rem;
  color:var(--text-faint); letter-spacing:0.1em;
  margin-top:1rem; padding-top:0.8rem;
  border-top:1px solid var(--border);
}
.lock-footer-dot{
  width:5px; height:5px; border-radius:50%;
  background:var(--teal);
  box-shadow:0 0 6px var(--teal);
  animation:blink 2s ease-in-out infinite;
}

/* ══════════════ HERO — departure board ══════════════ */
.hero{
  position:relative;
  border:1px solid var(--border);
  border-radius:var(--radius-xl);
  padding:2.8rem 2.8rem 2.2rem;
  margin-bottom:1.4rem;
  background:
    linear-gradient(155deg, rgba(79,143,247,0.07), rgba(177,140,255,0.04) 55%, rgba(52,209,184,0.03)),
    var(--surface-glass);
  backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  overflow:hidden;
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.04);
}
.hero::before{
  content:"";
  position:absolute; top:-50%; right:-15%; width:420px; height:420px;
  background:radial-gradient(circle, rgba(79,143,247,0.18), transparent 65%);
  filter:blur(8px);
  animation:pulseGlow 7s ease-in-out infinite;
}
.hero::after{
  content:"";
  position:absolute; bottom:-30%; left:-10%; width:350px; height:350px;
  background:radial-gradient(circle, rgba(177,140,255,0.10), transparent 65%);
  filter:blur(12px);
  animation:pulseGlow 9s ease-in-out infinite reverse;
}
@keyframes pulseGlow{
  0%,100%{ opacity:0.5; transform:scale(1); }
  50%{ opacity:1; transform:scale(1.1); }
}

/* hero top badge */
.hero-eyebrow{
  font-family:var(--font-mono);
  font-size:0.7rem; font-weight:600; letter-spacing:0.2em; text-transform:uppercase;
  color:var(--blue); display:inline-flex; align-items:center; gap:0.5rem;
  background:rgba(79,143,247,0.08); border:1px solid rgba(79,143,247,0.15);
  padding:0.35rem 0.9rem; border-radius:20px; margin-bottom:1.1rem;
}
.hero-eyebrow .dot{
  width:6px; height:6px; border-radius:50%;
  background:var(--teal);
  box-shadow:0 0 10px var(--teal), 0 0 20px rgba(52,209,184,0.3);
  animation:blink 2s ease-in-out infinite;
}
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:0.2;} }

.hero-title{
  font-family:var(--font-display);
  font-size:2.8rem; font-weight:700; letter-spacing:-0.03em;
  color:var(--text); margin:0 0 0.6rem; line-height:1.1;
  position:relative; z-index:1;
}
.hero-title .accent{
  background:linear-gradient(135deg, var(--blue) 0%, var(--violet) 50%, var(--teal) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-size:200% 200%;
  animation: gradientShift 6s ease infinite;
}
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-sub{
  color:var(--text-dim); font-size:1.02rem; max-width:600px; line-height:1.7;
  position:relative; z-index:1;
}
.hero-route{
  display:flex; align-items:center; gap:0.6rem; margin-top:1.6rem;
  font-family:var(--font-mono); font-size:0.78rem; color:var(--text-faint);
  position:relative; z-index:1;
}
.hero-route .seg{
  flex:1; height:1px; position:relative;
  background:repeating-linear-gradient(90deg, var(--border) 0 6px, transparent 6px 12px);
}
.hero-route .seg::after{
  content:""; position:absolute; top:-1px; left:0; height:3px; width:0;
  background:linear-gradient(90deg, var(--blue), var(--teal));
  border-radius:2px;
  animation: routeFly 4s ease-in-out infinite;
}
@keyframes routeFly {
  0% { width:0; left:0; opacity:0; }
  30% { width:40%; opacity:1; }
  70% { width:40%; opacity:1; }
  100% { width:0; left:100%; opacity:0; }
}
.hero-route .plane{ font-size:0.95rem; animation: planeFloat 3s ease-in-out infinite; }
@keyframes planeFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* feature pills below hero */
.feature-pills{
  display:flex; gap:0.6rem; margin-top:1.4rem; flex-wrap:wrap;
  position:relative; z-index:1;
}
.feature-pill{
  font-family:var(--font-mono); font-size:0.7rem; font-weight:500;
  color:var(--text-dim); background:rgba(255,255,255,0.03);
  border:1px solid var(--border); padding:0.3rem 0.75rem;
  border-radius:20px; letter-spacing:0.04em;
  transition: all 0.3s ease;
}
.feature-pill:hover{
  border-color:var(--blue); color:var(--text);
  background:rgba(79,143,247,0.06);
  box-shadow:0 0 16px rgba(79,143,247,0.1);
}

/* ══════════════ destination strip ══════════════ */
.dest-strip{ display:flex; gap:0.6rem; margin:0 0 1.6rem; }
.dest-card{
  flex:1; position:relative; border-radius:var(--radius-md); overflow:hidden; height:100px;
  border:1px solid var(--border-soft);
  transition:all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  cursor:pointer;
}
.dest-card:hover{
  transform:translateY(-5px) scale(1.02);
  border-color:var(--blue);
  box-shadow: 0 12px 40px rgba(79,143,247,0.2), 0 0 0 1px rgba(79,143,247,0.1);
}
.dest-card img{
  width:100%; height:100%; object-fit:cover;
  filter:brightness(0.4) saturate(1.1);
  transition: filter 0.4s ease, transform 0.6s ease;
}
.dest-card:hover img{
  filter:brightness(0.55) saturate(1.2);
  transform: scale(1.08);
}
.dest-card .tag{
  position:absolute; bottom:0; left:0; right:0; color:#fff;
  font-size:0.8rem; font-weight:600; font-family:var(--font-body);
  padding:0.6rem 0.8rem; text-shadow:0 1px 6px rgba(0,0,0,0.6);
  background:linear-gradient(transparent, rgba(0,0,0,0.6));
}
.dest-card .tag .dest-temp{
  font-family:var(--font-mono); font-size:0.65rem; font-weight:400;
  color:rgba(255,255,255,0.7); margin-left:0.3rem;
}

/* ══════════════ input card ══════════════ */
.input-section{
  background: var(--surface-glass);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
  border:1px solid var(--border);
  border-radius:var(--radius-lg);
  padding:1.8rem 2rem 1.6rem;
  margin-bottom:1.5rem;
  box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,0.03);
}
.input-label{
  font-family:var(--font-mono); color:var(--blue); font-size:0.72rem; font-weight:600;
  letter-spacing:0.16em; text-transform:uppercase; margin-bottom:0.65rem;
  display:flex; align-items:center; gap:0.5rem;
}
.input-label .input-icon{
  width:20px; height:20px; border-radius:5px;
  background:rgba(79,143,247,0.1); border:1px solid rgba(79,143,247,0.2);
  display:inline-flex; align-items:center; justify-content:center; font-size:0.65rem;
}
.stTextArea textarea{
  background:var(--bg-soft) !important; border:1px solid var(--border) !important;
  border-radius:var(--radius-md) !important; color:var(--text) !important; font-size:0.97rem !important;
  font-family:var(--font-body) !important; resize:none !important; padding:1.1rem 1.2rem !important;
  transition: all 0.3s ease !important;
}
.stTextArea textarea:focus{
  border-color:var(--blue) !important;
  box-shadow:0 0 0 3px rgba(79,143,247,0.12), 0 0 20px rgba(79,143,247,0.06) !important;
  background:var(--surface) !important;
}
.stTextArea textarea::placeholder{ color:var(--text-faint) !important; }

/* quick chips (gate buttons) */
div[data-testid="column"] .stButton > button{
  background:var(--bg-soft) !important; color:var(--text-dim) !important;
  border:1px solid var(--border) !important; border-radius:20px !important;
  padding:0.4rem 1rem !important; font-size:0.8rem !important; font-weight:500 !important;
  box-shadow:none !important; transition:all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  font-family:var(--font-body) !important;
}
div[data-testid="column"] .stButton > button:hover{
  border-color:var(--blue) !important; color:var(--text) !important;
  background:rgba(79,143,247,0.08) !important;
  transform:translateY(-2px) !important;
  box-shadow:0 4px 16px rgba(79,143,247,0.12) !important;
}

/* primary generate button */
.generate-btn div[data-testid="stButton"] > button{ }
.generate-btn div[data-testid="stButton"] > button{
  background:linear-gradient(135deg, var(--blue) 0%, #2f66c9 40%, var(--violet) 100%) !important;
  color:#fff !important; border:none !important; border-radius:var(--radius-md) !important;
  padding:1rem 2.5rem !important; font-size:1.06rem !important; font-weight:700 !important;
  letter-spacing:0.02em !important; width:100% !important; font-family:var(--font-display) !important;
  box-shadow:
    0 0 0 1px rgba(79,143,247,0.2),
    0 4px 16px rgba(79,143,247,0.25),
    0 12px 40px rgba(79,143,247,0.15),
    inset 0 1px 0 rgba(255,255,255,0.15) !important;
  transition:all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
  position:relative; overflow:hidden;
}
.generate-btn div[data-testid="stButton"] > button:hover{
  box-shadow:
    0 0 0 1px rgba(79,143,247,0.35),
    0 6px 24px rgba(79,143,247,0.35),
    0 16px 56px rgba(79,143,247,0.2),
    inset 0 1px 0 rgba(255,255,255,0.2) !important;
  transform:translateY(-2px) !important;
}
.generate-btn div[data-testid="stButton"] > button:active{
  transform:translateY(0) !important;
  box-shadow:
    0 0 0 1px rgba(79,143,247,0.3),
    0 2px 8px rgba(79,143,247,0.2) !important;
}

/* ══════════════ route tracker (signature element) ══════════════ */
.tracker{
  margin:0.4rem 0 1.8rem;
  padding:1.5rem 1.8rem;
  background: var(--surface-glass);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
  border:1px solid var(--border);
  border-radius:var(--radius-lg);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,0.03);
}
.tracker-label{
  font-family:var(--font-mono); font-size:0.7rem; letter-spacing:0.18em;
  text-transform:uppercase; color:var(--text-faint); margin-bottom:1.2rem;
  display:flex; align-items:center; gap:0.5rem;
}
.tracker-label::before{
  content:""; width:6px; height:6px; border-radius:50%;
  background:var(--teal);
  box-shadow:0 0 8px var(--teal);
  animation:blink 2s ease-in-out infinite;
}
.tracker-row{ display:flex; align-items:center; }
.tracker-node{ display:flex; flex-direction:column; align-items:center; gap:0.5rem; width:64px; flex-shrink:0; }
.tracker-node .ring{
  width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:1.1rem; background:var(--bg); border:2px solid var(--border);
  color:var(--text-faint); transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position:relative;
}
.tracker-node.done .ring{
  border-color:var(--_c); color:#fff;
  background:linear-gradient(135deg, var(--_c), color-mix(in srgb, var(--_c) 70%, #000));
  box-shadow:0 0 20px var(--_c), 0 0 40px color-mix(in srgb, var(--_c) 40%, transparent);
  animation:nodePop 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.tracker-node.done .ring::after{
  content:""; position:absolute; inset:-4px; border-radius:50%;
  border:1px solid var(--_c); opacity:0.3;
}
.tracker-node.active .ring{
  border-color:var(--_c); color:var(--_c); background:var(--bg);
  box-shadow:0 0 16px var(--_c), 0 0 32px color-mix(in srgb, var(--_c) 30%, transparent);
  animation:pulseActive 1.8s infinite alternate;
}
@keyframes pulseActive {
  0% { transform: scale(1); box-shadow: 0 0 10px var(--_c); }
  100% { transform: scale(1.1); box-shadow: 0 0 25px var(--_c), 0 0 50px color-mix(in srgb, var(--_c) 25%, transparent); }
}
@keyframes nodePop{ 0%{ transform:scale(0.5); opacity:0; } 60%{ transform:scale(1.15); } 100%{ transform:scale(1); opacity:1; } }
.tracker-node .name{ font-size:0.67rem; color:var(--text-faint); text-align:center; font-weight:500; }
.tracker-node.done .name{ color:var(--text-dim); font-weight:600; }
.tracker-node.active .name{ color:var(--text); font-weight:600; }
.tracker-line{ flex:1; height:2px; background:var(--border); margin:0 -6px 26px; position:relative; overflow:hidden; border-radius:1px; }
.tracker-line.done::after{
  content:""; position:absolute; inset:0;
  background:linear-gradient(90deg, var(--_c), color-mix(in srgb, var(--_c) 80%, #fff));
  transform-origin:left;
  animation:fillLine 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  box-shadow:0 0 8px var(--_c);
}
.tracker-line.active::after{
  content:""; position:absolute; inset:0;
  background:linear-gradient(90deg, var(--_c), transparent);
  animation:pulseLine 1.8s infinite linear; transform-origin:left;
}
@keyframes fillLine{ from{ transform:scaleX(0); } to{ transform:scaleX(1); } }
@keyframes pulseLine {
  0% { transform: scaleX(0); opacity: 0.3; }
  50% { transform: scaleX(1); opacity: 0.8; }
  100% { transform: scaleX(1); opacity: 0; }
}

/* ══════════════ custom loader ══════════════ */
.loader-container {
  background: var(--surface-glass);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2.4rem 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  animation: cardIn 0.5s ease both;
}
.loader-container::before {
  content: ""; position: absolute; top: 0; left: -100%; width: 100%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--blue), var(--violet), transparent);
  animation: scanning 2.5s infinite linear;
}
.loader-container::after {
  content: ""; position: absolute; bottom: 0; right: -100%; width: 100%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--teal), transparent);
  animation: scanning 3s infinite linear reverse;
}
@keyframes scanning {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Orbital spinner */
.loader-spinner-wrap{
  width:52px; height:52px; margin:0 auto 1.4rem; position:relative;
}
.loader-spinner {
  width: 52px; height: 52px;
  border: 2px solid rgba(79,143,247,0.1);
  border-top-color: var(--blue);
  border-right-color: rgba(177,140,255,0.4);
  border-radius: 50%;
  animation: spin 1s infinite linear;
  position:absolute; inset:0;
}
.loader-spinner-inner{
  position:absolute; inset:8px;
  border:2px solid transparent;
  border-bottom-color:var(--teal);
  border-left-color:rgba(52,209,184,0.3);
  border-radius:50%;
  animation:spin 1.6s infinite linear reverse;
}
.loader-spinner-dot{
  position:absolute; top:50%; left:50%; transform:translate(-50%, -50%);
  width:6px; height:6px; border-radius:50%;
  background:var(--blue);
  box-shadow:0 0 10px var(--blue);
  animation: dotPulse 1.2s infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes dotPulse { 0%,100%{ opacity:1; transform:translate(-50%,-50%) scale(1); } 50%{ opacity:0.5; transform:translate(-50%,-50%) scale(0.6); } }

.loader-text {
  font-family: var(--font-display);
  font-size: 1.15rem; font-weight: 600; color: var(--text);
  margin-bottom: 0.4rem;
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
}
.loader-sub {
  font-size: 0.84rem; color: var(--text-dim); line-height:1.5;
}

/* ══════════════ section headers ══════════════ */
.sec-head{
  display:flex; align-items:center; gap:0.7rem; margin:2.2rem 0 1rem;
}
.sec-head .bar{
  width:3px; height:20px;
  background:linear-gradient(180deg, var(--blue), var(--violet));
  border-radius:2px;
  box-shadow:0 0 8px rgba(79,143,247,0.3);
}
.sec-head span{
  font-family:var(--font-display); font-size:1.15rem; font-weight:600; color:var(--text);
  letter-spacing:-0.01em;
}

/* ══════════════ agent result cards ══════════════ */
.agent-card{
  position:relative;
  background: var(--surface-glass);
  backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
  border:1px solid var(--border);
  border-left:3px solid var(--_c);
  border-radius:var(--radius-lg);
  padding:1.4rem 1.6rem 1.5rem;
  margin-bottom:1rem;
  box-shadow: var(--shadow-md);
  animation:cardIn 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
  overflow:hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.agent-card:hover{
  border-color: color-mix(in srgb, var(--_c) 60%, var(--border));
  box-shadow: var(--shadow-md), 0 0 30px color-mix(in srgb, var(--_c) 12%, transparent);
}
.agent-card::before{
  content:""; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg, var(--_c), transparent 60%);
  opacity:0.3;
}
@keyframes cardIn{ from{ opacity:0; transform:translateY(18px); } to{ opacity:1; transform:translateY(0); } }
.agent-card__head{ display:flex; align-items:center; gap:0.65rem; margin-bottom:0.8rem; }
.agent-card__icon{
  font-size:1.1rem; width:36px; height:36px; border-radius:10px;
  background:var(--_cd); border:1px solid var(--_c);
  display:flex; align-items:center; justify-content:center;
  box-shadow: 0 0 12px color-mix(in srgb, var(--_c) 20%, transparent);
}
.agent-card__label{ font-family:var(--font-display); font-weight:600; font-size:1.04rem; color:var(--text); flex:1; }
.agent-card__badge{
  font-family:var(--font-mono); font-size:0.66rem; color:var(--_c); background:var(--_cd);
  padding:0.22rem 0.65rem; border-radius:20px; letter-spacing:0.06em; font-weight:600;
  border:1px solid color-mix(in srgb, var(--_c) 20%, transparent);
}
.agent-card__body{ color:#b8cce0; font-size:0.94rem; line-height:1.75; }
.agent-card__body p{ margin:0 0 0.6rem; }
.agent-card__body ul{ margin:0 0 0.7rem; padding-left:1.25rem; }
.agent-card__body li{ margin-bottom:0.35rem; }
.agent-card__body h2,.agent-card__body h3,.agent-card__body h4{
  font-family:var(--font-display); color:var(--text); margin:0.9rem 0 0.4rem;
}
.agent-card__body strong{ color:var(--text); }

/* boarding lane state (before result arrives) */
.boarding-line{
  display:flex; align-items:center; gap:0.7rem; padding:0.9rem 1.2rem; background:var(--surface);
  border:1px dashed var(--border); border-radius:var(--radius-sm); color:var(--text-faint);
  font-family:var(--font-mono); font-size:0.83rem; margin-bottom:1rem;
}
.boarding-line .plane-fly{ display:inline-block; animation:flyAcross 1.6s ease-in-out infinite; }
@keyframes flyAcross{ 0%,100%{ transform:translateX(0); } 50%{ transform:translateX(6px); } }

/* ══════════════ metrics ══════════════ */
.metric-row{ display:flex; gap:0.8rem; margin:1.8rem 0; }
.metric-box{
  flex:1;
  background: var(--surface-glass);
  backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
  border:1px solid var(--border);
  border-radius:var(--radius-md);
  padding:1.2rem 1.2rem;
  text-align:center;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  position:relative; overflow:hidden;
}
.metric-box:hover{
  border-color:rgba(79,143,247,0.25);
  transform:translateY(-2px);
  box-shadow: var(--shadow-md), var(--shadow-glow-blue);
}
.metric-box::before{
  content:""; position:absolute; top:0; left:0; right:0; height:2px;
  border-radius:2px 2px 0 0;
}
.metric-box:nth-child(1)::before{ background:linear-gradient(90deg, var(--blue), transparent); }
.metric-box:nth-child(2)::before{ background:linear-gradient(90deg, var(--violet), transparent); }
.metric-box:nth-child(3)::before{ background:linear-gradient(90deg, var(--teal), transparent); }
.metric-val{
  font-family:var(--font-display); font-size:2rem; font-weight:700;
  background:linear-gradient(135deg, var(--blue), var(--violet));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.metric-box:nth-child(3) .metric-val{
  background:linear-gradient(135deg, var(--teal), #6ee7c8);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.metric-lbl{
  font-family:var(--font-mono); font-size:0.68rem; color:var(--text-faint); margin-top:0.3rem;
  text-transform:uppercase; letter-spacing:0.12em;
}

/* ══════════════ boarding pass — final ticket ══════════════ */
.ticket{
  position:relative;
  background:linear-gradient(155deg, #0c1e35 0%, #060e1a 100%);
  border:1px solid var(--border);
  border-radius:var(--radius-xl);
  padding:0; overflow:hidden;
  box-shadow:
    0 30px 80px rgba(0,0,0,0.5),
    0 0 0 1px rgba(79,143,247,0.08),
    inset 0 1px 0 rgba(255,255,255,0.04);
}
/* holographic sheen */
.ticket::before{
  content:""; position:absolute; inset:0; z-index:1; pointer-events:none;
  background:linear-gradient(
    125deg,
    transparent 30%,
    rgba(79,143,247,0.04) 40%,
    rgba(177,140,255,0.03) 50%,
    rgba(52,209,184,0.04) 60%,
    transparent 70%
  );
  background-size:300% 300%;
  animation: holoSheen 8s ease infinite;
}
@keyframes holoSheen {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.ticket-head{
  display:flex; justify-content:space-between; align-items:center; padding:1.5rem 2rem;
  background:linear-gradient(120deg, rgba(52,209,184,0.12), rgba(79,143,247,0.08), rgba(177,140,255,0.05));
  position:relative; z-index:2;
}
.ticket-head .brand{
  font-family:var(--font-display); font-weight:700; font-size:1.15rem;
  color:var(--text); letter-spacing:0.02em;
}
.ticket-head .brand span{ color:var(--teal); }
.ticket-head .status{
  font-family:var(--font-mono); font-size:0.7rem; letter-spacing:0.12em;
  color:var(--teal);
  border:1px solid rgba(52,209,184,0.25);
  background:rgba(52,209,184,0.08);
  padding:0.3rem 0.8rem; border-radius:20px;
  font-weight:600;
  box-shadow: 0 0 12px rgba(52,209,184,0.15);
  animation: statusPulse 3s ease infinite;
}
@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 12px rgba(52,209,184,0.15); }
  50% { box-shadow: 0 0 20px rgba(52,209,184,0.3); }
}

.ticket-meta {
  display: flex; justify-content: space-between; padding: 1rem 2rem;
  font-family: var(--font-mono); font-size: 0.74rem; color: var(--text-dim);
  border-bottom: 1px dashed var(--border); background: rgba(255,255,255,0.01);
  position:relative; z-index:2;
}
.ticket-meta strong { color: var(--blue); }
.ticket-perf{
  position:relative; height:1px;
  background:repeating-linear-gradient(90deg, var(--border) 0 8px, transparent 8px 16px);
  margin:0 2rem;
}
.ticket-perf::before,.ticket-perf::after{
  content:""; position:absolute; top:-10px; width:20px; height:20px; border-radius:50%; background:var(--bg);
  border:1px solid var(--border);
}
.ticket-perf::before{ left:-2rem; } .ticket-perf::after{ right:-2rem; }
.ticket-body{
  padding:1.8rem 2.2rem 2rem; color:#c8d9ec; font-size:0.97rem; line-height:1.8;
  position:relative; z-index:2;
}
.ticket-body p{ margin:0 0 0.75rem; }
.ticket-body ul{ padding-left:1.3rem; margin:0 0 0.8rem; }
.ticket-body li{ margin-bottom:0.4rem; }
.ticket-body h2,.ticket-body h3,.ticket-body h4{
  font-family:var(--font-display); color:#fff; margin:1rem 0 0.5rem;
}
.ticket-body strong{ color:#fff; }
.ticket-barcode {
  display: flex; justify-content: center; align-items: center; gap: 2px;
  padding: 1.8rem 0; background: rgba(255,255,255,0.015);
  border-top: 1px dashed var(--border);
  position:relative; z-index:2;
}
.ticket-barcode span {
  display: inline-block; height: 38px; background: var(--text-faint);
  border-radius:1px;
}

/* ══════════════ save bar ══════════════ */
.save-bar{
  background:var(--surface-glass);
  backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
  border:1px solid var(--border);
  border-radius:var(--radius-sm);
  padding:0.85rem 1.2rem; color:var(--text-dim); font-size:0.84rem; font-family:var(--font-mono);
  display:flex; align-items:center; height:100%;
}
.save-bar code{
  color:var(--blue); background:rgba(79,143,247,0.08);
  border:1px solid rgba(79,143,247,0.15);
  padding:0.1rem 0.4rem; border-radius:4px; font-size:0.78rem;
}

/* download buttons */
div[data-testid="stDownloadButton"] > button{
  background:var(--surface) !important; color:var(--text) !important;
  border:1px solid var(--border) !important; border-radius:var(--radius-sm) !important;
  font-weight:600 !important; transition:all 0.25s ease !important;
  font-family:var(--font-body) !important;
}
div[data-testid="stDownloadButton"] > button:hover{
  border-color:var(--blue) !important; color:var(--blue) !important;
  background:rgba(79,143,247,0.05) !important;
  box-shadow:0 4px 16px rgba(79,143,247,0.12) !important;
  transform:translateY(-1px) !important;
}

/* ══════════════ sidebar — boarding-pass stub ══════════════ */
section[data-testid="stSidebar"]{
  background:var(--bg-soft) !important;
  border-right:1px solid var(--border-soft) !important;
}
.side-brand-wrap{
  padding:0.4rem 0 0.6rem;
  border-bottom:1px solid var(--border);
  margin-bottom:1rem;
}
.side-brand{
  font-family:var(--font-display); font-weight:700; font-size:1.25rem;
  color:var(--text); margin:0 0 0.15rem;
  display:flex; align-items:center; gap:0.5rem;
}
.side-brand .logo-mark{
  width:28px; height:28px; border-radius:8px;
  background:linear-gradient(135deg, var(--blue), var(--violet));
  display:flex; align-items:center; justify-content:center;
  font-size:0.85rem; color:#fff;
  box-shadow:0 0 16px rgba(79,143,247,0.25);
}
.side-brand span{ color:var(--blue); }
.side-tag{
  font-family:var(--font-mono); font-size:0.66rem; color:var(--text-faint);
  letter-spacing:0.12em; margin-left:2.2rem;
}
.side-title{
  color:var(--text-faint); font-family:var(--font-mono); font-size:0.68rem; font-weight:600;
  text-transform:uppercase; letter-spacing:0.14em; margin:1.4rem 0 0.6rem;
  display:flex; align-items:center; gap:0.45rem;
}
.side-title::before{
  content:""; width:12px; height:1px; background:var(--border);
}
.stack-chip{
  background:rgba(255,255,255,0.02); border:1px solid var(--border-soft);
  border-radius:var(--radius-sm);
  padding:0.5rem 0.8rem; margin-bottom:0.35rem; font-size:0.8rem; color:var(--text-dim);
  transition: all 0.2s ease;
}
.stack-chip:hover{
  border-color:rgba(79,143,247,0.2);
  background:rgba(79,143,247,0.03);
}

.pipe-item{ display:flex; align-items:center; gap:0.6rem; padding:0.5rem 0; position:relative; }
.pipe-item .num{
  width:22px; height:22px; border-radius:6px;
  background:rgba(79,143,247,0.06);
  border:1px solid var(--border);
  color:var(--text-faint); font-family:var(--font-mono); font-size:0.66rem;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.pipe-item .label{ font-size:0.82rem; color:var(--text-dim); }
.pipe-item:not(:last-child)::after{
  content:""; position:absolute; left:11px; top:28px; width:1px; height:16px;
  background:linear-gradient(180deg, var(--border), transparent);
}

section[data-testid="stSidebar"] input[type="text"]{
  background:var(--bg) !important; border:1px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; color:var(--text) !important;
  font-family:var(--font-body) !important;
}
section[data-testid="stSidebar"] input[type="text"]:focus{
  border-color:var(--blue) !important;
  box-shadow:0 0 0 3px rgba(79,143,247,0.1) !important;
}
section[data-testid="stSidebar"] label{
  color:var(--blue) !important; font-size:0.72rem !important;
  font-weight:600 !important; letter-spacing:0.1em !important;
  font-family:var(--font-mono) !important;
}

/* ══════════════ footer signature ══════════════ */
.footer-sig{
  text-align:center; padding:2rem 0 1rem;
  font-family:var(--font-mono); font-size:0.7rem; color:var(--text-faint);
  letter-spacing:0.06em;
}
.footer-sig .brand-text{
  background:linear-gradient(135deg, var(--blue), var(--violet));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  font-weight:600;
}

/* general */
.stAlert{
  background:var(--surface-glass) !important;
  backdrop-filter:blur(12px) !important;
  border:1px solid var(--border) !important;
  border-radius:var(--radius-sm) !important;
}
.stAlert p{ color:var(--text) !important; }
#MainMenu, footer, header{ visibility:hidden; }

/* ══════════════ RESPONSIVE ══════════════ */
@media (max-width:768px){
  .hero-title{ font-size:1.8rem; }
  .dest-strip{ flex-wrap:wrap; }
  .dest-card{ min-width:45%; height:80px; }
  .metric-row{ flex-wrap:wrap; }
  .metric-box{ min-width:45%; }
  .ticket-body{ padding:1.2rem 1rem; }
  .feature-pills{ display:none; }
}
</style>
""", unsafe_allow_html=True)
def check_password():
    """Returns True if the user entered the correct password."""
    target_pwd = os.getenv("DEMO_PASSWORD", "wayfarer_demo")
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Full-screen immersive lock gate
    st.markdown("""
    <div class="lock-fullscreen">
      <!-- Animated particles -->
      <div class="lock-particles">
        <div class="particle p1">✈</div>
        <div class="particle p2">🌍</div>
        <div class="particle p3">🗺</div>
        <div class="particle p4">⭐</div>
        <div class="particle p5">🧭</div>
        <div class="particle p6">🌏</div>
        <div class="particle p7">✦</div>
        <div class="particle p8">🛫</div>
        <div class="particle p9">🌐</div>
        <div class="particle p10">💫</div>
        <div class="particle p11">🗼</div>
        <div class="particle p12">🏔</div>
      </div>

      <!-- Central content -->
      <div class="lock-card-wrapper">
        <!-- Orbital rings -->
        <div class="lock-orbit lock-orbit-1"></div>
        <div class="lock-orbit lock-orbit-2"></div>
        <div class="lock-orbit lock-orbit-3"></div>

  
      <div class="lock-logo">
          <div class="lock-logo-inner">✦</div>
          <div class="lock-logo-ring-1"></div>
          <div class="lock-logo-ring-2"></div>
          <div class="lock-logo-pulse"></div>
        </div>

      <h1 class="lock-brand">Way<span class="lock-brand-accent">farer</span></h1>
      <p class="lock-tagline">AI-Powered Multi-Agent Travel Concierge</p>

      <div class="lock-divider">
        <span class="lock-divider-line"></span>
        <span class="lock-divider-dot"></span>
        <span class="lock-divider-line"></span>
      </div>

      <p class="lock-subtitle">This live demo is password-protected to prevent API abuse.<br>Enter the password to begin your journey.</p>

      <div class="lock-route">
        <div class="lock-route-node">🔒</div>
          <div class="lock-route-line"><div class="lock-route-beam"></div></div>
          <div class="lock-route-node">✈</div>
          <div class="lock-route-line"><div class="lock-route-beam"></div></div>
          <div class="lock-route-node">🌍</div>
          <div class="lock-route-line"><div class="lock-route-beam"></div></div>
          <div class="lock-route-node">✦</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="lock-input-card">', unsafe_allow_html=True)
        pwd_input = st.text_input("🔑  ACCESS CODE", type="password", placeholder="Enter your password...")
        
        st.markdown('<div class="lock-btn-wrap">', unsafe_allow_html=True)
        if st.button("✦  Unlock & Begin Journey", use_container_width=True):
            if pwd_input == target_pwd:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("😕 Incorrect password. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="lock-footer">
          <span class="lock-footer-dot"></span>
          Secured by Wayfarer · Multi-Agent System
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

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
COLOR_DIM = {"blue": "#122346", "amber": "#3a2510", "violet": "#251e42", "teal": "#0d2925"}


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
    <div class="loader-container" style="border-top: 2px solid {c};">
      <div class="loader-spinner-wrap">
        <div class="loader-spinner" style="border-top-color: {c};"></div>
        <div class="loader-spinner-inner" style="border-bottom-color: {c};"></div>
        <div class="loader-spinner-dot" style="background: {c}; box-shadow: 0 0 10px {c};"></div>
      </div>
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
        '<div class="side-brand-wrap">'
        '<div class="side-brand"><span class="logo-mark">✦</span> Way<span>farer</span></div>'
        '<div class="side-tag">MULTI-AGENT TRAVEL CONCIERGE</div>'
        '</div>',
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
  <div class="hero-sub">Four specialized AI agents work in concert — searching flights, scouting stays,
  drafting your itinerary, and stitching it all into one boarding pass.</div>
  <div class="hero-route">
    <span>YOU</span><span class="seg"></span><span class="plane">✈</span><span class="seg"></span><span>ANYWHERE</span>
  </div>
  <div class="feature-pills">
    <span class="feature-pill">⚡ Real-time search</span>
    <span class="feature-pill">🤖 4 AI agents</span>
    <span class="feature-pill">🧠 Memory-enabled</span>
    <span class="feature-pill">📋 PDF export</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Destination strip ────────────────────────────────────────────────────
DESTINATIONS = [
    ("Tokyo",   "28°C", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("Paris",   "22°C", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("Bangkok", "33°C", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("Rome",    "26°C", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("Dubai",   "38°C", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]
st.markdown(
    '<div class="dest-strip">' +
    "".join(
        f'<div class="dest-card"><img src="{u}"/>'
        f'<div class="tag">{n} <span class="dest-temp">{t}</span></div></div>'
        for n, t, u in DESTINATIONS
    ) +
    '</div>',
    unsafe_allow_html=True,
)

# ── Input ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown('<div class="input-label"><span class="input-icon">🗺</span> Describe your trip</div>', unsafe_allow_html=True)

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
generate = st.button("✦  Generate My Travel Plan", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
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

            # Footer
            st.markdown("""
            <div class="footer-sig">
              Built with ♥ by <span class="brand-text">Wayfarer</span> · Multi-Agent AI Travel Concierge
            </div>
            """, unsafe_allow_html=True)

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
