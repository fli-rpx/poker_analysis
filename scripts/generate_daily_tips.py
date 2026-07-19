#!/usr/bin/env python3
"""Generate daily-tips.html from data/tips.json"""
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
TIPS_PATH = ROOT / "data" / "tips.json"
OUT_PATH = ROOT / "daily-tips.html"

with open(TIPS_PATH) as f:
    tips = json.load(f)

# Normalize categories
CAT_MAP = {"Mental Game": "Psychology", "Bankroll": "Sessions", "Tournament": "Live Play",
           "Live Reads": "Live Play", "Hand Reading": "Postflop", "Turn/River": "Postflop",
           "Positional": "Preflop"}
for t in tips:
    t["cat"] = CAT_MAP.get(t["category"], t["category"])

# Detect today's tip for "Today's Tip" section
today_date = datetime.now().strftime("%b %-d").replace(" 0", " ")
today_tip = next((t for t in tips if t.get("date", "").lower() == today_date.lower()), None)
today_day = today_tip["day"] if today_tip else None

COLS = {
    "Preflop": ('#d4af37', 'rgba(212,175,55,0.12)'),
    "Postflop": ('#27AE60', 'rgba(39,174,96,0.12)'),
    "Math": ('#4A90D9', 'rgba(74,144,217,0.12)'),
    "Psychology": ('#E74C3C', 'rgba(231,76,60,0.12)'),
    "Live Play": ('#E67E22', 'rgba(230,126,34,0.12)'),
    "Sessions": ('#9B59B6', 'rgba(155,89,182,0.12)'),
}

CATS = ["ALL", "PREFLOP", "POSTFLOP", "MATH", "PSYCHOLOGY", "LIVE PLAY", "SESSIONS"]

filter_btns = ""
for c in CATS:
    act = ' active' if c == 'ALL' else ''
    filter_btns += f'<button class="filter-btn{act}" data-filter="{c}">{c}</button>\n'

tips_json_raw = json.dumps(tips, ensure_ascii=True)

