🌟 DATAWHIZ – AI Data Analyst
Upload datasets → Ask questions → Get instant insights, visualizations & pandas code

🚀 Overview

DATAWHIZ – AI Data Analyst is an interactive web app that turns natural language questions into real, executable pandas code.
You upload a CSV/Excel file, ask questions like:

“Show the average glucose value by outcome”
“Plot BMI vs Age”
“Find missing values per column”

… and the app instantly gives you:

✔ AI-generated pandas code

✔ Visualizations (scatter, bar, line, heatmaps, etc.)

✔ Tabular results

✔ Downloadable CSV outputs

✔ Secure sandbox execution with timeout

Built using Flask, Groq LLaMA 3.3, pandas, matplotlib, and a fully sandboxed execution environment.

🎯 Features
🧹 Smart Data Cleaning

Automatically handles:

Type inference

Date conversions

Corrupted quotes

Missing value handling

Cleaned CSV download

🧠 Ask Any Question

AI turns your query into valid pandas code that is:

Safe

Clean

Executable

Downloadable

📊 Visual Insights

Supports:

Scatter plots

Histograms

Line plots

Bar graphs

Heatmaps

Correlation analysis

🔒 Safe Execution

All AI-generated code runs inside:

A separate Python worker

No external imports allowed

Timeout protection

No filesystem access

🏗 Tech Stack
Layer	Technologies
Frontend	TailwindCSS, AOS Animations, Lottie Animations
Backend	Flask, Python
AI	Groq API (LLaMA-3.3 70B)
Data	pandas, matplotlib
Isolation	Multiprocessing Sandbox
📁 Project Structure
AI_Data_Analyst/
│── app.py
│── config.py
│── requirements.txt
│── .gitignore
│── static/
│   ├── images/
│   └── style.css
│── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── analyze.html
│   └── result.html
│── utils/
│   ├── preprocess.py
│   ├── safe_exec.py
│   ├── groq_handler.py
│   └── summarize.py
└── samples/
    └── diabetes.csv   (optional)
