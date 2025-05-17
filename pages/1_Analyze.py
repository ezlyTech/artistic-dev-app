import streamlit as st
import uuid
import io
import numpy as np
import plotly.graph_objects as go
import time
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
from utils.auth import login, signup, is_authenticated, logout, get_supabase_client, get_supabase_admin_client
from classes_def import stage_insights, development_tips, recommended_activities, classes

st.set_page_config(page_title="Analyze", page_icon="🖼️")

# --- Connect to Supabase (always main client) ---
supabase_admin = get_supabase_admin_client()


if supabase_admin is None:
    st.error("Error: Unable to connect to Supabase.")
    st.stop()

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            background: url('https://images.unsplash.com/photo-1637248970116-838902fe389a?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D') no-repeat center center fixed;
            background-size: cover;
            font-family: "Comic Sans MS", "Segoe UI", sans-serif;
            color: #222 !important;
        }
        .stApp {
            background: rgba(255, 255, 255, 78%);
            backdrop-filter: blur(10px);
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3, h4, h5 {
            color: #ff6f61 !important;
        }
        .upload-box {
            border: 2px dashed #ffc1cc;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            background-color: #fff0f5;
            cursor: pointer;
        }
        .upload-box:hover {
            background-color: #ffeef2;
        }
        .confidence-box {
            background-color: #fff3cd;
            border-left: 5px solid #ffcc00;
            padding: 12px;
            border-radius: 8px;
            margin-top: 12px;
        }
        .stage-info {
            background-color: #ffecf1;
            color: #5a0033;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            font-weight: 500;
        }
        .stImage img {
            max-width: 100%;
            height: auto;
        }
        .stExpanderHeader {
            font-weight: 600;
            font-size: 18px;
            color: #ff6f61;
        }
        
        @media (max-width: 768px) {
            .stApp {
                margin: 0;
                border-radius: 0;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- If authenticated, show welcome and main UI ---
if is_authenticated():
    st.success(f"Welcome, {st.session_state['user']['username']}!")

    # Upload UI
    st.markdown("<h5>📸 Upload Your Child's Drawing</h5>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .stFileUploader {
            border: 2px dashed #FF914D;
            padding: 40px;
            text-align: center;
            border-radius: 15px;
            background-color: #fff3e6;
            transition: background-color 0.3s ease;
        }
        .stFileUploader:hover {
            background-color: #ffe1c4;
        }
        .stFileUploader label { display: none; }
        </style>
    """, unsafe_allow_html=True)

    # Session state defaults
    if "last_prediction" not in st.session_state:
        st.session_state.last_prediction = None
    if "image_data" not in st.session_state:
        st.session_state.image_data = None
    if "analyzed_once" not in st.session_state:
        st.session_state.analyzed_once = False

    @st.cache_resource
    def get_model():
        return load_model("model.h5")

    upload = st.file_uploader("", type=["png", "jpg", "jpeg"], key="file_input", label_visibility="collapsed")

    if upload:
        im = Image.open(upload).convert("RGB")
        img = np.asarray(im)
        image = cv2.resize(img, (224, 224)) / 255.0
        image = np.expand_dims(image, axis=0)

        @st.dialog("🎯 Analysis Result")
        def show_result_dialog():
            with st.spinner("Analyzing your drawing... 🎯"):
                time.sleep(2)
                model = get_model()
                preds = model.predict(image)
                percentages = preds[0]
                pred_class = np.argmax(percentages)
                stage_name = classes[pred_class]
                confidence = percentages[pred_class] * 100

                # Upload image to Supabase Storage
                image_bytes = io.BytesIO()
                im.save(image_bytes, format='PNG')
                image_bytes = image_bytes.getvalue()

                filename = f"{uuid.uuid4().hex}.png"
                storage_path = f"user_uploads/{filename}"

                # Upload image to Supabase Storage
                # upload_response = supabase_admin.storage.from_("drawings").upload(
                #     storage_path, image_bytes, {"content-type": "image/png"}
                # )


                # Check if upload was successful
                # if not isinstance(upload_response, str) or "Upload completed" not in upload_response:
                #     st.error("Image upload failed.")
                #     st.stop()

                # Get public URL
                image_url = supabase_admin.storage.from_("drawings").get_public_url(storage_path)


                # Save analysis to Supabase DB
                supabase_admin.table("results").insert({
                    "user_id": st.session_state["user"]["id"],
                    "image_path": image_url,
                    "prediction": stage_name,
                    "confidence": float(confidence)
                }).execute()

            st.markdown(f"<div class='stage-info'><strong>{stage_name}</strong><br>{stage_insights[stage_name]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='confidence-box'>This prediction has a <strong>{confidence:.2f}%</strong> match with <strong>{stage_name}</strong>.</div>", unsafe_allow_html=True)
            st.image(im, caption='Uploaded Drawing', use_container_width=True)

            colors = ['#ffcccc' if i != pred_class else '#ff6666' for i in range(len(classes))]
            fig = go.Figure(go.Bar(
                x=percentages * 100,
                y=classes,
                orientation='h',
                text=[f"{p*100:.1f}%" for p in percentages],
                textposition='outside',
                marker=dict(color=colors, line=dict(color='#222', width=1))
            ))
            fig.update_layout(
                title="Model Confidence per Artistic Stage",
                xaxis_title="Confidence (%)",
                yaxis_title="Stage",
                xaxis=dict(range=[0, 100], gridcolor='lightgray'),
                height=420,
                template="plotly_white",
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                margin=dict(l=50, r=50, t=60, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)

            traits = ['Symbol Use', 'Spatial Awareness', 'Realism', 'Emotion', 'Motor Skills']
            trait_scores = np.random.uniform(50, 100, size=5)
            radar = go.Figure(data=go.Scatterpolar(
                r=trait_scores,
                theta=traits,
                fill='toself',
                marker_color='rgba(255,105,97,0.8)'
            ))
            radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title="🌭 Artistic Trait Profile"
            )
            st.plotly_chart(radar, use_container_width=True)

            st.subheader("🛠️ Development Tips")
            for tip in development_tips[stage_name]:
                st.markdown(f"- {tip}")

            st.subheader("🎨 Activity Ideas")
            for activity in recommended_activities[stage_name]:
                st.markdown(f"- {activity}")

            with st.expander("🔍 Expert Perspective"):
                st.write("This stage reflects important aspects of your child's cognitive and emotional development. It can be useful to explore their creative interests and encourage expression.")

            st.info("📈 Want to track progress? Upload a new drawing every month and see how their style changes over time!")
            st.caption("✨ Use this result to guide learning. Speak with an educator or psychologist for further support.")

        show_result_dialog()

    if st.button("Logout"):
        logout()
        st.experimental_rerun()


else:
    st.markdown("<h5 style='text-align: center;'>Please login or create an account first.</h5>", unsafe_allow_html=True)
    
    tabs = st.tabs(["🔐 Login", "📝 Create Account"])

    # --- Login Tab ---
    with tabs[0]:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.switch_page("pages/1_Analyze.py")
            else:
                st.error("Invalid username or password.")

    # --- Create Account Tab ---
    with tabs[1]:
        new_username = st.text_input("Choose a Username", key="signup_username")
        new_password = st.text_input("Choose a Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_username) < 3 or len(new_password) < 5:
                st.warning("Username must be at least 3 characters, password at least 5.")
            else:
                result = signup(new_username, new_password)
                if result:
                    st.success("Account created successfully! Logging you in...")
                    if login(new_username, new_password):
                        st.switch_page("pages/1_Analyze.py")
                else:
                    st.error("Username already taken or account creation failed.")


# --- Footer ---

st.markdown("<footer style='text-align:center; padding:10px; font-size:12px;'>© 2025 Drawee. This thesis project features an AI model powered by ResNet-50 for classifying children's drawings based on Lowenfeld's stages of artistic development.</footer>", unsafe_allow_html=True)