# All the Tailwind-like CSS
CSS = """
:root{--bg:#0a0a0a;--surface:#1a1a1e;--surface-hover:#222228;--gold:#d4af37;--gold-dim:#a08028;--text-primary:#f5f5f0;--text-dim:#a0a0a0;--text-muted:#6b6b70;--border:#2a2a2e}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:Inter,sans-serif;background:var(--bg);color:var(--text-primary);line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:"Playfair Display",Georgia,serif;font-weight:700;letter-spacing:-0.01em}
a{color:var(--gold);text-decoration:none}
.app{display:flex;flex-direction:column;height:100vh;overflow:hidden}
.top-bar{flex:0 0 auto;background:linear-gradient(180deg,rgba(26,26,30,0.95)0%,rgba(26,26,30,0.85)100%);border-bottom:1px solid var(--border);padding:1rem 1.25rem;z-index:10}
.top-inner{max-width:1400px;margin:0 auto}
.brand-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:.875rem}
.brand{font-family:"Playfair Display",Georgia,serif;font-size:1.5rem;color:var(--gold)}
.brand span{color:var(--text-primary);font-weight:500}
.mobile-toggle{display:none;background:rgba(212,175,55,0.1);border:1px solid var(--gold-dim);color:var(--gold);padding:.45rem .85rem;border-radius:8px;font-size:.85rem;font-weight:600;cursor:pointer}
.controls{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem}
.filter-group{display:flex;flex-wrap:wrap;gap:.4rem}
.filter-btn{background:transparent;border:1px solid var(--border);color:var(--text-dim);padding:.4rem .75rem;border-radius:999px;font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em;cursor:pointer;transition:all .2s}
.filter-btn:hover{border-color:var(--gold-dim);color:var(--text-primary)}
.filter-btn.active{background:var(--gold);border-color:var(--gold);color:#0a0a0a;box-shadow:0 0 14px rgba(212,175,55,0.18)}
.search-wrap{position:relative;flex:1 1 220px;min-width:180px;max-width:320px}
.search-wrap svg{position:absolute;left:.75rem;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--text-muted);pointer-events:none}
.search-input{width:100%;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:10px;padding:.55rem .85rem .55rem 2.25rem;color:var(--text-primary);font-size:.9rem;outline:none;transition:border-color .2s}
.search-input::placeholder{color:var(--text-muted)}
.search-input:focus{border-color:var(--gold-dim);box-shadow:0 0 0 3px rgba(212,175,55,0.18)}
.main{flex:1;display:flex;overflow:hidden;max-width:1400px;width:100%;margin:0 auto}
.sidebar{flex:0 0 320px;display:flex;flex-direction:column;background:rgba(26,26,30,0.55);border-right:1px solid var(--border)}
.sidebar-header{padding:1rem 1.25rem;border-bottom:1px solid var(--border)}
.count{font-size:.8rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em}
.count strong{color:var(--gold);font-size:1.1rem;margin-right:.2rem}
.tip-list{flex:1;overflow-y:auto;padding:.5rem}
.tip-item{display:flex;align-items:flex-start;gap:.85rem;padding:.85rem .9rem;border-radius:10px;cursor:pointer;transition:background .18s;margin-bottom:.35rem;border:1px solid transparent}
.tip-item:hover{background:var(--surface-hover)}
.tip-item.active{background:rgba(212,175,55,0.12);border-color:var(--gold-dim);box-shadow:inset 4px 0 0 var(--gold)}
.day-badge{flex:0 0 32px;height:32px;border-radius:50%;display:grid;place-items:center;background:rgba(255,255,255,0.05);border:1px solid var(--border);font-size:.8rem;font-weight:700;color:var(--text-dim)}
.tip-item.active .day-badge{background:var(--gold);color:#0a0a0a;border-color:var(--gold)}
.tip-meta{flex:1;min-width:0}
.tip-item-title{font-size:.95rem;font-weight:600;color:var(--text-primary);line-height:1.35;margin-bottom:.35rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tip-item.active .tip-item-title{color:var(--gold)}
.badge{display:inline-block;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:.2rem .5rem;border-radius:4px}
.content{flex:1;overflow-y:auto;padding:2rem 2.5rem}
.content-inner{max-width:760px;margin:0 auto;animation:fadeIn .35s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;color:var(--text-muted);padding:2rem}
.empty-state svg{width:64px;height:64px;margin-bottom:1.25rem;color:var(--gold-dim);opacity:.7}
.empty-state h2{font-size:1.35rem;color:var(--text-primary);margin-bottom:.5rem}
.empty-state p{font-size:.95rem;max-width:320px}
.tip-header{margin-bottom:1.5rem}
.tip-cat-badge{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;padding:.35rem .75rem;border-radius:6px;margin-bottom:.75rem;display:inline-block}
.tip-date-line{font-size:.85rem;color:var(--gold);font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.5rem}
.tip-title{font-size:2rem;line-height:1.2;color:var(--text-primary);margin-bottom:.5rem;font-family:"Playfair Display",Georgia,serif}
.tip-summary{color:var(--text-dim);font-size:1.05rem;line-height:1.85}
.tip-summary p{margin-bottom:1.25rem}
.tip-summary p:last-child{margin-bottom:0}
.gold-sep{display:block;text-align:center;color:var(--gold-dim);font-size:.9rem;letter-spacing:.5em;margin:1.75rem 0;user-select:none}
.today-banner{background:linear-gradient(135deg,rgba(212,175,55,0.2),rgba(212,175,55,0.08));border:1px solid var(--gold-dim);border-radius:10px;padding:.75rem 1rem;margin-bottom:1.25rem;font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--gold);text-align:center;box-shadow:0 0 20px rgba(212,175,55,0.1)}
.today-tag{display:inline-block;font-size:.6rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em;padding:.15rem .4rem;border-radius:3px;background:var(--gold);color:#0a0a0a;margin-left:.35rem;vertical-align:middle;line-height:1.2}
.overlay{display:none}
@media(max-width:900px){
.mobile-toggle{display:inline-block}
.main{position:relative}
.sidebar{position:absolute;top:0;left:0;bottom:0;width:min(86vw,320px);z-index:20;transform:translateX(-105%);transition:transform .3s;box-shadow:4px 0 24px rgba(0,0,0,0.5)}
.sidebar.open{transform:translateX(0)}
.overlay{display:block;position:absolute;inset:0;background:rgba(0,0,0,0.55);opacity:0;pointer-events:none;transition:opacity .3s;z-index:15}
.overlay.open{opacity:1;pointer-events:auto}
.content{padding:1.5rem}
.tip-title{font-size:1.6rem}
}
"""

COLORS_JSON = json.dumps({k: list(v) for k, v in COLS.items()})

