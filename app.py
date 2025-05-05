import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="MP4 Seller Prototype", layout="centered")
st.title("🎬 Upload and Sell Your MP4 Video")

# Initialize session state
defaults = {
    "paid": False,
    "video_path": None,
    "title": "",
    "description": "",
    "price": "",
    "currency": "USD"
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Step 1: Upload and set details
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload MP4", type=["mp4"])
    title = st.text_input("Video Title", st.session_state.title)
    description = st.text_area("Description", st.session_state.description)
    price = st.text_input("Price", st.session_state.price)
    currency = st.selectbox("Currency", ["USD", "SOL"], index=["USD", "SOL"].index(st.session_state.currency))
    submitted = st.form_submit_button("Create Product Page")

if submitted:
    if uploaded_file and title and price:
        save_path = Path("temp")
        save_path.mkdir(exist_ok=True)
        video_path = save_path / uploaded_file.name
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Update session state
        st.session_state.video_path = video_path
        st.session_state.title = title
        st.session_state.description = description
        st.session_state.price = price
        st.session_state.currency = currency
        st.session_state.paid = False  # reset payment status

        st.success("✅ Product created! Scroll down to view page.")
    else:
        st.error("❌ Please complete all fields and upload a video.")

# Step 2: Show product page
if st.session_state.video_path:
    st.markdown("---")
    st.subheader(st.session_state.title)
    st.write(st.session_state.description)

    if not st.session_state.paid:
        st.info(f"💰 Price: {st.session_state.price} {st.session_state.currency}")
        if st.button("Simulate Payment"):
            st.session_state.paid = True
            st.success("🎉 Payment received! Enjoy your video.")
    else:
        st.video(str(st.session_state.video_path))
        with open(st.session_state.video_path, "rb") as vid_file:
            st.download_button(
                label="⬇️ Download Video",
                data=vid_file,
                file_name=os.path.basename(st.session_state.video_path),
                mime="video/mp4"
            )
