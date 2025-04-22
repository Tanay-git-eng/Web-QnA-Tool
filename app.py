import streamlit as st
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os
import google.api_core.exceptions  # Import for specific Gemini API error catching

# --- Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Web Q&A with Gemini",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📘"  # Optional: Add a page icon
)

# --- Load Environment Variables & Configure API ---
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini client - Essential check before proceeding
api_configured_successfully = False
if not gemini_api_key:
    st.sidebar.error("🔴 **Error:** GEMINI_API_KEY not found.")
    st.error("API Key Configuration Failed: Please set the GEMINI_API_KEY in your .env file.", icon="🚨")
    st.stop()  # Stop execution if no key
else:
    try:
        genai.configure(api_key=gemini_api_key)
        st.sidebar.success("✅ Gemini API Key Configured")
        api_configured_successfully = True
    except Exception as e:
        st.sidebar.error(f"🔴 **Error Configuring Gemini:** {e}")
        st.error(f"API Key Configuration Failed: Could not configure the Gemini client. Error: {e}", icon="🚨")
        st.stop()

# --- Session State Initialization ---
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

# --- Utility Functions ---

def text_preview(text, length=250):
    """Shortens text for previews, removing excess whitespace."""
    if not isinstance(text, str): text = str(text)
    preview_text = ' '.join(text.split())  # Consolidate whitespace
    return preview_text[:length] + ("..." if len(preview_text) > length else "")

