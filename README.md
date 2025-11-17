# DATAWHIZ – AI Data Analyst 🧠📊

An interactive AI-powered web application for seamless and secure data analysis. Ask questions about your datasets in natural language and get instant answers, visualizations, and exportable results!

## 🚀 Features

- **Upload CSV/Excel files** directly
- **Ask questions** about your data with natural language
- **Automatic pandas code generation** and safe execution
- **Interactive visualizations** (charts, tables) rendered on the fly
- **Download cleaned and result data** as CSV
- **Powered by Flask, Groq LLaMA 3.3, pandas, and matplotlib**

## Demo

![Demo GIF or Screenshot Here](link-to-demo.gif)

## 🔧 Getting Started

### Prerequisites

- Python 3.8+
- See `requirements.txt` for dependencies:
    - flask>=2.0
    - pandas>=1.5
    - openpyxl>=3.0
    - groq
    - python-dotenv>=0.21.0

### Installation

1. Clone the repository:
    ```
    git clone https://github.com/Sai2475/AI_Data_Analyst.git
    cd AI_Data_Analyst
    ```
2. Install requirements:
    ```
    pip install -r requirements.txt
    ```
3. Set up environment variables:
    - Add your `GROQ_API_KEY` to a `.env` file
    - Optionally set `FLASK_SECRET`

4. Run the application:
    ```
    python app.py
    ```
5. Open your browser and navigate to `http://localhost:5000`

## ✨ How It Works

1. Upload your CSV/XLSX file on the web interface
2. The app cleans/preprocesses your data
3. Ask natural language questions ("Show age distribution", "Plot sales over time", etc.)
4. The LLM generates pandas/matplotlib code that's evaluated in a secure sandbox
5. View results instantly – in tables or charts
6. Download processed or analyzed data as needed

## 🗂 Structure

- `app.py` — Main Flask web server handling file uploads, Q&A, code execution, visualization, and downloads
- `utils/` — Helper modules (preprocessing, safe code execution, LLM handler, summarization)
- `templates/` — HTML templates for UI pages
- `static/` — Static assets (images, CSS, JS)
- `requirements.txt` — Dependency list
- `config.py` — App configuration details
- `diabetes.csv` — Example dataset

## 🔒 Security

- User code is sandboxed for safe execution
- Supported file types: `.csv`, `.xlsx`
- Maximum upload size and secret key config for safety

## 📈 Usage Tips

- Questions like *"show mean by gender"*, *"plot sales trend"*, *"summarize missing values"* work best
- If your code fails to run, check file format and question phrasing

## 🤝 Contributing

PRs and suggestions welcome! Open an issue first for major proposals.

## 📄 License

[MIT License](LICENSE)

---

Enjoy instant data insights with AI!
