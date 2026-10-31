from __future__ import annotations

import base64
import html
import io
import json
import re
from urllib.parse import quote
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
ASSET_DIR = ROOT / "assets"
CAPTIONS_FILE = ROOT / "photo_captions.json"
CONTACT_CONFIG_FILE = ROOT / "contact_config.json"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

st.set_page_config(
    page_title="I'm sorry, baby 💗",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------- Romantic, phone-first visual design --------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=Caveat:wght@500;600;700&display=swap');
    :root { --ink:#54343f; --muted:#846a72; --rose:#b85d76; --rose2:#d98b9a; --line:#f0dce0; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp {
      background:
        radial-gradient(ellipse at 4% 4%, rgba(255,218,226,.85), transparent 30%),
        radial-gradient(ellipse at 96% 28%, rgba(255,232,216,.78), transparent 31%),
        radial-gradient(ellipse at 50% 100%, rgba(246,222,229,.65), transparent 35%),
        linear-gradient(145deg,#fffaf9 0%,#fff4f2 54%,#fbf0f2 100%);
      color:var(--ink);
    }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stToolbar"] { right:.5rem; }
    .block-container { max-width:760px; padding:1rem 1rem 2.8rem; }
    h1,h2,h3 { font-family:'Playfair Display',Georgia,serif !important; color:var(--ink); }
    p { color:var(--muted); }
    .eyebrow { text-transform:uppercase; letter-spacing:.22em; font-size:.67rem; font-weight:700; color:#b87988; text-align:center; }
    .cover {
      position:relative; isolation:isolate; overflow:hidden; text-align:center;
      border:1px solid rgba(231,190,201,.95); border-radius:32px;
      padding:clamp(1.8rem,6vw,3.25rem) clamp(1rem,4.5vw,2.7rem) 1.6rem;
      background:linear-gradient(145deg,rgba(255,255,255,.97),rgba(255,245,245,.96));
      box-shadow:0 26px 80px rgba(128,76,88,.13); animation:soft-arrive .9s ease both;
    }
    .cover:before,.cover:after { content:'✦'; position:absolute; z-index:-1; color:#d9a0ad; opacity:.55; animation:twinkle 3.4s ease-in-out infinite; }
    .cover:before { left:8%; top:10%; font-size:1.5rem; }
    .cover:after { right:8%; bottom:17%; font-size:1.7rem; animation-delay:1.1s; }
    .cover-title { font:600 clamp(2.55rem,9vw,4.1rem)/1.08 'Playfair Display',Georgia,serif; color:#563943; letter-spacing:-.035em; margin:.8rem 0 .75rem; }
    .cover-sub { max-width:530px; margin:0 auto; line-height:1.85; font-size:1rem; color:#866d74; }
    .gif-stage { display:grid; grid-template-columns:1fr 1fr; gap:.6rem; width:min(520px,100%); margin:1.45rem auto .75rem; align-items:center; }
    .gif-card { border:1px solid rgba(237,207,213,.85); border-radius:22px; background:linear-gradient(145deg,rgba(255,249,248,.97),rgba(255,237,240,.9)); padding:.3rem; box-shadow:0 10px 28px rgba(150,90,104,.08); animation:gentle-float 4.2s ease-in-out infinite; }
    .gif-card:nth-child(2) { animation-delay:1.1s; }
    .gif-card img { display:block; width:100%; height:auto; max-height:205px; object-fit:contain; }
    .envelope-stage { width:min(250px,75%); height:150px; margin:1rem auto .4rem; position:relative; }
    .envelope { position:absolute; inset:18px 0 0; height:128px; border-radius:14px; background:linear-gradient(145deg,#f5d4dc,#e9b5c1); box-shadow:0 16px 30px rgba(159,83,104,.19); animation:gentle-float 3.8s ease-in-out infinite; }
    .envelope:before { content:''; position:absolute; inset:0; border-radius:14px; background:linear-gradient(35deg,transparent 49.3%,rgba(255,255,255,.55) 50%,transparent 50.8%),linear-gradient(-35deg,transparent 49.3%,rgba(255,255,255,.45) 50%,transparent 50.8%); }
    .flap { position:absolute; top:0; left:0; width:100%; height:76px; background:#e8b4bf; clip-path:polygon(0 0,100% 0,50% 100%); transform-origin:top center; animation:flap-soft 4.2s ease-in-out infinite; }
    .letter-peek { position:absolute; left:12%; right:12%; top:15px; height:92px; border-radius:8px; background:#fffaf8; box-shadow:0 4px 9px rgba(115,70,80,.1); animation:peek-soft 4.2s ease-in-out infinite; }
    .letter-peek:after { content:'♥'; color:#bf7183; font-size:1.5rem; position:absolute; top:27px; left:0; right:0; }
    .seal { position:absolute; z-index:2; top:53px; left:50%; transform:translateX(-50%); width:51px; height:51px; border-radius:50%; display:grid; place-items:center; color:white; font-size:1.4rem; background:linear-gradient(145deg,#bd657a,#9f4e65); box-shadow:0 6px 17px rgba(125,52,72,.24); animation:heart-beat 2.1s ease-in-out infinite; }
    .script { font:600 1.7rem 'Caveat',cursive; color:#a85b70; margin:.35rem 0 .1rem; }
    .cover-note { color:#a17f88; font-size:.8rem; line-height:1.7; margin:.6rem auto 0; max-width:460px; }
    .page-top { text-align:center; padding:.45rem .3rem .4rem; animation:soft-arrive .6s ease both; }
    .page-title { font:600 clamp(2rem,7vw,3.05rem)/1.13 'Playfair Display',Georgia,serif; color:#563943; margin:.55rem 0 .55rem; }
    .page-sub { max-width:570px; margin:.3rem auto 0; line-height:1.85; font-size:.96rem; color:#866d74; }
    .story-card { border:1px solid rgba(239,218,222,.98); border-radius:27px; background:rgba(255,255,255,.92); padding:clamp(1.3rem,5vw,2.2rem); box-shadow:0 17px 52px rgba(116,65,77,.075); animation:soft-arrive .62s ease both; }
    .story-symbol { text-align:center; color:#cb8492; font-size:1.6rem; margin:0 0 .45rem; }
    .story-kicker { text-align:center; color:#bf7a89; text-transform:uppercase; letter-spacing:.19em; font-size:.65rem; font-weight:700; }
    .story-heading { text-align:center; font:600 clamp(1.8rem,6vw,2.4rem)/1.18 'Playfair Display',Georgia,serif; color:#563943; margin:.55rem 0 1.25rem; }
    .story-copy { color:#644b52; font-size:1rem; line-height:1.96; }
    .story-copy p { color:#644b52; margin:0 0 1.05rem; }
    .story-copy p:last-child { margin-bottom:0; }
    .photo-shell { border:1px solid #eedbde; border-radius:26px; padding:.65rem; background:rgba(255,255,255,.96); box-shadow:0 16px 42px rgba(116,65,77,.09); animation:soft-arrive .6s ease both; }
    .photo-frame { width:100%; max-height:72svh; min-height:100px; display:flex; justify-content:center; align-items:center; overflow:hidden; border-radius:19px; background:linear-gradient(145deg,#fbf0f1,#f8e9ed); }
    .photo-frame img { display:block; max-width:100%; max-height:72svh; width:auto; height:auto; object-fit:contain; }
    .photo-copy { text-align:center; padding:1.2rem .65rem .8rem; }
    .photo-title { font:600 clamp(1.55rem,5.5vw,2.05rem) 'Playfair Display',Georgia,serif; color:#63434d; margin:0 0 .55rem; }
    .photo-caption { max-width:550px; margin:0 auto; font-size:.96rem; line-height:1.85; color:#856b73; }
    .photo-count { color:#b77b88; text-align:center; text-transform:uppercase; letter-spacing:.2em; font-size:.65rem; font-weight:700; margin-bottom:.8rem; }
    .call-card { position:relative; overflow:hidden; text-align:center; padding:clamp(1.5rem,6vw,2.7rem); border-radius:29px; border:1px solid #e9cbd2; background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(255,239,242,.98)); box-shadow:0 20px 58px rgba(116,65,77,.1); animation:soft-arrive .7s ease both; }
    .call-heart { font-size:2.3rem; animation:heart-beat 2.4s ease-in-out infinite; }
    .call-title { font:600 clamp(2rem,7vw,2.75rem)/1.15 'Playfair Display',Georgia,serif; color:#563943; margin:.55rem 0 .85rem; }
    .call-copy { max-width:565px; margin:0 auto; color:#765d64; font-size:.98rem; line-height:1.92; }
    .call-copy p { color:#765d64; }
    .call-prompt { margin:1.3rem auto .8rem; color:#9b6071; font:600 1.55rem 'Caveat',cursive; }
    .time-wrap { background:rgba(255,255,255,.84); border:1px solid #efd9df; border-radius:22px; padding:1rem 1.1rem .8rem; margin:.8rem 0 1rem; text-align:left; }
    .time-caption { text-align:center; color:#9f6e7b; font-size:.79rem; line-height:1.7; margin:.3rem 0 .6rem; }
    .picked-time { margin:.75rem 0 1rem; padding:.8rem 1rem; border-radius:18px; text-align:center; color:#96566b; background:linear-gradient(110deg,#fff5f5,#fff0f2); border:1px solid #efd4dc; font-weight:600; }
    .end-script { font:600 1.7rem 'Caveat',cursive; color:#a6536b; margin-top:1.2rem; }
    .call-invite { margin:1rem 0 .35rem; text-align:center; color:#996879; font:600 1.5rem 'Caveat',cursive; }
    .call-helper { color:#987780; font-size:.85rem; line-height:1.75; text-align:center; margin:.15rem auto .75rem; }
    [data-testid="stTextInput"] label { color:#76545f !important; font-weight:600 !important; }
    [data-testid="stTextInput"] input { border:1px solid #e9cbd2 !important; border-radius:15px !important; background:#fffdfd !important; min-height:3rem; }
    .progress-label { text-align:center; color:#b1848e; font-size:.69rem; letter-spacing:.12em; text-transform:uppercase; margin:.2rem 0 .4rem; }
    .tiny-footer { text-align:center; color:#b08c94; font-size:.8rem; line-height:1.7; padding:1.2rem .5rem .1rem; }
    div.stButton > button, div.stLinkButton > a, div.stFormSubmitButton > button {
      width:100%; min-height:3.15rem; border:0; border-radius:999px;
      background:linear-gradient(100deg,#ad536b,#cd7b8b); color:white !important;
      font-weight:700; box-shadow:0 9px 22px rgba(164,78,101,.2);
      transition:transform .2s ease,box-shadow .2s ease;
    }
    div.stButton > button:hover, div.stLinkButton > a:hover, div.stFormSubmitButton > button:hover { color:white !important; border:0; transform:translateY(-2px); box-shadow:0 13px 27px rgba(164,78,101,.25); }
    div.stButton > button:focus, div.stFormSubmitButton > button:focus { color:white; border:0; }
    [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#b95f76,#df9ca5); }
    [data-testid="stHeader"] button { color:#895565 !important; }
    [data-testid="stTimeInput"] { background:transparent; }
    footer { visibility:hidden; }
    @keyframes soft-arrive { from {opacity:0;transform:translateY(17px)} to {opacity:1;transform:translateY(0)} }
    @keyframes twinkle { 0%,100%{opacity:.22;transform:scale(.8) rotate(0)}50%{opacity:.8;transform:scale(1.15) rotate(18deg)} }
    @keyframes gentle-float { 0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)} }
    @keyframes flap-soft { 0%,100%{transform:rotateX(0)}50%{transform:rotateX(7deg)} }
    @keyframes peek-soft { 0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)} }
    @keyframes heart-beat { 0%,100%{transform:scale(1)}50%{transform:scale(1.09)} }
    @media(max-width:640px) {
      .block-container { padding:.55rem .62rem 1.8rem; }
      .cover { border-radius:24px; padding:1.55rem .78rem 1.35rem; }
      .cover-title { font-size:clamp(2.35rem,10.7vw,3.25rem); }
      .cover-sub { font-size:.91rem; line-height:1.8; }
      .gif-stage { gap:.42rem; margin:1.1rem auto .55rem; }
      .gif-card { border-radius:17px; padding:.2rem; }
      .gif-card img { max-height:145px; }
      .envelope-stage { width:min(220px,73%); height:138px; margin:.7rem auto .2rem; }
      .envelope { height:118px; }
      .story-card { border-radius:21px; padding:1.2rem .98rem; }
      .story-copy { font-size:.95rem; line-height:1.88; }
      .photo-shell { padding:.46rem; border-radius:21px; }
      .photo-frame { max-height:66svh; border-radius:16px; }
      .photo-frame img { max-height:66svh; }
      .photo-copy { padding:.95rem .5rem .55rem; }
      .call-card { border-radius:23px; padding:1.35rem .92rem; }
      .time-wrap { padding:.8rem .8rem .65rem; }
      div.stButton > button,div.stLinkButton > a,div.stFormSubmitButton > button { min-height:3.05rem; font-size:.92rem; }
    }
    @media(prefers-reduced-motion:reduce) { *,*:before,*:after { animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Helpers --------------------
@st.cache_data(show_spinner=False)
def image_as_data_uri(image_path: str, modified_time: float) -> str:
    """Auto-orient and compress user photos for quicker, responsive phone display."""
    del modified_time
    with Image.open(image_path) as opened:
        image = ImageOps.exif_transpose(opened)
        if image.mode in ("RGBA", "LA"):
            rgba = image.convert("RGBA")
            bg = Image.new("RGBA", rgba.size, "white")
            bg.alpha_composite(rgba)
            image = bg.convert("RGB")
        else:
            image = image.convert("RGB")
        image.thumbnail((1500, 1900), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        image.save(out, format="JPEG", quality=82, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode("ascii")


@st.cache_data(show_spinner=False)
def local_gif_data_uri(path: str, modified_time: float) -> str:
    del modified_time
    raw = Path(path).read_bytes()
    return "data:image/gif;base64," + base64.b64encode(raw).decode("ascii")


def load_json(path: Path, fallback: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return fallback


def load_photo_captions() -> dict[str, Any]:
    """Load photo captions and show a useful warning instead of failing silently."""
    if not CAPTIONS_FILE.exists():
        st.warning("photo_captions.json was not found. Add it beside app.py to show your personal captions.")
        return {}
    try:
        with CAPTIONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        st.warning(f"photo_captions.json is not valid JSON (line {exc.lineno}, column {exc.colno}). Please check commas and quotation marks.")
        return {}
    except OSError as exc:
        st.warning(f"I could not read photo_captions.json: {exc}")
        return {}
    if not isinstance(data, dict):
        st.warning("photo_captions.json must contain an object keyed by photo filename, such as photo1.jpg.")
        return {}
    return data


def text_value(value: Any, fallback: str) -> str:
    value = str(value).strip() if value is not None else ""
    return value or fallback


def show_page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-top"><div class="eyebrow">{html.escape(kicker)}</div>'
        f'<div class="page-title">{html.escape(title)}</div>'
        f'<p class="page-sub">{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def show_story(symbol: str, kicker: str, title: str, paragraphs: list[str]) -> None:
    body = "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)
    st.markdown(
        f'<section class="story-card"><div class="story-symbol">{html.escape(symbol)}</div>'
        f'<div class="story-kicker">{html.escape(kicker)}</div>'
        f'<div class="story-heading">{html.escape(title)}</div>'
        f'<div class="story-copy">{body}</div></section>',
        unsafe_allow_html=True,
    )


# -------------------- Story order --------------------
# Cover -> every memory photo -> why I wanted us to talk -> call-time request.
story_pages: list[dict[str, Any]] = [{
    "kind": "story",
    "kicker": "Looking back at us",
    "title": "Why I wanted us to talk",
    "subtitle": "These memories mean a lot to me, and I don't want misunderstandings to speak for us.",
    "symbol": "💗",
    "paragraphs": [
        "These memories mean so much to me because they remind me of everything we've shared and how special this relationship is to me. I don't want misunderstandings, assumptions or things left unsaid to speak for us. I don't want us to lose something meaningful because we couldn't communicate properly. I want us to understand each other, talk openly about what's been bothering us and give ourselves a fair chance to work through this together❤️",
    ],
}]

def natural_sort_key(path: Path) -> list[tuple[int, Any]]:
    # Type tags keep numeric and text chunks comparable (for example 2.jpg and IMG.jpg).
    return [(1, int(part)) if part.isdigit() else (0, part.casefold()) for part in re.split(r"(\d+)", path.name)]


photo_files = sorted(
    [p for p in ASSET_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS],
    key=natural_sort_key,
) if ASSET_DIR.exists() else []
photo_captions = load_photo_captions()
# Match JSON keys without being sensitive to filename case.
caption_lookup = {str(key).casefold(): value for key, value in photo_captions.items()}

pages: list[dict[str, Any]] = [{"kind": "cover"}]
if not photo_files:
    st.info("No memory photos found yet. Add your JPG, PNG, or WebP photos to the assets folder to create the memory pages.")

for index, photo in enumerate(photo_files, start=1):
    # Exact filename matching comes first. If the actual photo has another name,
    # fall back to the corresponding photo1/photo2/... entry in the JSON file.
    candidates = [
        photo.name.casefold(),
        photo.stem.casefold(),
        f"photo{index}{photo.suffix.lower()}".casefold(),
        f"photo{index}.jpg",
        f"photo{index}.jpeg",
        f"photo{index}.png",
        f"photo{index}.webp",
        f"photo{index}",
    ]
    config = next((caption_lookup[key] for key in candidates if key in caption_lookup), {})
    if not isinstance(config, dict):
        config = {"caption": str(config)}
    pages.append({
        "kind": "photo", "path": photo, "index": index, "total": len(photo_files),
        "title": text_value(config.get("title"), f"A memory I hold close · {index}"),
        "caption": text_value(config.get("caption"), "A little moment that still means a lot to me. ❤️"),
    })

# The reflection page comes after every individual photo page.
pages.extend(story_pages)

# Final page: she suggests a time freely; there are no preset time choices or meeting request.
pages.append({
    "kind": "call",
    "kicker": "One little request",
    "title": "Can we set aside time for a proper call?",
    "subtitle": "I'd like us to have enough time to listen to each other without rushing.",
})

if "page_index" not in st.session_state:
    st.session_state.page_index = 0
if st.session_state.page_index >= len(pages):
    st.session_state.page_index = 0
page_index = st.session_state.page_index
page = pages[page_index]

if page_index > 0:
    st.markdown(
        f'<div class="progress-label">A little note from me to you · {page_index} of {len(pages)-1}</div>',
        unsafe_allow_html=True,
    )
    st.progress(page_index / (len(pages) - 1))

# -------------------- Render current page --------------------
if page["kind"] == "cover":
    gif_left = ASSET_DIR / "boy_apology.gif"
    gif_right = ASSET_DIR / "bear_apology.gif"
    left_html = ""
    right_html = ""
    if gif_left.exists():
        left_uri = local_gif_data_uri(str(gif_left), gif_left.stat().st_mtime)
        left_html = f'<div class="gif-card"><img src="{left_uri}" alt="A little cartoon boyfriend offering flowers as an apology"></div>'
    if gif_right.exists():
        right_uri = local_gif_data_uri(str(gif_right), gif_right.stat().st_mtime)
        right_html = f'<div class="gif-card"><img src="{right_uri}" alt="A sweet teddy bear holding a heart"></div>'

    st.markdown(
        f'''<section class="cover">
          <div class="eyebrow">A little apology from your boy</div>
          <div class="cover-title">I'm sorry, baby <span style="white-space:nowrap">💗</span></div>
          <p class="cover-sub">I know my goodbye message must have hurt. I wish I had asked to talk instead. I made this little letter because you deserve to hear what's in my heart properly.</p>
          <div class="gif-stage">{left_html}{right_html}</div>
          <div class="envelope-stage">
            <div class="envelope"><div class="letter-peek"></div><div class="flap"></div><div class="seal">♥</div></div>
          </div>
          <div class="script">A little note, from my heart to yours</div>
          <div class="cover-note">Read it at your own pace, baby. I'm not asking you to forget how you felt. I just hope you'll let me explain and hear you too. 🫂</div>
        </section>''',
        unsafe_allow_html=True,
    )

elif page["kind"] == "story":
    show_page_header(page["kicker"], page["title"], page["subtitle"])
    show_story(page.get("symbol", "♡"), page["kicker"], page["title"], page["paragraphs"])

elif page["kind"] == "photo":
    show_page_header("Little pieces of us", page["title"], "I wanted to give each memory its own little page, so you can pause and take it in.")
    st.markdown(f'<div class="photo-count">A little memory · {page["index"]} of {page["total"]}</div>', unsafe_allow_html=True)
    photo = page["path"]
    try:
        data_uri = image_as_data_uri(str(photo), photo.stat().st_mtime)
        st.markdown(
            f'''<section class="photo-shell"><div class="photo-frame"><img src="{data_uri}" alt="{html.escape(page['title'])}"></div>
            <div class="photo-copy"><h2 class="photo-title">{html.escape(page['title'])}</h2>
            <p class="photo-caption">{html.escape(page['caption'])}</p></div></section>''',
            unsafe_allow_html=True,
        )
    except (OSError, ValueError) as exc:
        st.warning(f"I couldn't display {photo.name}: {exc}")

elif page["kind"] == "call":
    show_page_header(page["kicker"], page["title"], page["subtitle"])
    st.markdown(
        """
        <section class="call-card">
          <div class="call-heart">💗</div>
          <div class="call-title">A little time for us?</div>
          <div class="call-copy">
            <p>Around that time, my health wasn't good, and I was feeling physically and emotionally overwhelmed. It affected how clearly I was thinking and how I handled my feelings. I was already carrying worry from the things I'd tried to explain, and when more misunderstandings happened, I reacted from that hurt instead of pausing.</p>
            <p>I don't want our relationship to end because of miscommunication or misunderstandings. What we've shared means too much to me for assumptions and things left unsaid to decide everything.</p>
            <p>I'd really like us to have a proper, unhurried call — enough time for both of us to explain how we've been feeling, listen to each other, and clear up what got misunderstood.</p>
            <p>I know I'm asking for a long call, and I realise that's a lot of your time. It may be a selfish thing to ask, but I don't want us to squeeze an important conversation into a few rushed minutes. I'd be grateful if we could block out some uninterrupted time whenever you're comfortable.</p>
            <p>Could you suggest a time that works for you? You can choose whatever feels right; there are no preset options and no pressure to decide immediately. I just want us to have the space to talk properly. 🫂</p>
          </div>
          <div class="end-script">I care about us, baby. ❤️</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="call-invite">Tell me a time that feels comfortable for you</div>', unsafe_allow_html=True)
    st.markdown('<div class="call-helper">You can suggest a day, a time, or a time window — whatever suits you best.</div>', unsafe_allow_html=True)
    suggested_time = st.text_input(
        "Your suggested time",
        placeholder="e.g. Tonight after 8, tomorrow evening, or Sunday afternoon",
        label_visibility="collapsed",
        key="suggested_call_time",
    )
    contact_config = load_json(CONTACT_CONFIG_FILE, {})
    if not isinstance(contact_config, dict):
        contact_config = {}
    whatsapp_number = re.sub(r"\D", "", str(contact_config.get("whatsapp_number", "")))
    if suggested_time.strip():
        whatsapp_message = (
            "Hey ❤️ A time that would work comfortably for me for our proper call is: "
            + suggested_time.strip()
            + ". Could we block out some uninterrupted time then? I'd like us to talk calmly and clear up the misunderstandings. 🫂"
        )
        st.markdown('<div class="picked-time">Your suggested time: ' + html.escape(suggested_time.strip()) + '</div>', unsafe_allow_html=True)
        if whatsapp_number:
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={quote(whatsapp_message)}"
            st.link_button("Send my suggested time on WhatsApp 💌", whatsapp_url, use_container_width=True)
        else:
            st.info("To activate the WhatsApp button, add your number to contact_config.json before deploying. The timing field will work once your number is configured.")
    else:
        st.caption("Your timing stays empty until you choose what works for you. ❤️")

# -------------------- Navigation --------------------
st.write("")
if page_index == 0:
    if st.button("Open my letter, baby 💌", use_container_width=True, key="open_letter"):
        st.session_state.page_index = 1
        st.rerun()
elif page_index < len(pages) - 1:
    left, right = st.columns(2)
    with left:
        if st.button("← Go back", use_container_width=True, key=f"previous_{page_index}"):
            st.session_state.page_index -= 1
            st.rerun()
    with right:
        if page["kind"] == "photo":
            next_label = "Next memory →" if page["index"] < page["total"] else "One last thing, baby →"
        elif page["kind"] == "story":
            next_label = "One last thing, baby →"
        else:
            next_label = "Continue, baby →"
        if st.button(next_label, use_container_width=True, key=f"next_{page_index}"):
            st.session_state.page_index += 1
            st.rerun()
else:
    left, right = st.columns(2)
    with left:
        if st.button("← Read the previous page", use_container_width=True, key="previous_last"):
            st.session_state.page_index -= 1
            st.rerun()
    with right:
        if st.button("Read my letter again ↺", use_container_width=True, key="restart_letter"):
            st.session_state.page_index = 0
            st.rerun()
