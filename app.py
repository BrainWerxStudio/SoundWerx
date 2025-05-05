import streamlit as st
import os
from pathlib import Path
import json

st.set_page_config(page_title="MP4 Seller Prototype", layout="centered")
st.title("🎬 Upload and Sell Your MP4 Video")

STORAGE_DIR = Path("temp")
METADATA_FILE = STORAGE_DIR / "metadata.json"
STORAGE_DIR.mkdir(exist_ok=True)

# Load metadata
if METADATA_FILE.exists():
    with open(METADATA_FILE, "r") as f:
        video_metadata = json.load(f)
else:
    video_metadata = []

# Initialize session state
if 'paid' not in st.session_state or not isinstance(st.session_state.paid, dict):
    st.session_state.paid = {}

# Upload new video form
st.subheader("Upload New Video")
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload MP4", type=["mp4"])
    title = st.text_input("Video Title")
    description = st.text_area("Description")
    price = st.text_input("Price")
    currency = st.selectbox("Currency", ["USD", "SOL"])
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
            "path": str(file_path)
        }
        video_metadata.append(entry)
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

    if not st.session_state.paid.get(selected_video["id"], False):
        st.info(f"💰 Price: {selected_video['price']} {selected_video['currency']}")
        if st.button("Simulate Payment"):
            st.session_state.paid[selected_video["id"]] = True
            st.success("🎉 Payment received! Enjoy your video.")
    else:
        st.video(selected_video["path"])
        with open(selected_video["path"], "rb") as vid_file:
            st.download_button(
                label="⬇️ Download Video",
                data=vid_file,
                file_name=os.path.basename(selected_video["path"]),
                mime="video/mp4"
            )
else:
    st.info("No songs uploaded yet.")