def extract_text_from_url(url):
    """Extracts main textual content from a webpage URL."""
    st.write(f"Attempting to fetch: {url}")  # Debug fetch attempt
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)  # Increased timeout
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type:
            st.warning(f"⚠️ Skipped {url}: Content is not HTML ({content_type})")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        for element in soup(["script", "style", "nav", "footer", "aside", "header", "form"]):  # Remove non-content elements
            element.decompose()

        main_content = soup.find('main') or soup.find('article') or soup.find(role='main')
        target_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'span', 'div']

        container_to_search = main_content if main_content else soup.find('body')
        if not container_to_search:
            st.warning(f"⚠️ Could not find main content or body in {url}")
            return None

        text_elements = container_to_search.find_all(target_tags)
        text_chunks = [element.get_text(separator=' ', strip=True) for element in text_elements]
        full_text = "\n".join(chunk for chunk in text_chunks if chunk and len(chunk.split()) > 2)  # Filter short/empty chunks
        cleaned_text = ' '.join(full_text.split())

        st.write(f"Successfully fetched {len(cleaned_text)} characters from: {url}")  # Debug success
        return cleaned_text if cleaned_text else "No relevant text found."

    except requests.exceptions.Timeout:
        st.warning(f"⚠️ Timeout fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else 'N/A'
        st.warning(f"⚠️ Failed to fetch {url}: Status {status_code} - {e}")
        return None
    except Exception as e:
        st.warning(f"⚠️ Error parsing {url}: {type(e).__name__} - {e}")
        return None

def get_answer_from_context(context, question):
    """Gets an answer from Gemini based on provided context and question."""
    if not api_configured_successfully:  # Double-check API config
        return "Error: Gemini API not configured."
    if not context or not question:
        return "Error: Missing context or question."

    try:
        # --- Use the more standard model identifier ---
        model = genai.GenerativeModel("gemini-1.5-pro")

        prompt = (
            "You are an AI assistant. Answer the following question based *only* on the provided text context.\n"
            "Do not use any external knowledge. If the answer isn't in the context, state exactly: "
            "'The answer is not available in the provided context.'\n\n"
            "=== CONTEXT START ===\n"
            f"{context}\n"
            "=== CONTEXT END ===\n\n"
            f"QUESTION: {question}\n\n"
            "ANSWER:"
        )

        response = model.generate_content(prompt)

        # Safely extract text from response
        try:
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif response.parts:
                return "".join(part.text for part in response.parts).strip()
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                return f"⚠️ Content generation blocked. Reason: {response.prompt_feedback.block_reason}."
            else:
                st.warning(f"Gemini returned an empty or unexpected response: {response}")
                return "⚠️ Gemini returned an empty response."
        except (AttributeError, ValueError) as e:
            st.warning(f"Could not parse response from Gemini: {e}")
            return "⚠️ Error parsing Gemini response."

    # --- Specific API Error Handling ---
    except google.api_core.exceptions.NotFound as e:
        st.error(f"🔴 **API Error: Model Not Found.** Ensure 'gemini-1.0-pro' is available/correctly named. Details: {e}", icon="🛰️")
        return "Error: Gemini model not found."
    except google.api_core.exceptions.PermissionDenied as e:
        st.error(f"🔴 **API Error: Permission Denied.** Check API Key, Gemini API enablement in Cloud project, and billing. Details: {e}", icon="🔒")
        return "Error: Permission denied (check API key/project)."
    except google.api_core.exceptions.ResourceExhausted as e:
        st.error(f"🔴 **API Error: Quota Exceeded.** Check usage limits. Details: {e}", icon="⏳")
        return "Error: API quota exceeded."
    except google.api_core.exceptions.InvalidArgument as e:
        st.error(f"🔴 **API Error: Invalid Argument.** Often due to API key format or request issues. Details: {e}", icon="📄")
        return f"Error: Invalid argument sent to API (check key format?). Details: {e}"
    except google.api_core.exceptions.InternalServerError as e:
        st.error(f"🔴 **API Error: Internal Server Error.** Google's servers might be busy. Try again later. Details: {e}", icon="⚙️")
        return "Error: Google internal server error. Try again later."
    except google.api_core.exceptions.GoogleAPIError as e:  # Catch other Google API errors
        st.error(f"🔴 **API Error:** {type(e).__name__} - {e}", icon="💥")
        return f"An API error occurred: {e}"
    except Exception as e:  # Catch-all for other unexpected errors
        st.error(f"🔴 **Unexpected Error during generation:** {type(e).__name__} - {e}", icon="💥")
        return f"An unexpected error occurred: {e}"

# --- Streamlit Web UI ---

# Optional: Custom CSS (minor tweaks)
st.markdown("""
    <style>
        .stTextArea textarea, .stTextInput input { font-size: 1rem; }
        .stButton>button { width: 100%; }
        .answer-box { background-color: #e8f0fe; border-left: 6px solid #1a73e8; padding: 1rem 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; line-height: 1.6; }
        .error-box { background-color: #fdeded; border-left: 6px solid #d93025; padding: 1rem 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
st.sidebar.title("⚙️ Configuration & Info")
st.sidebar.markdown("Uses Google Gemini to answer questions based on text scraped from web URLs.")
st.sidebar.markdown("**Status:**")
# Display API status from check earlier
if api_configured_successfully:
    st.sidebar.success("API Ready")
else:
    st.sidebar.error("API Not Configured")  # Should have stopped above, but for completeness

st.sidebar.markdown("**Instructions:**")
st.sidebar.markdown("1. Enter one or more URLs.")
st.sidebar.markdown("2. Ask a specific question.")
st.sidebar.markdown("3. Click 'Generate Answer'.")
st.sidebar.markdown("**Notes:**")
st.sidebar.markdown("- Scraping may fail on some sites.")
st.sidebar.markdown("- Answers based *only* on scraped text.")
st.sidebar.markdown("---")
st.sidebar.info("Ensure your virtual environment is active and required libraries are installed.")


# --- Main Page Content ---
st.title("📘 Web Content Q&A with Gemini")
st.caption("Enter URLs, ask a question, and get answers based on the website's text content.")

# --- Input Form ---
with st.form(key="qa_form"):
    st.markdown("##### 🔗 Step 1: Enter URLs")
    urls_input = st.text_area(
        "URLs (one per line):",
        height=100,
        placeholder="https://example.com/page1\nhttps://en.wikipedia.org/wiki/Artificial_intelligence",
        label_visibility="collapsed"
    )

    st.markdown("##### 🤔 Step 2: Ask Your Question")
    question_input = st.text_input(
        "Your Question:",
        placeholder="What is artificial intelligence?",
        label_visibility="collapsed"
    )

    submit_button = st.form_submit_button("Generate Answer")

# --- Process Inputs on Form Submit ---
if submit_button:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    question = question_input.strip()

    # Fetch text from URLs
    all_contexts = []
    for url in urls:
        context = extract_text_from_url(url)
        if context:
            all_contexts.append(context)

    # Generate and display answer
    if all_contexts:
        combined_context = "\n\n".join(all_contexts)
        answer = get_answer_from_context(combined_context, question)
        st.markdown(f"### Answer:")
        st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No valid content found from the provided URLs.")
