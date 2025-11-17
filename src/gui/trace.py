"""Utilities to capture step-by-step traces from TuringMachine runs.

We avoid modifying the TuringMachine class and instead rely on its debug
printing. We temporarily redirect stdout to capture the printed trace.
"""
from __future__ import annotations
import io
import sys
from contextlib import redirect_stdout
from typing import Tuple


def run_with_trace(tm, input_string: str, max_steps: int = 5000) -> Tuple[str, str]:
    """Run a TuringMachine instance with debug enabled and capture the trace.

    Returns (output_string, trace_text).
    """
    # Enable debug, capture stdout, then run
    try:
        if hasattr(tm, 'enable_debug_mode'):
            tm.enable_debug_mode()
        buff = io.StringIO()
        with redirect_stdout(buff):
            output = tm.run(input_string, max_steps=max_steps)
        trace = buff.getvalue()
        return output, trace
    finally:
        if hasattr(tm, 'disable_debug_mode'):
            tm.disable_debug_mode()


def safe_marks(s: str) -> str:
    """Return a printable summary for mark strings, using count for long inputs."""
    if not s:
        return "_ (vacío)"
    if set(s) <= {"|", "_", "+", "-", "X", "#"}:
        # If only simple tape symbols, show length-aware summary
        bars = s.count('|')
        if bars > 50:
            return f"{'|'*25}… (total {bars} marcas)"
        return s
    return s
