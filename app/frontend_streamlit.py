import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="BPA Breed ID (Prototype)", layout="centered")
st.title("BPA Breed Identification - FLW Assistant")
st.caption("Upload or capture an image to get breed suggestions.")

# -------------------------
# Sidebar settings
# -------------------------
api_url = st.sidebar.text_input("API URL", value="https://animalbreeddetectorbackend-2.onrender.com")
threshold = st.sidebar.slider("Suggestion threshold", 0.0, 1.0, 0.6, 0.05)
topk = st.sidebar.selectbox("Top-K", [1, 2, 3, 4, 5], index=2)

# -------------------------
# Tabs
# -------------------------
tab1, tab2 = st.tabs(["Predict", "Breeds"])

# -------------------------
# Predict tab
# -------------------------
with tab1:
    img_file = st.file_uploader("Upload image", type=["jpg","jpeg","png"])
    cam = st.camera_input("Or capture from camera", disabled=False)

    file_bytes = None
    if cam is not None:
        file_bytes = cam.getvalue()
    elif img_file is not None:
        file_bytes = img_file.read()

    if file_bytes:
        col1, col2 = st.columns(2)
        with col1:
            st.image(file_bytes, caption="Input", width="stretch")


        with col2:
            try:
                files = {"file": ("image.jpg", file_bytes, "image/jpeg")}
                data = {"threshold": str(threshold), "topk": str(topk)}
                r = requests.post(f"{api_url}/predict", files=files, data=data, timeout=30)
                if r.ok:
                    resp = r.json()

                    # --- Styled predicted breed display ---
                    predicted = resp.get("predicted_class")
                    if predicted:
                        st.markdown(
                            f"""
                            <div style="
                                padding: 15px;
                                border-radius: 10px;
                                background-color: #d4edda;
                                color: #155724;
                                font-weight: bold;
                                font-size: 20px;
                                text-align: center;
                                border: 1px solid #c3e6cb;
                            ">
                            Predicted Breed: {predicted}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("No confident prediction returned by API.")

                    # Optional suggestion message
                    if resp.get("suggestion"):
                        st.success(f"Suggested breed: **{resp['suggestion']}** (≥ threshold)")
                        if st.button("Copy suggestion for BPA"):
                            st.session_state["selected_breed"] = resp["suggestion"]
                else:
                    st.error(f"API error: {r.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# -------------------------
# Breeds tab
# -------------------------
with tab2:
    try:
        r = requests.get(f"{api_url}/breeds", timeout=10)
        if r.ok:
            breeds = r.json()
            if breeds:
                st.markdown("### Available Breeds")
                # Display breeds nicely instead of raw JSON
                for idx, breed in breeds.items():
                    st.markdown(f"- **{breed}**")
            else:
                st.warning("No breeds found in API.")
        else:
            st.error("Failed to fetch breeds list.")
    except Exception as e:
        st.error(f"Failed: {e}")

st.info("Tip: Good photos help—front/side profile, head horns, body color patterns, tail switch, udder view when possible.")
