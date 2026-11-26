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
    num_res = len(available)

    if num_procs == 0 or len(maximum) != num_procs:
        raise ValueError("Resource matrices have inconsistent dimensions.")
    if any(len(row) != num_res for row in allocation + maximum):
        raise ValueError("Resource matrices have inconsistent dimensions.")
    if any(x < 0 for x in available) or any(x < 0 for row in allocation + maximum for x in row):
        raise ValueError("Resource counts cannot be negative.")
    if any(maximum[i][j] < allocation[i][j] for i in range(num_procs) for j in range(num_res)):
        raise ValueError("Maximum claim cannot be below current allocation.")

    work = list(available)
    finish = [False] * num_procs
    need = [[maximum[i][j] - allocation[i][j] for j in range(num_res)] for i in range(num_procs)]
    sequence: list[int] = []
    trace: list[dict] = []

    while True:
        progressed = False
        for i in range(num_procs):
            if finish[i]:
                continue
            can_finish = all(need[i][j] <= work[j] for j in range(num_res))
            if can_finish:
                work_before = list(work)
                work = [work[j] + allocation[i][j] for j in range(num_res)]
                finish[i] = True
                sequence.append(i)
                trace.append(
                    {
                        "step": len(sequence),
                        "process": f"P{i}",
                        "need": list(need[i]),
                        "work_before": work_before,
                        "allocation": list(allocation[i]),
                        "work_after": list(work),
                    }
                )
                progressed = True
        if not progressed:
            break

    is_safe = all(finish)
    return {
        "safe": is_safe,
        "sequence": sequence if is_safe else [],
        "unfinished": [i for i, done in enumerate(finish) if not done],
        "need": need,
        "trace": trace,
    }


def request_resources(
    available: list[int],
    allocation: list[list[int]],
    maximum: list[list[int]],
    process: int,
    request: list[int],
) -> dict:
    if not 0 <= process < len(allocation):
        raise ValueError("Process index out of range.")
    if len(request) != len(available) or any(x < 0 for x in request):
        raise ValueError("Invalid request vector.")

    need = [maximum[process][j] - allocation[process][j] for j in range(len(available))]
    if any(request[j] > need[j] for j in range(len(request))):
        return {"granted": False, "reason": "Request exceeds declared remaining need."}
    if any(request[j] > available[j] for j in range(len(request))):
        return {"granted": False, "reason": "Requested resources exceed currently available units."}

    next_alloc = [row[:] for row in allocation]
    next_avail = list(available)
    for j, amount in enumerate(request):
        next_alloc[process][j] += amount
        next_avail[j] -= amount

    check = banker_safety(next_avail, next_alloc, maximum)
    reason = "Safe state preserved" if check["safe"] else "Request would leave the system in an unsafe state"
    return {
        "granted": check["safe"],
        "reason": reason,
        "safety": check,
        "new_available": next_avail,
        "new_allocation": next_alloc,
    }


def _disk_order_sstf(requests: list[int], head: int) -> list[int]:
    remaining = list(enumerate(requests))
    order: list[int] = []
    current = head

    while remaining:
        best_idx, best_track = min(remaining, key=lambda pair: (abs(pair[1] - current), pair[0]))
        order.append(best_track)
        current = best_track
        remaining.remove((best_idx, best_track))

    return order


def _disk_order_scan(requests: list[int], head: int, disk_size: int, direction: str) -> list[int]:
    left = sorted((x for x in requests if x < head), reverse=True)
    right = sorted(x for x in requests if x >= head)

    if direction == "right":
        if left:
            return right + [disk_size - 1] + left
        return right

    if right:
        return left + [0] + right
    return left


def disk_schedule(
    requests: list[int],
    head: int,
    algorithm: str = "fcfs",
    disk_size: int = 200,
    direction: str = "right",
) -> dict:
    if not requests:
        raise ValueError("At least one disk track request is required.")
    if disk_size <= 0 or not 0 <= head < disk_size or any(not 0 <= x < disk_size for x in requests):
        raise ValueError(f"Track positions must be within [0, {disk_size - 1}].")

    alg = algorithm.lower()
    dir_norm = direction.lower()
    if alg not in ("fcfs", "sstf", "scan"):
        raise ValueError(f"Unknown disk algorithm: {algorithm}")
    if dir_norm not in ("left", "right"):
        raise ValueError("SCAN direction must be 'left' or 'right'.")

    if alg == "fcfs":
        order = list(requests)
    elif alg == "sstf":
        order = _disk_order_sstf(requests, head)
    else:
        order = _disk_order_scan(requests, head, disk_size, dir_norm)

    path = [head]
    step_distances = []
    total = 0

    for step_idx, target in enumerate(order, 1):
        prev = path[-1]
        dist = abs(target - prev)
        total += dist
        path.append(target)
        step_distances.append(
            {
                "step": step_idx,
                "from": prev,
                "to": target,
                "distance": dist,
                "cumulative": total,
            }
        )

    return {
        "algorithm": alg,
        "head": head,
        "direction": dir_norm,
        "order": order,
        "path": path,
        "step_distances": step_distances,
        "total_movement": total,
        "average_movement": total / len(requests),
        "disk_size": disk_size,
    }


