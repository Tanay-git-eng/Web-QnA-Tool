📘 Web Content Q&A Tool
This is a Streamlit web app that lets you ask questions based solely on the content from any URL(s) you provide. It fetches and processes webpage content, sends it to OpenAI's GPT-4 model, and returns concise answers — with no external assumptions.

🚀 Features
🔗 Input one or more URLs
🤖 Ask questions and get answers using GPT-4o
📝 Source text previews highlighted for transparency
🌙 Sleek and minimal UI
🧰 Tech Stack
Streamlit
BeautifulSoup
Python-dotenv
📦 Installation
1. Clone the repo
git clone https://github.com/Tanay-git-eng/web-qna-tool.git
cd web-qna-tool
2. Create & activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  
venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Create a .env file in the project root
GEMINI_API_KEY="GEMINI_API_KEY"
❗Do NOT commit this file to GitHub. It contains sensitive data.

▶️ Run the App Locally
streamlit run app.py
🌐 Deploy to Streamlit Cloud
Push your code to GitHub (excluding .env)
Go to https://streamlit.io/cloud
Connect your repo and set your `GEMINI_API_KEY as a secret
Deploy!
📌 Notes
Answers are generated only from the content of the webpages provided.
Your API key will never be exposed if handled securely using .env or Streamlit secrets.
✨ Future Improvements
 Highlight answer text with source reference
 Export chat history as PDF or CSV
 Multi-language support
