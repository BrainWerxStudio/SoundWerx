import streamlit as st
import os
from pathlib import Path
import json
from moviepy.video.io.VideoFileClip import VideoFileClip

st.set_page_config(page_title="MP4 Seller Prototype", layout="centered")
st.title("🎬 Upload and Sell Your MP4 Video")

STORAGE_DIR = Path("temp")
PREVIEW_DIR = STORAGE_DIR / "previews"
METADATA_FILE = STORAGE_DIR / "metadata.json"

STORAGE_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)
PREVIEW_DURATION = 10  # seconds

# Load metadata
if METADATA_FILE.exists():
    with open(METADATA_FILE, "r") as f:
        video_metadata = json.load(f)
else:
    video_metadata = []

# Initialize session state
if 'paid' not in st.session_state or not isinstance(st.session_state.paid, dict):
    st.session_state.paid = {}

if 'analytics' not in st.session_state:
    st.session_state.analytics = {}

# Upload form
st.subheader("Upload New Video")
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload MP4", type=["mp4"])
    title = st.text_input("Video Title")
    description = st.text_area("Description")
    price = st.text_input("Price")
    currency = st.selectbox("Currency", ["USD", "SOL"])
    cover_art = st.file_uploader("Upload Cover Art (optional)", type=["jpg", "png"])
    submitted = st.form_submit_button("Upload and List")

if submitted:
    if uploaded_file and title and price:
        file_path = STORAGE_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create 10-second preview
        preview_file = PREVIEW_DIR / f"preview_{uploaded_file.name}"
        with VideoFileClip(str(file_path)) as clip:
            preview_clip = clip.subclip(0, min(PREVIEW_DURATION, clip.duration))
            preview_clip.write_videofile(str(preview_file), codec="libx264", audio_codec="aac", logger=None)

        entry = {
            "id": uploaded_file.name,
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "path": str(file_path),
            "preview": str(preview_file),
            "cover_art": cover_art.name if cover_art else None
        }
        video_metadata.append(entry)
        st.session_state.analytics[uploaded_file.name] = {"previewed": 0, "downloaded": 0}

        # Save metadata
        with open(METADATA_FILE, "w") as f:
            json.dump(video_metadata, f)

        if cover_art:
            with open(STORAGE_DIR / cover_art.name, "wb") as f:
                f.write(cover_art.getbuffer())

        st.success("✅ Video uploaded and listed successfully!")
    else:
        st.error("❌ Please complete all fields and upload a video.")

# Browse existing songs
st.subheader("Available Songs")
if video_metadata:
    selected_title = st.selectbox("Choose a song to preview and buy", [v["title"] for v in video_metadata])
    selected_video = next(v for v in video_metadata if v["title"] == selected_title)

    st.markdown("---")
    st.subheader(selected_video["title"])
    st.write(selected_video["description"])

    if selected_video.get("cover_art"):
        st.image(STORAGE_DIR / selected_video["cover_art"], caption="Cover Art")

    # Preview button
       # Preview button
    if st.button("▶ Preview 10s"):
        if "preview" in selected_video and os.path.exists(selected_video["preview"]):
            st.video(selected_video["preview"])
            st.session_state.analytics.setdefault(selected_video["id"], {"previewed": 0, "downloaded": 0})
            st.session_state.analytics[selected_video["id"]]["previewed"] += 1
        else:
            st.warning("⚠️ Preview not available for this video.")


    # Payment & full access
    if not st.session_state.paid.get(selected_video["id"], False):
        st.info(f"💰 Price: {selected_video['price']} {selected_video['currency']}")
        if st.button("💳 Simulate Payment"):
            st.session_state.paid[selected_video["id"]] = True
            st.success("🎉 Payment received! Enjoy your full video.")
    else:
        st.video(selected_video["path"])  # Full video access after payment

    # Analytics
    analytics = st.session_state.analytics.get(selected_video["id"], {"previewed": 0, "downloaded": 0})
    st.write(f"👁️ Previewed {analytics['previewed']} times.")
else:
    st.info("No songs uploaded yet.")