def compute_all_subsystems(ds: dict) -> dict:
    processes = [Process(**p) for p in ds["processes"]]
    quantum = int(ds.get("quantum", 2))

    cpu_results = {alg: cpu_schedule(processes, alg, quantum=quantum) for alg in ("fcfs", "sjf", "priority", "rr")}
    mem_results = {
        strat: mem_allocate(ds["memory"]["blocks"], ds["memory"]["requests"], strat)
        for strat in ("first_fit", "best_fit", "worst_fit")
    }
    dl_result = banker_safety(
        ds["deadlock"]["available"],
        ds["deadlock"]["allocation"],
        ds["deadlock"]["maximum"],
    )
    disk_results = {
        alg: disk_schedule(
            ds["disk"]["requests"],
            int(ds["disk"]["head"]),
            alg,
            int(ds["disk"].get("disk_size", 200)),
            ds["disk"].get("direction", "right"),
        )
        for alg in ("fcfs", "sstf", "scan")
    }

    return {
        "scheduling": cpu_results,
        "memory": mem_results,
        "deadlock": dl_result,
        "disk": disk_results,
    }


def _pid_sort_key(pid: str) -> tuple:
    prefix, digits = re.match(r"^(\D*)(\d*)", str(pid)).groups()
    return (prefix, int(digits) if digits else -1, str(pid))


def style_fig(fig: go.Figure, title: str = "", height: int = 320) -> go.Figure:
    title_cfg = dict(text=title, font=dict(family=SERIF, size=15, color=INK), x=0, xanchor="left") if title else None
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        height=height,
        font=dict(family=MONO, size=11, color=MUTED),
        title=title_cfg,
        margin=dict(l=48, r=20, t=48 if title else 20, b=44),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=MUTED), title=None),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=RULE, font=dict(family=MONO, size=11, color=INK)),
        xaxis=dict(
            gridcolor=GRID,
            linecolor=IDLE,
            linewidth=1,
            zeroline=False,
            tickfont=dict(family=MONO, size=10, color=FAINT),
        ),
        yaxis=dict(
            gridcolor=GRID,
            linecolor=IDLE,
            linewidth=1,
            zeroline=False,
            tickfont=dict(family=MONO, size=10, color=FAINT),
        ),
    )
    return fig


def make_gantt(segments: list[dict]) -> go.Figure:
    pids = sorted(
        (p for p in dict.fromkeys(s["pid"] for s in segments) if p != "IDLE"),
        key=_pid_sort_key,
    )
    colors = {"IDLE": IDLE}
    for i, pid in enumerate(pids):
        colors[pid] = PALETTE[i % len(PALETTE)]

    fig = go.Figure()
    for seg in segments:
        duration = seg["end"] - seg["start"]
        fig.add_trace(
            go.Bar(
                x=[duration],
                y=["CPU"],
                base=[seg["start"]],
                orientation="h",
                name=seg["pid"],
                marker_color=colors[seg["pid"]],
                marker_line_color=SURFACE,
                marker_line_width=1,
                showlegend=False,
                text=[seg["pid"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(family=MONO, size=10, color="#FFFFFF"),
                hovertemplate=(
                    f"<b>{seg['pid']}</b><br>"
                    f"start&nbsp;&nbsp;{seg['start']}<br>"
                    f"end&nbsp;&nbsp;&nbsp;&nbsp;{seg['end']}<br>"
                    f"duration&nbsp;{duration}"
                    "<extra></extra>"
                ),
            )
        )

    end = max((s["end"] for s in segments), default=1)
    fig.update_layout(
        barmode="overlay",
        height=195,
        margin=dict(l=18, r=18, t=16, b=40),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=MONO, size=11, color=MUTED),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=RULE, font=dict(family=MONO, size=11, color=INK)),
        xaxis=dict(
            title=dict(text="time (units)", font=dict(family=MONO, size=10, color=FAINT)),
            range=[0, end],
            dtick=1 if end <= 30 else None,
            gridcolor=GRID,
            gridwidth=1,
            linecolor=IDLE,
            linewidth=1,
            zeroline=False,
            tickfont=dict(family=MONO, size=10, color=FAINT),
        ),
        yaxis=dict(showticklabels=False, showgrid=False),
    )
    return fig


