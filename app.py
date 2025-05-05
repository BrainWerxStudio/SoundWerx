import streamlit as st
import os
from pathlib import Path
import json

st.set_page_config(page_title="MP4 Seller Prototype", layout="centered")
st.title("🎬 Upload and Sell Your MP4 Video")

STORAGE_DIR = Path("temp")
METADATA_FILE = STORAGE_DIR / "metadata.json"
STORAGE_DIR.mkdir(exist_ok=True)
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

# Ensure analytics is initialized for each video in session state
if 'analytics' not in st.session_state:
    st.session_state.analytics = {v['id']: {'previewed': 0, 'downloaded': 0} for v in video_metadata}

# Upload new video form
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

        entry = {
            "id": uploaded_file.name,
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "path": str(file_path),
            "cover_art": cover_art.name if cover_art else None,
            "previewed": 0,
            "downloaded": 0
        }
        video_metadata.append(entry)

        # Ensure analytics is initialized for the new video
        st.session_state.analytics[uploaded_file.name] = {'previewed': 0, 'downloaded': 0}

        with open(METADATA_FILE, "w") as f:
            json.dump(video_metadata, f)

        st.success("✅ Video uploaded and listed successfully!")
    else:
        st.error("❌ Please complete all fields and upload a video.")

# Browse listed videos
st.subheader("Available Songs")
if video_metadata:
    selected_title = st.selectbox("Choose a song to preview and buy", [v["title"] for v in video_metadata])
    selected_video = next(v for v in video_metadata if v["title"] == selected_title)

    st.markdown("---")
    st.subheader(selected_video["title"])
    st.write(selected_video["description"])

    # Check if cover art exists before trying to display it
    if selected_video.get("cover_art"):
        st.image(STORAGE_DIR / selected_video["cover_art"], caption="Cover Art")

    # Show preview
    if st.button("Preview 10s"):
        preview_video_path = selected_video["path"]
        st.video(preview_video_path, start_time=0)
        
        # Debugging: Check if the video ID exists in analytics
        if selected_video["id"] in st.session_state.analytics:
            st.session_state.analytics[selected_video["id"]]["previewed"] += 1
        else:
            st.warning(f"Warning: {selected_video['id']} not found in analytics!")

    # Display pricing info and simulate payment
    if not st.session_state.paid.get(selected_video["id"], False):
        st.info(f"💰 Price: {selected_video['price']} {selected_video['currency']}")
        if st.button("Simulate Payment"):
            st.session_state.paid[selected_video["id"]] = True
            st.success("🎉 Payment received! Enjoy your video.")
    else:
        st.video(selected_video["path"])

    # Show analytics
    if selected_video["id"] in st.session_state.analytics:
        preview_count = st.session_state.analytics[selected_video["id"]]["previewed"]
        download_count = st.session_state.analytics[selected_video["id"]]["downloaded"]
        st.write(f"Previewed {preview_count} times, Downloaded {download_count} times.")
    else:
        st.warning(f"Warning: Analytics for {selected_video['id']} not found!")
else:
    st.info("No songs uploaded yet.")
