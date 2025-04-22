# Web Content Q&A Tool

This is a Streamlit web app that lets you ask questions based solely on the content from any URL(s) you provide. It fetches and processes webpage content, sends it to Gemini model, and returns concise answers — with no external assumptions.

---

##  Features

-  Input one or more URLs
-  Ask questions and get answers using **Gemini Ai**
-  Source text previews highlighted for transparency
-  Sleek and minimal UI

---

##  Tech Stack

- [Streamlit](https://streamlit.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/Tanay-git-eng/web-qna-tools.git
cd web-qna-tool
```

### 2. Create & activate a virtual environment (optional but recommended)

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root

```env
Gemini_API_KEY=your_genini_api_key_here
```

** Do NOT commit this file to GitHub. It contains sensitive data.**

---

## Run the App Locally

```bash
streamlit run app.py
```

---

##  Deploy to Streamlit Cloud

1. Push your code to GitHub (excluding `.env`)
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your repo and set your `Gemini_API_KEY` as a **secret**
4. Deploy!

---
