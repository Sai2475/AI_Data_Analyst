import pandas as pd 
import tempfile
import csv
from groq import Groq

def preprocess_and_save(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8', na_values=["NA","N/A","missing"])
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, na_values=["NA","N/A","missing"])
        else:
            return None, None, None,"unsupported file format."