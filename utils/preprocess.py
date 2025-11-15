# utils/preprocess.py
import pandas as pd
import csv
import os

def _escape_quotes(df):
    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)
    return df

def _convert_types(df):
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif df[col].dtype == "object":
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass
    return df

def preprocess_file(file_path):
    """
    Reads the file from file_path, cleans it, saves cleaned CSV into uploads/cleaned_<uuid>.csv
    Returns (df, cleaned_path, error_str_or_None)
    """
    try:
        _, ext = os.path.splitext(file_path.lower())
        if ext == ".csv":
            df = pd.read_csv(file_path, encoding="utf-8", na_values=["NA", "N/A", "missing"])
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path, na_values=["NA", "N/A", "missing"])
        else:
            return None, None, "Unsupported file format."

        df = _escape_quotes(df)
        df = _convert_types(df)

        # Save cleaned file to uploads/ prefix (use same filename cleaned_)
        base = os.path.basename(file_path)
        cleaned_name = f"cleaned_{base}"
        cleaned_path = os.path.join("uploads", cleaned_name)
        df.to_csv(cleaned_path, index=False, quoting=csv.QUOTE_ALL)

        return df, cleaned_path, None
    except Exception as e:
        return None, None, str(e)
