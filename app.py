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

# Initialize the client with the user's key
client = genai.Client(api_key=api_key_input)

# 3. The UI Layout
st.title("🎨 The Magic Image Studio")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Control Panel")
    
    # Engine & Ratios - Updated with the correct API model names!
    model_choice = st.selectbox(
        "Choose your engine:", 
        [
            "gemini-2.5-flash-image", # The native Gemini generator
            "imagen-3.0-generate-002" # The standard Imagen 3 model
        ]
    )
    aspect_ratio = st.selectbox("Aspect Ratio:", ["1:1", "16:9", "9:16", "4:3", "3:4"])
    seed = st.number_input("Seed (0 for random):", value=0, help="Use the same seed to reproduce an exact image.")
    
    st.divider()
    
    st.markdown("### Reference Images")
    st.caption("Advanced features for future expansion!")
    style_ref = st.file_uploader("Upload Style Reference", type=["png", "jpg", "jpeg"])

with col2:
    st.subheader("The Canvas")
    prompt = st.text_area("What do you want to see?", placeholder="A cyberpunk cat drinking a neon espresso...")
    neg_prompt = st.text_input("Negative Prompt (what to avoid):", placeholder="blurry, ugly, low resolution")
    
    if st.button("Generate Masterpiece", type="primary"):
        if not prompt:
            st.warning("You gotta give me a prompt first, Picasso!")
        else:
            with st.spinner("Mixing the digital paints..."):
                try:
                    # Route A: Using the native Gemini models (Nano Banana series)
                    if "gemini" in model_choice:
                        response = client.models.generate_content(
                            model=model_choice,
                            contents=[prompt],
                        )
                        # Extract the image from the response parts
                        for part in response.candidates[0].content.parts:
                            if part.inline_data is not None:
                                image = Image.open(io.BytesIO(part.inline_data.data))
                                st.image(image, caption=prompt, use_container_width=True)
                                st.balloons()
                                
                    # Route B: Using the Imagen models
                    else:
                        config = types.GenerateImagesConfig(
                            number_of_images=1,
                            aspect_ratio=aspect_ratio,
                            negative_prompt=neg_prompt if neg_prompt else None,
                        )
                        result = client.models.generate_images(
                            model=model_choice,
                            prompt=prompt,
                            config=config
                        )
                        # Display the image
                        for generated_image in result.generated_images:
                            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                            st.image(image, caption=prompt, use_container_width=True)
                            st.balloons()
                            
                except Exception as e:
                    st.error(f"Oops, we hit a snag: {e}")
