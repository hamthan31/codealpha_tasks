"""
FAQ Chatbot - LankaMart Customer Support
-----------------------------------------
Pipeline:
  1. Load a curated FAQ set (question, answer, category).
  2. Preprocess every FAQ question and every user query with NLTK:
     lowercase -> remove punctuation/digits -> tokenize -> remove
     stopwords -> lemmatize.
  3. Vectorize the cleaned FAQ questions with TF-IDF.
  4. For a new user question, vectorize it with the same fitted TF-IDF
     model and rank FAQs by cosine similarity.
  5. Return the best-matching answer if the similarity clears a
     confidence threshold, otherwise ask the user to rephrase and show
     the closest suggestions.

Run locally with:
    streamlit run app.py
"""

import os
import re

import nltk
import pandas as pd
import streamlit as st

# Keep NLTK corpora alongside the app so the environment is self-contained
# and reproducible (no reliance on a machine-wide NLTK_DATA folder).
_NLTK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nltk_data")
os.makedirs(_NLTK_DIR, exist_ok=True)
if _NLTK_DIR not in nltk.data.path:
    nltk.data.path.insert(0, _NLTK_DIR)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_PATH = "faqs.csv"
SIMILARITY_THRESHOLD = 0.30  # below this, the bot admits it isn't confident

# --------------------------------------------------------------------------
# One-time NLTK resource check (data is pre-downloaded; this just verifies).
# Cached so it runs once per server process, not on every chat interaction.
# --------------------------------------------------------------------------
@st.cache_resource
def ensure_nltk_resources():
    for resource in ["tokenizers/punkt", "tokenizers/punkt_tab",
                      "corpora/stopwords", "corpora/wordnet", "corpora/omw-1.4"]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource.split("/")[-1], download_dir=_NLTK_DIR)
    return True

ensure_nltk_resources()

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

st.set_page_config(page_title="LankaMart FAQ Chatbot", page_icon="💬", layout="centered")


# --------------------------------------------------------------------------
# NLP preprocessing
# --------------------------------------------------------------------------
def preprocess(text: str) -> str:
    """Lowercase, strip punctuation/digits, tokenize, remove stopwords,
    lemmatize (verb pass then noun pass so 'returning'/'returns' both
    normalize towards 'return'). Returns a cleaned, space-joined string
    ready for TF-IDF."""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)          # drop punctuation & digits
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    tokens = [LEMMATIZER.lemmatize(t, pos="v") for t in tokens]
    tokens = [LEMMATIZER.lemmatize(t, pos="n") for t in tokens]
    return " ".join(tokens)


@st.cache_data
def load_faqs(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["keywords"] = df.get("keywords", "").fillna("")
    # Matching text = question + curated paraphrase keywords, so common
    # synonyms ("package"/"parcel" for "order", "money back" for "refund")
    # are captured without needing a full semantic model. Keywords are used
    # only for matching, never shown to the user as the FAQ question.
    df["match_text"] = (df["question"] + " " + df["keywords"]).str.strip()
    df["clean_question"] = df["match_text"].apply(preprocess)
    return df


@st.cache_resource
def build_vectorizer(clean_questions: list[str]):
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(clean_questions)
    return vectorizer, matrix


faqs = load_faqs(FAQ_PATH)
vectorizer, faq_matrix = build_vectorizer(faqs["clean_question"].tolist())


def match_faq(user_question: str, top_n: int = 3):
    """Return a DataFrame of the top_n closest FAQs with a similarity score."""
    clean_q = preprocess(user_question)
    if not clean_q.strip():
        return None
    query_vec = vectorizer.transform([clean_q])
    sims = cosine_similarity(query_vec, faq_matrix).flatten()
    ranked = faqs.copy()
    ranked["similarity"] = sims
    ranked = ranked.sort_values("similarity", ascending=False).head(top_n)
    return ranked


def get_bot_response(user_question: str):
    ranked = match_faq(user_question, top_n=3)
    if ranked is None or ranked.empty:
        return ("I couldn't understand that question. Could you rephrase it?",
                None, ranked)

    best = ranked.iloc[0]
    if best["similarity"] >= SIMILARITY_THRESHOLD:
        return (best["answer"], best, ranked)

    return (
        "I'm not fully sure I understood that. Here is my closest match, or "
        "try rephrasing your question:",
        best,
        ranked,
    )


# --------------------------------------------------------------------------
# Chat UI
# --------------------------------------------------------------------------
st.title("💬 LankaMart FAQ Chatbot")
st.caption(
    "Ask me about orders, shipping, returns, payments, your account or promotions. "
    f"Matching uses TF-IDF + cosine similarity over {len(faqs)} FAQs."
)

with st.sidebar:
    st.header("About this bot")
    st.write(
        "This assistant matches your question against a fixed FAQ set using "
        "NLTK preprocessing (tokenize, stopword removal, lemmatization) and "
        "TF-IDF cosine similarity — no external API calls."
    )
    st.metric("Confidence threshold", f"{SIMILARITY_THRESHOLD:.2f}")
    st.write("Browse the FAQ categories:")
    for cat in sorted(faqs["category"].unique()):
        st.write(f"- {cat}")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm the LankaMart support bot. What can I help you with today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your question, e.g. 'How do I return an item?'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    answer, best_match, ranked = get_bot_response(user_input)

    with st.chat_message("assistant"):
        st.markdown(answer)
        if best_match is not None:
            st.caption(
                f"Matched FAQ: \u201c{best_match['question']}\u201d "
                f"(similarity {best_match['similarity']:.2f}, category: {best_match['category']})"
            )
        if ranked is not None and len(ranked) > 1:
            with st.expander("See other related questions"):
                for _, row in ranked.iloc[1:].iterrows():
                    st.write(f"- **{row['question']}** (similarity {row['similarity']:.2f})")

    st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown("---")
st.subheader("📋 Browse all FAQs")
category_filter = st.selectbox("Filter by category", ["All"] + sorted(faqs["category"].unique().tolist()))
show = faqs if category_filter == "All" else faqs[faqs["category"] == category_filter]
for _, row in show.iterrows():
    with st.expander(row["question"]):
        st.write(row["answer"])
