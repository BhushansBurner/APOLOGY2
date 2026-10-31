# A little apology from your boy — Streamlit app (Version 8)

A romantic, mobile-friendly, page-by-page letter with animated apology GIFs, one page per memory photo, a reflection after the memories, and a final free-form call-time suggestion.

## Story order

1. Romantic opening with animated boyfriend-apology and teddy-bear GIFs plus an animated envelope.
2. One page for each memory photo, with its title and caption.
3. **Why I wanted us to talk** — appears after the memories and explains why they matter and why you do not want misunderstandings to decide the relationship.
4. **Can we set aside time for a proper call?** — the health context is the opening paragraph on this page. She can type any day/time or time window she prefers. There are no preset time choices and no meeting request. Once a time is entered, a WhatsApp button prepares a message to you.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

No `secrets.toml` file is needed.

## Add your photos

Put each memory photo in `assets/`. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`. The animated GIFs are for the cover and are not included in the memory gallery. For the most predictable order, name your images `photo1.jpg`, `photo2.jpg`, and so on (or use matching numbered filenames such as `photo1.png`).

The app also supports other image names. It first looks for an exact filename key in `photo_captions.json`; if none is found, it uses the numbered `photo1`, `photo2`, etc. caption entry for the photo's natural-sorted position.

## Add photo titles and descriptions

Edit `photo_captions.json`, which must stay in the same folder as `app.py`. Use this format:

```json
{
  "photo1.jpg": {
    "title": "Our little adventure",
    "caption": "I still remember how happy I felt that day. ❤️"
  }
}
```

If captions do not appear, check that your photos are inside `assets/`, the JSON file is beside `app.py`, and the keys match the photo filenames or numbered positions. The app now displays a warning if the JSON file is missing or invalid.

## Set up the WhatsApp call-time suggestion

Open `contact_config.json` and put your WhatsApp number with country code, digits only (no `+`, spaces, or hyphens):

```json
{
  "whatsapp_number": "919876543210"
}
```

When she types a timing on the final page, the app creates a WhatsApp link addressed to that number. It prepares a message containing the time she typed; she still reviews and taps **Send** inside WhatsApp. The page has a free-text field only, not a set of suggested times.

## Deploy

1. Upload the entire folder to a GitHub repository, including `assets/`, `photo_captions.json`, and `contact_config.json`.
2. In Streamlit Community Cloud, create an app from the repository and select `app.py`.
3. Share the deployed URL.

Anyone with the app URL can view the message and photos. Only add images you're comfortable sharing through that link.
