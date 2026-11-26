from __future__ import annotations

import json
import re
import sys
import unittest
from collections import deque
from copy import deepcopy
from dataclasses import dataclass

if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv = [a for a in sys.argv if a != "--test"]
        _RUN_TESTS_ON_MAIN = True
    else:
        _RUN_TESTS_ON_MAIN = False
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is None:
            from streamlit.web import cli as stcli

            sys.argv = ["streamlit", "run", __file__, *sys.argv[1:]]
            sys.exit(stcli.main())
else:
    _RUN_TESTS_ON_MAIN = False

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

PALETTE = [
    "#1F4E79",
    "#2E75B6",
    "#A6611A",
    "#4D7C5F",
    "#7F5A83",
    "#B08D57",
    "#6B7B8C",
    "#9C4A3C",
]
INK = "#1A1A1A"
MUTED = "#5F5F5F"
FAINT = "#8A8A8A"
RULE = "#DAD5C9"
GRID = "#E7E2D8"
IDLE = "#B9B2A3"
FREE_FILL = "#EFECE4"
SURFACE = "#FFFFFF"
SERIF = "Source Serif 4, Georgia, serif"
MONO = "IBM Plex Mono, SFMono-Regular, Consolas, monospace"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
  --paper:#FBFAF7; --surface:#FFFFFF; --ink:#1A1A1A; --muted:#5F5F5F;
  --faint:#8A8A8A; --rule:#DAD5C9; --rule-strong:#B9B2A3;
  --accent:#1F4E79; --accent-dark:#173B5C; --wash:#EAF0F6;
  --ok:#3F6B4F; --warn:#8C5A1B; --bad:#8C2F1B;
}

html, body, .stApp{background:var(--paper); color:var(--ink);}
.stApp{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stDecoration"]{display:none;}
#MainMenu{visibility:hidden;}
[data-testid="stSidebar"]{background:var(--surface); border-right:1px solid var(--rule);}

.block-container{max-width:1120px; padding:2.2rem 2rem 4rem;}

.top-nav{
  display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:14px;
  padding:0.9rem 0 1.1rem; margin-bottom:0.6rem;
  border-bottom:1px solid var(--rule);
}
.top-brand{display:flex; align-items:center; gap:14px;}
.top-logo{
  font-family:'IBM Plex Mono',monospace; font-size:.82rem; letter-spacing:.12em;
  font-weight:600; color:var(--accent); border:1px solid var(--accent);
  padding:.22rem .5rem; border-radius:2px;
}
.top-title{
  font-family:'Source Serif 4',Georgia,serif; font-size:1.45rem; font-weight:600;
  color:var(--ink); letter-spacing:-.01em;
}
.top-sub{
  font-family:'IBM Plex Mono',monospace; font-size:.68rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint);
}

h1,h2,h3,h4{font-family:'Source Serif 4',Georgia,serif !important; color:var(--ink) !important; font-weight:600 !important;}
h1{font-size:2.1rem; letter-spacing:-.01em; margin:.15rem 0 .35rem !important;}
h2{font-size:1.32rem; border-bottom:1px solid var(--rule); padding-bottom:.35rem; margin-top:2rem !important;}
h3{font-size:1.05rem; margin-top:1.3rem !important;}
p, li{font-size:.95rem; line-height:1.6; color:var(--muted);}

.page-head{border-bottom:1px solid var(--rule); padding-bottom:1rem; margin-bottom:1.5rem;}
.kicker{font-family:'IBM Plex Mono',monospace; font-size:.68rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); margin-bottom:.35rem;}
.lede{color:var(--muted); font-size:.95rem; margin:.1rem 0 0; max-width:74ch;}

.stat{border-top:2px solid var(--ink); padding:.65rem 0 0;}
.stat-label{font-family:'IBM Plex Mono',monospace; font-size:.66rem; letter-spacing:.12em;
  text-transform:uppercase; color:var(--faint);}
.stat-value{font-family:'Source Serif 4',Georgia,serif; font-size:1.7rem; font-weight:600;
  color:var(--ink); line-height:1.2; margin:.2rem 0 .1rem; font-variant-numeric:tabular-nums;}
.stat-value.ok{color:var(--ok);}
.stat-value.bad{color:var(--bad);}
.stat-note{font-family:'IBM Plex Mono',monospace; font-size:.66rem; color:var(--faint);}

.panel{background:var(--surface); border:1px solid var(--rule); border-radius:2px;
  padding:1.05rem 1.25rem; margin:.5rem 0 1rem;}
.panel p:last-child{margin-bottom:0;}

.callout{border:1px solid var(--rule); border-left:3px solid var(--accent); background:var(--surface);
  border-radius:2px; padding:.85rem 1.1rem; margin:.75rem 0 1.1rem;
  font-family:'IBM Plex Mono',monospace; font-size:.8rem; color:var(--ink);}
.callout.ok{border-left-color:var(--ok);}
.callout.bad{border-left-color:var(--bad);}
.callout.warn{border-left-color:var(--warn);}

.stButton > button, .stDownloadButton > button{
  border-radius:2px; font-family:'IBM Plex Mono',monospace;
  font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; min-height:38px;
  transition:background-color .12s ease, border-color .12s ease;
}
.stButton > button[kind="primary"]{background:var(--accent); border:1px solid var(--accent);}
.stButton > button[kind="primary"] p{color:#fff !important;}
.stButton > button[kind="primary"]:hover{background:var(--accent-dark); border-color:var(--accent-dark);}
.stButton > button[kind="secondary"], .stDownloadButton > button{
  background:transparent; border:1px solid var(--rule-strong); color:var(--ink);
}
.stButton > button[kind="secondary"] p, .stDownloadButton > button p{color:var(--ink) !important;}
.stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover{
  border-color:var(--accent); background:var(--wash);
}
.stButton > button[kind="secondary"]:hover p, .stDownloadButton > button:hover p{color:var(--accent) !important;}

[data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label{
  font-family:'IBM Plex Mono',monospace; font-size:.66rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint);
}
[data-baseweb="select"] > div, [data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea{
  border-radius:2px !important; border-color:var(--rule-strong) !important; background:var(--surface) !important;
  font-family:'IBM Plex Mono',monospace !important; font-size:.82rem !important;
}
[data-baseweb="select"] > div:focus-within, [data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus{
  border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent) !important;
}

