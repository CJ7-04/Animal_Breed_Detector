import streamlit as st
import requests

st.set_page_config(
    page_title="Animal Breed Identifier",
    layout="centered"
)

# -------------------------
# HEADER
# -------------------------
st.title("🐄 Animal Breed Identifier")
st.caption("AI tool for farmers & field workers")

# -------------------------
# SIDEBAR SETTINGS
# -------------------------
st.sidebar.header("⚙ Settings")

api_url = st.sidebar.text_input(
    "Backend API URL",
    value="https://animalbreeddetectorbackend-2.onrender.com"
)

threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.6, 0.05)
topk = st.sidebar.selectbox("Top Predictions", [1, 2, 3, 4, 5], index=2)

language = st.sidebar.radio(
    "Language",
    ["English", "हिन्दी"]
)

lang_code = "hi" if language == "हिन्दी" else "en"

st.sidebar.markdown("---")
st.sidebar.info("Higher threshold = more accurate suggestion")

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["🔍 Identify Breed", "📚 Breed List"])

# -------------------------
# PREDICT TAB
# -------------------------
with tab1:

    st.subheader("Upload or Capture Image")

    img_file = st.file_uploader("Upload image", type=["jpg","jpeg","png"])
    cam = st.camera_input("Capture from camera")

    file_bytes = None

    if cam is not None:
        file_bytes = cam.getvalue()
    elif img_file is not None:
        file_bytes = img_file.read()

    if file_bytes:

        st.image(file_bytes, caption="Selected Image", use_container_width=True)

        if st.button("🔎 Identify Breed"):

            with st.spinner("Analyzing image..."):

                try:
                    files = {"file": ("image.jpg", file_bytes, "image/jpeg")}
                    data = {
                        "threshold": str(threshold),
                        "topk": str(topk),
                        "lang": lang_code
                    }

                    r = requests.post(f"{api_url}/predict", files=files, data=data, timeout=60)

                    if r.ok:
                        resp = r.json()

                        suggestion = resp.get("suggestion")
                        top_predictions = resp.get("topk", [])
                        breed_info = resp.get("breed_info")
                        confidence_msg = resp.get("confidence_message")

                        # -------------------------
                        # RESULT DISPLAY
                        # -------------------------
                        if suggestion:
                            st.success(f"✅ Suggested Breed: **{suggestion}**")
                        else:
                            st.warning("No confident suggestion")

                        # 🌾 Confidence guidance
                        if confidence_msg:
                            st.info(confidence_msg)

                        # -------------------------
                        # CONFIDENCE LIST
                        # -------------------------
                        if top_predictions:
                            st.markdown("### 📊 Prediction Confidence")
                            for p in top_predictions:
                                st.write(f"**{p['breed']}** — {p['confidence']}%")

                        # -------------------------
                        # BREED INFO CARD
                        # -------------------------
                        if breed_info:
                            st.markdown("### 🐄 Breed Information")

                            display_name = breed_info.get("display_name") or breed_info.get("name")

                            st.markdown(f"**Name:** {display_name}")
                            st.markdown(f"**Region:** {breed_info.get('region','')}")
                            st.markdown(f"**Milk Yield:** {breed_info.get('milk_yield','')}")
                            st.markdown(f"**Uses:** {breed_info.get('uses','')}")

                            if breed_info.get("farmer_tip"):
                                st.info(f"🌾 Farmer Tip: {breed_info['farmer_tip']}")

                    else:
                        st.error(f"API Error: {r.text}")

                except Exception as e:
                    st.error(f"Connection failed: {e}")

    st.markdown("---")
    st.info("📷 Tip: Take clear side & front photos for better accuracy.")

# -------------------------
# BREEDS TAB
# -------------------------
with tab2:

    st.subheader("Available Breeds")

    try:
        r = requests.get(f"{api_url}/breeds", timeout=15)

        if r.ok:
            breeds = r.json()

            for b in breeds.values():
                st.markdown(f"• {b}")

        else:
            st.error("Could not fetch breed list")

    except Exception as e:
        st.error(f"Failed: {e}")

