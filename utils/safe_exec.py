# utils/safe_exec.py

import matplotlib
matplotlib.use("Agg")  # headless rendering

import matplotlib.pyplot as plt
import multiprocessing as mp
import pandas as pd
import pickle
import traceback
import io
import re
from pandas.io.formats.style import Styler
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.image import AxesImage


# -----------------------------
# Detects if LLM generated a Styler heatmap
# -----------------------------
def _wants_styler_heatmap(code_str: str) -> bool:
    s = code_str.lower()
    return ("style" in s and "background_gradient" in s) or \
           ("style" in s and "highlight" in s)


# -----------------------------
# Worker executed in sandboxed process
# -----------------------------
def _worker(code_str, df_bytes, out_q):
    try:
        df = pickle.loads(df_bytes)

        # If LLM generated a Styler heatmap → convert to imshow heatmap
        if _wants_styler_heatmap(code_str):
            code_str = "result = df.corr().plot(kind='imshow', cmap='coolwarm')"

        safe_globals = {"__builtins__": {}}
        safe_locals = {"df": df, "pd": pd, "plt": plt}

        exec(code_str, safe_globals, safe_locals)

        result = safe_locals.get("result", None)

        # ---------------------------------------------------
        # Case 1: Pandas Styler (return as HTML)
        # ---------------------------------------------------
        if isinstance(result, Styler):
            try:
                html = result.to_html()
                out_q.put(("ok_html", html))
                return
            except Exception:
                out_q.put(("ok", str(result)))
                return

        # ---------------------------------------------------
        # Case 2: Detect matplotlib Figure / Axes / AxesImage
        # ---------------------------------------------------
        fig = None

        if isinstance(result, Figure):
            fig = result

        elif isinstance(result, Axes):
            fig = result.figure

        elif isinstance(result, AxesImage):
            fig = result.axes.figure

        else:
            # Result is None but plot was created implicitly
            if plt.get_fignums():
                fig = plt.gcf()

        # If any figure found → convert to PNG
        if fig is not None:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_bytes = buf.read()

            plt.close(fig)
            plt.close("all")

            out_q.put(("plot", img_bytes))
            return

        # ---------------------------------------------------
        # Normal outputs (DataFrame / Series / scalar)
        # ---------------------------------------------------
        if isinstance(result, (pd.DataFrame, pd.Series)):
            out_q.put(("ok", result))
            return

        if isinstance(result, (int, float, str, list, dict, tuple, bool, type(None))):
            out_q.put(("ok", result))
            return

        # Try to pickle result
        try:
            pickle.dumps(result)
            out_q.put(("ok", result))
            return
        except Exception:
            out_q.put(("ok", str(result)))
            return

    except Exception:
        out_q.put(("error", traceback.format_exc()))
        return


# -----------------------------
# Public API
# -----------------------------
def run_code_safely(code_str, df, timeout=15):
    """
    Runs user/LLM-generated Pandas code in a separate process (sandbox).
    
    Returns dict with:
      - {"status":"ok", "result": object}
      - {"status":"ok_html", "result": "<html>...</html>"}
      - {"status":"plot", "result": b"...PNG_BYTES..."}
      - {"status":"error", "error": "traceback..."}
    """
    ctx = mp.get_context("spawn")
    out_q = ctx.Queue()

    df_bytes = pickle.dumps(df)
    p = ctx.Process(target=_worker, args=(code_str, df_bytes, out_q))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return {"status": "error", "error": "Execution timed out and was terminated."}

    if not out_q.empty():
        status, payload = out_q.get()
        if status in ("ok", "ok_html", "plot"):
            return {"status": status, "result": payload}
        else:
            return {"status": "error", "error": payload}

    return {"status": "error", "error": "No output from worker."}