def make_cpu_comparison_chart(cpu_results: dict[str, dict]) -> go.Figure:
    algs = [a.upper() for a in cpu_results.keys()]
    metrics = [
        ("Avg Waiting", "avg_waiting", PALETTE[0]),
        ("Avg Turnaround", "avg_turnaround", PALETTE[1]),
        ("Avg Response", "avg_response", PALETTE[3]),
    ]
    fig = go.Figure()
    for label, key, color in metrics:
        vals = [round(cpu_results[a.lower()][key], 2) for a in algs]
        fig.add_trace(
            go.Bar(
                name=label,
                x=algs,
                y=vals,
                marker_color=color,
                text=[f"{v:.2f}" for v in vals],
                textposition="outside",
                textfont=dict(family=MONO, size=10, color=MUTED),
            )
        )
    style_fig(fig, title="Scheduling Policy Comparison (time units)", height=330)
    fig.update_layout(barmode="group", yaxis_title="time (units)")
    return fig


def make_memory_map(mem_result: dict) -> go.Figure:
    blocks = mem_result["initial_blocks"]
    contents = mem_result["block_contents"]
    final_free = mem_result["final_free"]
    block_labels = [f"Block {i + 1} ({b})" for i, b in enumerate(blocks)]

    fig = go.Figure()
    max_parts = max((len(c) for c in contents), default=0)

    for part_idx in range(max_parts):
        sizes = []
        labels = []
        hovers = []
        for b_idx in range(len(blocks)):
            if part_idx < len(contents[b_idx]):
                item = contents[b_idx][part_idx]
                sizes.append(item["size"])
                labels.append(f"{item['request']} ({item['size']})")
                hovers.append(f"<b>{item['request']}</b><br>Block {b_idx + 1}<br>Size: {item['size']}")
            else:
                sizes.append(0)
                labels.append("")
                hovers.append("")

        fig.add_trace(
            go.Bar(
                y=block_labels,
                x=sizes,
                orientation="h",
                name=f"Segment {part_idx + 1}",
                showlegend=False,
                marker_color=PALETTE[part_idx % len(PALETTE)],
                marker_line_color=SURFACE,
                marker_line_width=1,
                text=labels,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(family=MONO, size=10, color="#FFFFFF"),
                hovertext=hovers,
                hoverinfo="text",
            )
        )

    fig.add_trace(
        go.Bar(
            y=block_labels,
            x=final_free,
            orientation="h",
            name="Free",
            showlegend=True,
            marker_color=FREE_FILL,
            marker_line_color=RULE,
            marker_line_width=1,
            text=[f"Free ({f})" if f > 0 else "" for f in final_free],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(family=MONO, size=10, color=MUTED),
            hovertemplate="<b>Free Space</b><br>%{y}<br>Remaining: %{x}<extra></extra>",
        )
    )

    style_fig(fig, title="Contiguous Block Partition Map", height=max(240, 48 * len(blocks) + 90))
    fig.update_layout(
        barmode="stack",
        xaxis_title="memory units",
        yaxis=dict(autorange="reversed", gridcolor=GRID, linecolor=IDLE, tickfont=dict(family=MONO, size=10, color=INK)),
    )
    return fig


def make_memory_comparison_chart(mem_results: dict[str, dict]) -> go.Figure:
    strats = list(mem_results.keys())
    labels = [s.replace("_", " ").title() for s in strats]
    utils = [round(mem_results[s]["utilization_pct"], 1) for s in strats]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=utils,
            marker_color=[PALETTE[0], PALETTE[1], PALETTE[3]],
            text=[f"{u:.1f}%" for u in utils],
            textposition="outside",
            textfont=dict(family=MONO, size=10, color=MUTED),
            showlegend=False,
        )
    )
    style_fig(fig, title="Memory Utilization by Strategy (%)", height=300)
    fig.update_layout(yaxis=dict(range=[0, 110], title="utilization (%)"))
    return fig


def make_disk_head_chart(disk_result: dict) -> go.Figure:
    path = disk_result["path"]
    steps = list(range(len(path)))

    fig = go.Figure()
    fig.add_trace(
