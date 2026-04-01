import streamlit as st
import requests
import json

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Breed AI", layout="centered")

st.title("🐄 AI Breed Identification")
st.caption("Upload or capture an image to identify cattle breed")

# -------------------------
# Load breed database (🔥 FIX)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "breed_db.json")

with open(file_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)
# Convert list → dictionary
BREED_DB = {b["name"]: b for b in raw_data["breeds"]}

# -------------------------
# Sidebar
# -------------------------
api_url = st.sidebar.text_input(
    "API URL",
    value="https://animalbreeddetectorbackend-2.onrender.com"
)
topk = st.sidebar.slider("Top Predictions", 1, 5, 3)

# -------------------------
# Upload section
# -------------------------
img_file = st.file_uploader("📤 Upload Image", type=["jpg","jpeg","png"])
cam = st.camera_input("📷 Capture Image")

file_bytes = None
if cam:
    file_bytes = cam.getvalue()
elif img_file:
    file_bytes = img_file.read()

# -------------------------
# Prediction
# -------------------------
if file_bytes:
    col1, col2 = st.columns(2)

    with col1:
        st.image(file_bytes, caption="Input Image", use_container_width=True)

    with col2:
        with st.spinner("🔍 Analyzing..."):
            try:
                files = {"file": ("image.jpg", file_bytes, "image/jpeg")}
                r = requests.post(f"{api_url}/predict", files=files, timeout=60)

                if r.ok:
                    resp = r.json()
                    preds = resp.get("top_predictions", [])

                    if preds:
                        best = preds[0]
                        breed_name = best["breed"]
                        confidence = best["confidence"]

                        # 🏆 Prediction Card
                        st.markdown(
                            f"""
                            <div style="
                                padding: 15px;
                                border-radius: 12px;
                                background-color: #d4edda;
                                color: #155724;
                                font-size: 22px;
                                font-weight: bold;
                                text-align: center;
                            ">
                            🏆 {breed_name} ({confidence*100:.1f}%)
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # 📋 Breed Details
                        info = BREED_DB.get(breed_name)

                        if info:
                            st.markdown("### 📋 Breed Details")

                            st.markdown(f"**🐄 Name:** {info.get('name')}")
                            st.markdown(f"**🧬 Species:** {info.get('species')}")
                            st.markdown(f"**🧬 Local Name:** {info.get('local_name')}")
                            st.markdown(f"**🌍 Region:** {info.get('region')}")
                            st.markdown(f"**🌡 Climate:** {info.get('climate')}")
                            st.markdown(f"**🥛 Milk Yield:** {info.get('milk_yield')}")

                            # Aliases
                            aliases = ", ".join(info.get("aliases", []))
                            st.markdown(f"**🔁 Aliases:** {aliases}")

                            st.markdown("**🔍 Identification:**")
                            st.info(info.get("identification"))

                            st.markdown("**💡 Farmer Tip:**")
                            st.success(info.get("farmer_tip"))

                        else:
                            st.warning("Breed info not available")

                        # 📊 Top Predictions
                        st.markdown("### 📊 Other Possible Breeds")
                        for i, p in enumerate(preds[:topk]):
                            st.write(f"{i+1}. **{p['breed']}** → {p['confidence']*100:.1f}%")

                    else:
                        st.warning("No prediction returned")

                else:
                    st.error(f"API Error: {r.text}")

            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.info("💡 Tip: Use clear side-view images for best results")
