# LankaMart FAQ Chatbot

A simple FAQ chatbot built with Python, NLTK and scikit-learn. It matches a
user's question against a curated FAQ set using TF-IDF + cosine similarity,
and answers through a Streamlit chat UI.

## Pipeline
1. **FAQ data** — `faqs.csv` (question, answer, category, keywords).
2. **Preprocessing (NLTK)** — lowercase, strip punctuation/digits, tokenize,
   remove stopwords, lemmatize.
3. **Matching** — TF-IDF vectorization of FAQ questions, then cosine
   similarity against the user's (same-processed) query.
4. **Response** — best-matching answer is returned if similarity clears a
   confidence threshold (0.30); otherwise the bot says it isn't sure and
   shows its closest guesses.
5. **UI** — Streamlit chat interface (`st.chat_message` / `st.chat_input`),
   plus a browsable FAQ list by category.

NLTK data is bundled in `nltk_data/` so the app works offline without
needing to hit an external download server at runtime.

## Run it locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) — open
it in your browser to chat with the bot.

## Project structure
```
.
├── app.py             # Streamlit app: preprocessing, matching, chat UI
├── faqs.csv           # FAQ dataset (question, answer, category, keywords)
├── nltk_data/          # Bundled NLTK corpora (punkt, stopwords, wordnet)
├── requirements.txt
└── README.md
```

## Notes / limitations
- Matching is lexical (TF-IDF), so very different phrasings of the same
  question may not always score highly unless a paraphrase is present in
  the `keywords` column.
- The similarity threshold (`SIMILARITY_THRESHOLD` in `app.py`) can be
  tuned to make the bot more or less willing to guess.
