# 🌐 Language Translation Tool

A simple web app built with Streamlit that lets users enter text, choose a source and target language, and get an instant translation. Includes optional text-to-speech playback for the translated result.

## Features

- Enter any text and translate it between multiple languages
- Auto-detect source language
- Copy-to-clipboard for translated text
- Optional text-to-speech playback of the translation
- Handles rate-limit errors from the translation service gracefully (with automatic retry)

## Tech Stack

- **Python 3**
- **Streamlit** – web UI
- **deep-translator** – translation engine (Google Translate wrapper)
- **gTTS** – text-to-speech

## Setup & Installation

1. Clone this repository:
   ```
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   ```
   Windows:
   ```
   .venv\Scripts\activate
   ```
   macOS/Linux:
   ```
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app:
   ```
   streamlit run app.py
   ```

## Usage

1. Select a source language (or leave on Auto Detect).
2. Select a target language.
3. Enter the text you want to translate.
4. Click **Translate**.
5. Optionally, click the copy icon to copy the result, or play the audio version.

## Notes

- Translation is powered by a free, unofficial Google Translate endpoint via `deep-translator`. It's rate-limited (~5 requests/second), so heavy usage may occasionally trigger a short delay while the app retries automatically.
- Text-to-speech is not available for every language.

## License

This project was built as part of an internship task.
