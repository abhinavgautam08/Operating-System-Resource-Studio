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

.stTabs [data-baseweb="tab-list"]{gap:1.4rem; border-bottom:1px solid var(--rule);}
.stTabs [data-baseweb="tab"]{background:transparent; border-radius:0; padding:.45rem 0;
  font-family:'IBM Plex Mono',monospace; font-size:.7rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--faint);}
.stTabs [aria-selected="true"]{color:var(--accent) !important; border-bottom:2px solid var(--accent);}

[data-testid="stDataFrame"]{border:1px solid var(--rule); border-radius:2px; overflow:hidden;}
[data-testid="stDataFrame"] *{font-family:'IBM Plex Mono',monospace !important; font-size:.78rem !important;}

hr{border:none; border-top:1px solid var(--rule); margin:1.6rem 0;}
.footer{font-family:'IBM Plex Mono',monospace; font-size:.66rem; color:var(--faint);
  border-top:1px solid var(--rule); padding-top:.8rem; margin-top:3rem; letter-spacing:.04em;}
.note{font-family:'IBM Plex Mono',monospace; font-size:.7rem; color:var(--faint); line-height:1.6;}
</style>
"""

PRESETS: dict[str, dict] = {
    "Lab Standard (Default)": {
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 7, "priority": 2},
            {"pid": "P2", "arrival": 2, "burst": 4, "priority": 1},
            {"pid": "P3", "arrival": 4, "burst": 1, "priority": 3},
            {"pid": "P4", "arrival": 5, "burst": 4, "priority": 2},
        ],
        "memory": {
            "blocks": [100, 500, 200, 300, 600],
            "requests": [212, 417, 112, 426, 95],
        },
        "deadlock": {
            "available": [3, 3, 2],
            "allocation": [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2],
            ],
            "maximum": [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3],
            ],
        },
        "disk": {
            "requests": [98, 183, 37, 122, 14, 124, 65, 67],
            "head": 53,
            "disk_size": 200,
            "direction": "right",
        },
    },
    "Idle Gaps & Convoy": {
        "quantum": 3,
        "processes": [
            {"pid": "P1", "arrival": 1, "burst": 9, "priority": 3},
            {"pid": "P2", "arrival": 2, "burst": 2, "priority": 1},
            {"pid": "P3", "arrival": 3, "burst": 1, "priority": 2},
            {"pid": "P4", "arrival": 16, "burst": 4, "priority": 1},
            {"pid": "P5", "arrival": 17, "burst": 3, "priority": 2},
        ],
        "memory": {
            "blocks": [150, 350, 250, 450, 180],
            "requests": [140, 200, 310, 175, 90],
        },
        "deadlock": {
            "available": [2, 3, 0],
            "allocation": [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 3],
                [2, 1, 1],
                [0, 0, 2],
            ],
            "maximum": [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 3],
                [2, 2, 2],
                [4, 3, 3],
            ],
        },
        "disk": {
            "requests": [176, 79, 34, 60, 92, 11, 41, 114],
            "head": 50,
            "disk_size": 200,
            "direction": "left",
        },
    },
    "Unsafe Deadlock & Fragmentation": {
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 6, "priority": 2},
            {"pid": "P2", "arrival": 0, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 1, "burst": 5, "priority": 3},
            {"pid": "P4", "arrival": 2, "burst": 2, "priority": 1},
        ],
        "memory": {
            "blocks": [200, 150, 300, 120],
            "requests": [180, 140, 250, 130, 110],
        },
        "deadlock": {
            "available": [1, 0, 0],
            "allocation": [
                [1, 1, 0],
                [2, 1, 1],
                [1, 0, 2],
                [0, 2, 1],
            ],
            "maximum": [
                [4, 2, 2],
                [3, 3, 2],
                [3, 1, 3],
                [2, 3, 2],
            ],
        },
        "disk": {
            "requests": [190, 10, 175, 25, 160, 40, 145],
            "head": 100,
            "disk_size": 200,
            "direction": "right",
        },
    },
}


def get_preset(name: str) -> dict:
    return deepcopy(PRESETS[name])


def parse_int_list(text: str) -> list[int]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        raise ValueError("Enter at least one integer value.")
    return [int(p) for p in parts]


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0

    def __post_init__(self) -> None:
        if not str(self.pid).strip():
            raise ValueError("Process ID cannot be empty.")
        if self.arrival < 0:
            raise ValueError(f"Arrival time for {self.pid} must be non-negative.")
        if self.burst <= 0:
            raise ValueError(f"Burst time for {self.pid} must be positive.")


def _build_segments_with_idle(timeline: list[tuple[int, int, str]]) -> list[dict]:
    segments = []
    current_time = 0

    for start, end, pid in timeline:
        if start > current_time:
            segments.append({"pid": "IDLE", "start": current_time, "end": start})
        segments.append({"pid": pid, "start": start, "end": end})
        current_time = end

    return segments


def _cpu_metrics(
    processes: list[Process],
    completion: dict[str, int],
    timeline: list[tuple[int, int, str]],
    algorithm: str,
) -> dict:
    rows = []
    for p in processes:
        finish_time = completion[p.pid]
        turnaround = finish_time - p.arrival
        waiting = turnaround - p.burst
        first_start = next(start for start, _, pid in timeline if pid == p.pid)
        response = first_start - p.arrival

        rows.append(
            {
                "pid": p.pid,
                "arrival": p.arrival,
                "burst": p.burst,
                "priority": p.priority,
                "completion": finish_time,
                "turnaround": turnaround,
                "waiting": waiting,
                "response": response,
            }
        )

    makespan = max(completion.values()) if completion else 0
    total_burst = sum(p.burst for p in processes)
    cpu_utilization = (total_burst / makespan * 100.0) if makespan > 0 else 0.0
    throughput = (len(processes) / makespan) if makespan > 0 else 0.0

    segments = _build_segments_with_idle(timeline)
    non_idle = [s for s in segments if s["pid"] != "IDLE"]
    context_switches = max(0, len(non_idle) - 1)

    return {
        "algorithm": algorithm,
        "processes": rows,
        "timeline": timeline,
        "segments": segments,
        "avg_waiting": sum(r["waiting"] for r in rows) / len(rows),
        "avg_turnaround": sum(r["turnaround"] for r in rows) / len(rows),
        "avg_response": sum(r["response"] for r in rows) / len(rows),
        "makespan": makespan,
        "cpu_utilization": cpu_utilization,
        "throughput": throughput,
        "context_switches": context_switches,
    }


def _pick_next_process(ready: list[Process], alg: str, original_order: dict[str, int]) -> Process:
    if alg == "fcfs":
        return min(ready, key=lambda p: (p.arrival, original_order[p.pid]))
    if alg == "sjf":
        return min(ready, key=lambda p: (p.burst, p.arrival, original_order[p.pid]))
    return min(ready, key=lambda p: (p.priority, p.arrival, original_order[p.pid]))


def _run_non_preemptive(processes: list[Process], alg: str) -> tuple[dict[str, int], list[tuple[int, int, str]]]:
    original_order = {p.pid: idx for idx, p in enumerate(processes)}
    pending = list(processes)
    now = 0
    completion: dict[str, int] = {}
    timeline: list[tuple[int, int, str]] = []

    while pending:
        ready = [p for p in pending if p.arrival <= now]
        if not ready:
            now = min(p.arrival for p in pending)
            ready = [p for p in pending if p.arrival <= now]

        chosen = _pick_next_process(ready, alg, original_order)
        start = now
        now += chosen.burst
        timeline.append((start, now, chosen.pid))
        completion[chosen.pid] = now
        pending.remove(chosen)

    return completion, timeline


def _run_round_robin(processes: list[Process], quantum: int) -> tuple[dict[str, int], list[tuple[int, int, str]]]:
    original_order = {p.pid: idx for idx, p in enumerate(processes)}
    arrivals = sorted(processes, key=lambda p: (p.arrival, original_order[p.pid]))
    remaining = {p.pid: p.burst for p in processes}
    ready: deque[Process] = deque()

    now = 0
    index = 0
    completion: dict[str, int] = {}
    timeline: list[tuple[int, int, str]] = []

    while index < len(arrivals) or ready:
        if not ready and index < len(arrivals) and now < arrivals[index].arrival:
            now = arrivals[index].arrival

        while index < len(arrivals) and arrivals[index].arrival <= now:
            ready.append(arrivals[index])
            index += 1

        current = ready.popleft()
        run_time = min(quantum, remaining[current.pid])
        start = now
        now += run_time
        timeline.append((start, now, current.pid))
        remaining[current.pid] -= run_time

        while index < len(arrivals) and arrivals[index].arrival <= now:
            ready.append(arrivals[index])
            index += 1

        if remaining[current.pid] > 0:
            ready.append(current)
        else:
            completion[current.pid] = now

    return completion, timeline


def cpu_schedule(processes: list[Process], algorithm: str = "fcfs", quantum: int = 2) -> dict:
    ps = list(processes)
    if not ps:
        raise ValueError("At least one process is required.")
    if len({p.pid for p in ps}) != len(ps):
        raise ValueError("Process IDs must be unique.")

    alg = algorithm.lower()
    if alg not in ("fcfs", "sjf", "priority", "rr"):
        raise ValueError(f"Unknown scheduling algorithm: {algorithm}")
    if alg == "rr" and quantum <= 0:
        raise ValueError("Round-robin quantum must be positive.")

    if alg == "rr":
        completion, timeline = _run_round_robin(ps, quantum)
    else:
        completion, timeline = _run_non_preemptive(ps, alg)

    return _cpu_metrics(ps, completion, timeline, alg)


def _choose_memory_block(free: list[int], size: int, strat: str) -> int | None:
    candidates = [i for i, space in enumerate(free) if space >= size]
    if not candidates:
        return None
    if strat == "first_fit":
        return candidates[0]
    if strat == "best_fit":
        return min(candidates, key=lambda i: free[i])
    return max(candidates, key=lambda i: free[i])


def mem_allocate(blocks: list[int], requests: list[int], strategy: str = "first_fit") -> dict:
    if not blocks or any(not isinstance(x, int) or x <= 0 for x in blocks):
        raise ValueError("Memory blocks must be positive integers.")
    if any(not isinstance(x, int) or x <= 0 for x in requests):
        raise ValueError("Memory requests must be positive integers.")

    strat = strategy.lower()
    if strat not in ("first_fit", "best_fit", "worst_fit"):
        raise ValueError(f"Unknown allocation strategy: {strategy}")

    free = list(blocks)
    block_contents: list[list[dict]] = [[] for _ in blocks]
    rows: list[dict] = []

    for idx, size in enumerate(requests, 1):
        chosen = _choose_memory_block(free, size, strat)
        if chosen is not None:
            free[chosen] -= size
            block_contents[chosen].append({"request": f"R{idx}", "size": size})

        rows.append(
            {
                "request": idx,
                "label": f"R{idx}",
                "size": size,
                "block": chosen + 1 if chosen is not None else None,
                "remaining_in_block": free[chosen] if chosen is not None else None,
                "allocated": chosen is not None,
            }
        )

    total_capacity = sum(blocks)
    total_allocated = sum(r["size"] for r in rows if r["allocated"])
    total_free = sum(free)
    allocated_count = sum(1 for r in rows if r["allocated"])

    return {
        "strategy": strat,
        "allocations": rows,
        "initial_blocks": list(blocks),
        "final_free": free,
        "block_contents": block_contents,
        "allocated_count": allocated_count,
        "unallocated_count": len(rows) - allocated_count,
        "total_capacity": total_capacity,
        "total_allocated": total_allocated,
        "total_free": total_free,
        "utilization_pct": (total_allocated / total_capacity * 100.0) if total_capacity else 0.0,
        "internal_fragmentation": total_free,
    }


def banker_safety(available: list[int], allocation: list[list[int]], maximum: list[list[int]]) -> dict:
    num_procs = len(allocation)
