import os
import uuid
import pandas as pd

from dotenv import load_dotenv
load_dotenv()   # <-- IMPORTANT: Load .env before anything else

from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from utils.preprocess import preprocess_file
from utils.safe_exec import run_code_safely as safe_exec
from utils.groq_handler import generate_code
from utils.summarize import summarize_dataframe
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

print("Loaded GROQ KEY:", os.getenv("GROQ_API_KEY"))


UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {".csv", ".xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_me")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

file_map = {}

def allowed_filename(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT


@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Please upload a CSV or XLSX file.", "error")
            return redirect(request.url)

        if not allowed_filename(file.filename):
            flash("Unsupported file type. Use .csv or .xlsx", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(save_path)

        df, cleaned_path, err = preprocess_file(save_path)
        if err:
            flash(f"Preprocessing error: {err}", "error")
            return redirect(request.url)

        file_id = uuid.uuid4().hex
        file_map[file_id] = {"original": save_path, "cleaned": cleaned_path}

        pickle_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{file_id}.pkl")
        df.to_pickle(pickle_path)

        summary = summarize_dataframe(df)
        preview_html = df.head().to_html(classes="table-auto w-full")

        return render_template(
            "upload.html",
            summary=summary,
            preview_html=preview_html,
            file_id=file_id,
            cleaned_name=os.path.basename(cleaned_path),
        )

    return render_template("upload.html")


@app.route("/download/<file_id>")
def download_cleaned(file_id):
    meta = file_map.get(file_id)
    if not meta:
        flash("File not found or expired.", "error")
        return redirect(url_for("upload_page"))
    return send_file(meta["cleaned"], as_attachment=True,
                     download_name=os.path.basename(meta["cleaned"]))


@app.route("/analyze/<file_id>", methods=["GET", "POST"])
def analyze_page(file_id):

    df_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{file_id}.pkl")
    if not os.path.exists(df_path):
        flash("Dataset not found. Please upload again.", "error")
        return redirect(url_for("upload_page"))

    df = pd.read_pickle(df_path)

    if request.method == "POST":
        query = request.form.get("query")
        code = generate_code(query, columns=df.columns.tolist())

        # Heuristic to detect plot-y questions early (keeps previous behavior)
        plot_keywords = [
            "plot(", ".plot", "hist(", "bar(", "line(", "scatter(", "boxplot(",
            "df.plot", "plot.bar", "plot.hist"
        ]
        is_plot = any(k in code for k in plot_keywords)

        # If you prefer to execute plotting code in main process (no sandbox),
        # keep the old behavior. Otherwise the sandbox can also return plots.
        if is_plot:
            try:
                safe_globals = {"__builtins__": {}}
                safe_locals = {"df": df, "pd": pd, "plt": plt}

                exec(code, safe_globals, safe_locals)
                result = safe_locals.get("result")

                # If result is axes/figure, render it
                import matplotlib
                if result is not None:
                    if hasattr(result, "figure"):
                        fig = result.figure
                        import io, base64
                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight")
                        buf.seek(0)
                        img_bytes = buf.read()
                        plt.close(fig)
                        plt.close("all")
                        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                        result_html = f"<img src='data:image/png;base64,{img_b64}' class='mx-auto rounded shadow-lg' />"
                        return render_template("result.html", code=code, result_html=result_html, file_id=file_id, result_file=None)

                # If we didn't get a figure from direct exec, fall back to sandbox run
            except Exception as e:
                # If main-process plotting fails, fall back to sandbox below
                pass

        # Run sandboxed worker which now supports plots and styler-html
        res = safe_exec(code, df, timeout=15)

        # ---- Plot result (bytes) ----
        if res["status"] == "plot":
            import base64
            img_bytes = res["result"]
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            result_html = f"<img src='data:image/png;base64,{img_b64}' class='mx-auto rounded shadow-lg' />"
            return render_template("result.html", code=code, result_html=result_html, file_id=file_id, result_file=None)

        # ---- Styled HTML (pandas Styler) ----
        if res["status"] == "ok_html":
            result_html = res["result"]  # already HTML
            return render_template("result.html", code=code, result_html=result_html, file_id=file_id, result_file=None)

        # ---- Normal result (DataFrame / scalar) ----
        if res["status"] == "ok":
            result = res["result"]

            if isinstance(result, pd.DataFrame):
                result_html = result.to_html(classes="table-auto w-full")
                result_file = os.path.join(app.config["UPLOAD_FOLDER"], f"result_{uuid.uuid4().hex}.csv")
                result.to_csv(result_file, index=False)
            else:
                result_html = "<pre>" + str(result) + "</pre>"
                result_file = None

            return render_template("result.html", code=code, result_html=result_html, file_id=file_id, result_file=result_file)

        # ---- Error ----
        return render_template("result.html", code=code, error=res.get("error"), file_id=file_id)

    # GET request
    return render_template("analyze.html", columns=df.columns.tolist(), file_id=file_id)
@app.route("/download_result")
def download_result():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        flash("Result file not found.", "error")
        return redirect(url_for("upload_page"))

    return send_file(
        path,
        as_attachment=True,
        download_name=os.path.basename(path)
    )

# -------------------------------
# THIS BLOCK MUST BE LAST
# -------------------------------
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    print("Flask server starting...")
    app.run(debug=True)

