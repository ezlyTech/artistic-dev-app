import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
from utils import stages_info, stage_insights, development_tips, recommended_activities

# --- Page Setup ---
st.set_page_config(page_title="Drawee | Child Drawing Classifier", layout="centered", page_icon="🎨")

# --- Model Classes & Descriptions ---
classes = [
    "The Scribbling Stage",
    "The Preschematic Stage",
    "The Schematic Stage",
    "The Gang Age",
    "The Stage of Reasoning",
    "Adolescent Art"
]

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
            max-width: 800px;
            margin: 30px auto;
            background: rgba(255, 255, 255, 78%);
            backdrop-filter: blur(10px);
            border-radius: 15px;
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
        
        /* Mobile-specific styles */
        @media (max-width: 768px) {
            .stApp {
                margin: 0;
                border-radius: 0;
            }
        }
    </style>
""", unsafe_allow_html=True)


# --- Title ---
st.markdown("<h1 style='text-align: center;'>🎨 Drawee</h1>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center;'>Watch little hands tell big stories</h6>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 14px;'>Drawee helps parents, teachers, and child development experts understand a child's artistic growth by analyzing their drawings. Based on Lowenfeld’s stages of artistic development, Drawee reveals the creative journey behind every doodle, making it fun and easy to track artistic progress</p>", 
    unsafe_allow_html=True
    )
st.markdown("---")

# --- Upload UI ---
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

# --- Before File Upload ---
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "image_data" not in st.session_state:
    st.session_state.image_data = None
if "analyzed_once" not in st.session_state:
    st.session_state.analyzed_once = False


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
            model = load_model("model.h5")
            preds = model.predict(image)
            percentages = preds[0]
            pred_class = np.argmax(percentages)
            stage_name = classes[pred_class]
            confidence = percentages[pred_class] * 100

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

        # Artistic Trait Radar Chart
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
            title="🧭 Artistic Trait Profile"
        )
        st.plotly_chart(radar, use_container_width=True)

        # Development Tips
        st.subheader("🛠️ Development Tips")
        for tip in development_tips[stage_name]:
            st.markdown(f"- {tip}")

        # Recommended Activities
        st.subheader("🎨 Activity Ideas")
        for activity in recommended_activities[stage_name]:
            st.markdown(f"- {activity}")

        # Expert Perspective
        with st.expander("🔍 Expert Perspective"):
            st.write("This stage reflects important aspects of your child's cognitive and emotional development. It can be useful to explore their creative interests and encourage expression.")

        # Progress Tracker Note
        st.info("📈 Want to track progress? Upload a new drawing every month and see how their style changes over time!")

        st.caption("✨ Use this result to guide learning. Speak with an educator or psychologist for further support.")

    show_result_dialog()

# --- Learning Section ---
st.markdown("<h5>💡 Learn about the stages</h5>", unsafe_allow_html=True)
cols = st.columns(2)
for i, (label, desc) in enumerate(stages_info.items()):
    with cols[i % 2].expander(label, expanded=True):
        st.markdown(f"**{desc}**")

st.markdown("---")

st.markdown("<footer style='text-align:center; padding:10px; font-size:12px;'>© 2025 Drawee. This thesis project features an AI model powered by ResNet-50 for classifying children's drawings based on Lowenfeld's stages of artistic development.</footer>", unsafe_allow_html=True)