JS = f"""\
var TIPS = {tips_json_raw};
var CM = {COLORS_JSON};
var TD = {today_day if today_day else "null"};
var activeFilter="ALL",activeId=TD;
var fG=document.getElementById("filterGroup"),sI=document.getElementById("searchInput"),tL=document.getElementById("tipList"),cI=document.getElementById("contentInner"),eS=document.getElementById("emptyState"),tC=document.getElementById("tipCount"),sB=document.getElementById("sidebar"),oL=document.getElementById("overlay"),mT=document.getElementById("mobileToggle");
function n(s){{return(s||"").toLowerCase().replace(/[^a-z0-9]/g,"")}}
function getTips(){{var q=n(sI.value);return TIPS.filter(function(t){{return(activeFilter==="ALL"||t.cat.toUpperCase()===activeFilter)&&(!q||n(t.title).indexOf(q)!==-1||n(t.summary).indexOf(q)!==-1)}})}}
function fmt(t){{return t.split("\\n\\n").map(function(p){{return"<p>"+p.replace(/\\n/g,"<br/>")+"</p>"}}).join("")}}
function badge(cat,cls){{var m=CM[cat]||CM.Preflop;return'<span class="'+cls+'" style="color:'+m[0]+";background:"+m[1]+";border:1px solid "+m[0]+'30;">'+cat+"</span>"}}
function rList(){{var tips=getTips();tC.textContent=tips.length;tL.innerHTML=tips.map(function(t){{return'<div class="tip-item'+(activeId===t.day?" active":"")+'" data-day="'+t.day+'"><div class="day-badge">'+(t.day===TD?"\\u2605":t.day)+'</div><div class="tip-meta"><div class="tip-item-title">'+t.title.replace(/"/g,"&quot;")+'</div>'+badge(t.cat,"badge")+(t.day===TD?' <span class="today-tag">TODAY</span>':"")+'</div></div>'}}).join("");if(activeId!==null){{var el=tL.querySelector('[data-day="'+activeId+'"]');if(el)el.scrollIntoView({{block:"nearest",behavior:"smooth"}})}}}}
function rContent(t){{if(!t)return;var m=CM[t.cat]||CM.Preflop;var banner=t.day===TD?'<div class="today-banner">\\u2605 TODAY TIP</div>':"";cI.innerHTML=banner+'<article class="tip-header"><span class="tip-cat-badge" style="color:'+m[0]+";background:"+m[1]+";border:1px solid "+m[0]+'30;">'+t.cat+'</span><div class="tip-date-line">'+t.date+'</div><h2 class="tip-title">'+t.title+'</h2></article><div class="gold-sep">\\u25c6 \\u25c6 \\u25c6</div><div class="tip-summary">'+fmt(t.summary)+"</div>";eS.style.display="none";cI.style.display="block";cI.style.animation="none";void cI.offsetHeight;cI.style.animation=""}}
function selectTip(d){{if(activeId===d){{activeId=null;eS.style.display="flex";cI.style.display="none";rList();return}}activeId=d;rContent(TIPS.find(function(t){{return t.day===d}}));rList();if(window.innerWidth<=900)closeS()}}
function openS(){{sB.classList.add("open");oL.classList.add("open")}}
function closeS(){{sB.classList.remove("open");oL.classList.remove("open")}}
fG.addEventListener("click",function(e){{if(!e.target.classList.contains("filter-btn"))return;activeFilter=e.target.dataset.filter;document.querySelectorAll(".filter-btn").forEach(function(b){{b.classList.toggle("active",b.dataset.filter===activeFilter)}});rList()}});
sI.addEventListener("input",rList);
tL.addEventListener("click",function(e){{var i=e.target.closest(".tip-item");if(i)selectTip(parseInt(i.dataset.day,10))}});
mT.addEventListener("click",openS);
oL.addEventListener("click",closeS);
document.addEventListener("keydown",function(e){{if(e.key==="Escape")closeS()}});
rList();if(TD){{var t=TIPS.find(function(x){{return x.day===TD}});if(t)rContent(t)}}
"""

# fmt fix: the f-string doubles braces. The JS function needs double-backslash for \\n
# In the f-string, \\\\n → \\n → JS sees \\n which is a newline escape
# And \\n\\n → \\n\\n → JS sees \\n\\n which is double newline (paragraph separator)
# But the ensure_ascii=True JSON already has \\uXXXX escapes for Unicode
# The summary stored in TIPS has literal \\n\\n (from the JSON file) → JS sees \\n\\n → we split on "\\n\\n"

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Daily Tips — The River</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet"/>
<style>{CSS}</style>
</head>
<body>
<div class="app">
<header class="top-bar">
<div class="top-inner">
<div class="brand-row">
<h1 class="brand"><a href="./index.html" style="color:inherit;text-decoration:none">The River <span>— Daily Tips</span></a></h1>
<button class="mobile-toggle" id="mobileToggle" aria-label="Open tip list">&#9776; Tips</button>
</div>
<div class="controls">
<div class="filter-group" id="filterGroup">
{filter_btns}
</div>
<div class="search-wrap">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
<input type="text" class="search-input" id="searchInput" placeholder="Search tips..." autocomplete="off"/>
</div>
</div>
</div>
</header>
<div class="main">
<aside class="sidebar" id="sidebar">
<div class="sidebar-header">
<div class="count"><strong id="tipCount">{len(tips)}</strong> tips available</div>
</div>
<div class="tip-list" id="tipList"></div>
</aside>
<div class="overlay" id="overlay"></div>
<section class="content" id="content">
<div class="empty-state" id="emptyState">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
<h2>Select a tip from the left</h2>
<p>Choose a daily tip to read the full lesson.</p>
</div>
<div class="content-inner" id="contentInner" style="display:none;"></div>
</section>
</div>
</div>
<script>{JS}</script>
</body>
</html>"""

OUT_PATH.write_text(HTML, encoding="utf-8")
size = len(HTML)
print(f"Generated {OUT_PATH} ({size} bytes, {len(tips)} tips)")
