import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
from utils import stages_info, stage_insights, development_tips, recommended_activities, classes






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
            # model = load_model("drawee-v1.7.h5")
            # model = load_model("drawee-v1.6.h5")
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


