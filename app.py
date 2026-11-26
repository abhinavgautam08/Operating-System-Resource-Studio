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
