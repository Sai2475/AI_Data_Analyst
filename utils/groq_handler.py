import os
from groq import Groq

# CLEAN CODE BLOCKS
def _strip_code_blocks(text):
    text = text.strip()

    # Remove fenced blocks
    if text.startswith("```"):
        parts = text.split("```")
        cleaned = "".join(parts[1:-1]).strip()
        text = cleaned

    # Remove leading "python"/"py"
    if text.lower().startswith("python"):
        text = text[6:].strip()

    if text.lower().startswith("py"):
        text = text[2:].strip()

    return text.strip("`").strip()


# GENERATE CODE FROM QUERY
def generate_code(query: str, columns=None) -> str:

    print("GroqHandler sees key:", os.getenv("GROQ_API_KEY"))  # Debug

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Server Groq API key is not set (GROQ_API_KEY).")

    if columns:
        col_list = ", ".join(columns)
        col_hint = f"Columns available in df: {col_list}\n"
    else:
        col_hint = ""

    prompt = f"""
You are an expert Python data analyst.

Write ONLY valid Python code for a DataFrame named `df`.

QUESTION:
{query}

{col_hint}

RULES:
- IMPORTANT: Use ONLY pandas and plotly.graph_objects (go).
- Do NOT import matplotlib or seaborn.
- Do NOT use df.style or any HTML styling.
- When creating charts, ALWAYS use this format:

    import plotly.graph_objects as go
    fig = go.Figure(data=[ ... ])
    result = fig

- For correlation heatmap, ALWAYS use:

    import plotly.graph_objects as go
    corr = df.corr()
    heatmap = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu'
    ))
    result = heatmap

- If the answer is a table: return a DataFrame in `result`.
- If it's a number/text: store the raw value in `result`.
- The LAST line MUST define: result = ...

Return ONLY the code, no explanations.
"""

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )

    raw = completion.choices[0].message.content
    return _strip_code_blocks(raw)
