import streamlit as st
from google import genai
from google.genai import types
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="My AI Art Studio", layout="wide", page_icon="🎨")

# 2. Sidebar for Authentication
st.sidebar.header("🔑 Authentication")
st.sidebar.markdown("Grab your API key from Google AI Studio and paste it below.")
api_key_input = st.sidebar.text_input("Gemini API Key:", type="password")

if not api_key_input:
    st.info("👈 Please enter your API key in the sidebar to unlock the studio!")
    st.stop()

# Initialize the client
client = genai.Client(api_key=api_key_input)

# 3. The UI Layout
st.title("🎨 The Magic Image Studio")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Control Panel")
    
    # Engine Selection - Exclusively using the Developer API native models!
    model_choice = st.selectbox(
        "Choose your engine:", 
        [
            "gemini-2.5-flash-image",
            "gemini-3-pro-image-preview"
        ]
    )
    
    # Aspect ratio is now handled correctly in the ImageConfig
    aspect_ratio = st.selectbox("Aspect Ratio:", ["1:1", "16:9", "9:16", "4:3", "3:4"])

with col2:
    st.subheader("The Canvas")
    prompt = st.text_area("What do you want to see?", placeholder="A cyberpunk cat drinking a neon espresso...")
    
    if st.button("Generate Masterpiece", type="primary"):
        if not prompt:
            st.warning("You gotta give me a prompt first, Picasso!")
        else:
            with st.spinner("Mixing the digital paints..."):
                try:
                    # CRITICAL FIX: We explicitly demand an IMAGE response type
                    config = types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                        )
                    )
                    
                    response = client.models.generate_content(
                        model=model_choice,
                        contents=prompt,
                        config=config
                    )
                    
                    # Safely extract the image from the response payload
                    image_found = False
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            image = Image.open(io.BytesIO(part.inline_data.data))
                            st.image(image, caption=prompt, use_container_width=True)
                            st.balloons()
                            image_found = True
                            
                    if not image_found:
                        st.error("No image returned. This usually means the prompt triggered a safety block.")
                        
                except Exception as e:
                    st.error(f"API Error: {e}")
