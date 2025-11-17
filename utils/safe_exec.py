# utils/safe_exec.py

import multiprocessing as mp
import pandas as pd
import pickle
import traceback
import io
from pandas.io.formats.style import Styler
import plotly.io as pio
import plotly.graph_objects as go


# Detect Styler heatmap code
def _wants_styler_heatmap(code_str: str) -> bool:
    s = code_str.lower()
    return ("style" in s and "background_gradient" in s)


# Worker process
def _worker(code_str, df_bytes, out_q):
    try:
        df = pickle.loads(df_bytes)

        safe_globals = {"__builtins__": {}}
        safe_locals = {"df": df, "pd": pd, "go": go}

        # Fix heatmap -> Plotly version
        if _wants_styler_heatmap(code_str):
            code_str = """
import plotly.graph_objects as go
corr = df.corr()
heatmap = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu'))
result = heatmap
"""

        exec(code_str, safe_globals, safe_locals)

        result = safe_locals.get("result")

        # 1) Plotly Figure → Convert to HTML
        if hasattr(result, "to_html"):
            html = pio.to_html(result, include_plotlyjs='cdn', full_html=False)
            out_q.put(("ok_html", html))
            return

        # 2) Pandas Styler
        if isinstance(result, Styler):
            html = result.to_html()
            out_q.put(("ok_html", html))
            return

        # 3) DataFrame / Series
        if isinstance(result, (pd.DataFrame, pd.Series)):
            out_q.put(("ok", result))
            return

        # 4) Primitive types
        if isinstance(result, (int, float, str, bool, list, dict, tuple, type(None))):
            out_q.put(("ok", result))
            return

        # 5) Unknown → try to convert to string
        out_q.put(("ok", str(result)))
        return

    except Exception:
        out_q.put(("error", traceback.format_exc()))
        return


# Public API
def run_code_safely(code_str, df, timeout=15):
    ctx = mp.get_context("spawn")
    out_q = ctx.Queue()

    df_bytes = pickle.dumps(df)
    p = ctx.Process(target=_worker, args=(code_str, df_bytes, out_q))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return {"status": "error", "error": "Execution timed out."}

    if not out_q.empty():
        status, payload = out_q.get()
        if status in ("ok_html", "ok"):
            return {"status": status, "result": payload}
        return {"status": "error", "error": payload}

    return {"status": "error", "error": "No output received."}
