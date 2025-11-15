import os
from groq import Groq

# -------------------------------
# CLEAN CODE BLOCKS
# -------------------------------
def _strip_code_blocks(text):
    text = text.strip()

    # Remove triple backtick blocks
    if text.startswith("```"):
        parts = text.split("```")
        cleaned = "".join(parts[1:-1]).strip()
        text = cleaned

    # Remove leading "python" or "py"
    if text.lower().startswith("python"):
        text = text[6:].strip()

    if text.lower().startswith("py"):
        text = text[2:].strip()

    # Remove stray backticks
    text = text.strip("`").strip()

    return text


# -------------------------------
# GENERATE CODE FROM QUERY
# -------------------------------
def generate_code(query: str, columns=None) -> str:

    print("GroqHandler sees key:", os.getenv("GROQ_API_KEY"))  # DEBUG

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Server Groq API key is not set (GROQ_API_KEY).")

    if columns:
        col_list = ", ".join(columns)
        col_hint = f"\nColumns available in df: {col_list}\n"
    else:
        col_hint = ""

    prompt = f"""
You are an expert Python pandas data analyst. Write ONLY valid pandas code for the DataFrame `df`.

QUESTION:
{query}

{col_hint}

RULES:
- Do NOT import anything.
- Do NOT use seaborn, numpy, matplotlib, or df.style.
- Do NOT use df.corr().style.background_gradient.
- Do NOT generate heatmap using 'kind="heatmap"' (pandas does NOT support that).
- If user asks for a heatmap or correlation visualization,
  ALWAYS use this syntax:
      result = df.corr().plot(kind='imshow', cmap='coolwarm')

- Store the final output in a variable named `result`.
"""

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )

    raw = completion.choices[0].message.content
    return _strip_code_blocks(raw)
