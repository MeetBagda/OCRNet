import streamlit as st
import os
from PIL import Image
import tempfile
import sys
import requests
from io import BytesIO
import ollama
import time

# Import functions directly from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import extract_text_from_image, load_image, get_gdrive_direct_url

# Initialize session state for tracking extraction status
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Apply custom CSS for a modern, elegant UI with light blue and white
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body {
        font-family: 'Inter', sans-serif;
        background-color: #F0F8FF; /* AliceBlue */
    }

    .main {
        background-color: #F0F8FF;
    }

    .stApp {
        background-color: #F0F8FF;
    }

    /* Main container styling */
    .css-18e3th9 {
        padding: 2rem 3rem;
    }

    /* Custom card for content */
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }

    /* Button styling */
    .stButton > button {
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        color: white;
        background-color: #3B82F6; /* A nice blue */
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #2563EB;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    .stButton > button:disabled {
        background-color: #9CA3AF;
        color: #E5E7EB;
    }

    /* Download button styling */
    .stDownloadButton > button {
        border: 1px solid #3B82F6;
        background-color: #EFF6FF;
        color: #3B82F6;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton > button:hover {
        background-color: #DBEAFE;
        border-color: #2563EB;
    }

    /* Header styling - Make text visible */
    h1 {
        color: #1E3A8A !important; /* Darker blue for titles */
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
    }
    h3 {
        color: #1E40AF !important;
        font-weight: 600 !important;
    }

    /* Radio button styling - Make text visible */
    .stRadio > div {
        flex-direction: row;
        gap: 20px;
    }
    .stRadio > div > label {
        color: #1F2937 !important;
        font-weight: 500 !important;
        font-size: 16px !important;
    }
    .stRadio > div > label > div {
        color: #1F2937 !important;
    }

    /* Text styling for better visibility */
    p, span, div {
        color: #1F2937 !important;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        padding: 10px;
        color: #1F2937;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 8px;
    }

    /* Make sure all text is visible */
    .stMarkdown, .stText {
        color: #1F2937 !important;
    }

</style>
""", unsafe_allow_html=True)

# streamlit_app.py


# Set page configuration
st.set_page_config(
    page_title="OCR Text Extractor",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Create columns for logo and title
col1, col2 = st.columns([1, 5])

# Add a placeholder for logo (you can replace with your own logo)
with col1:
    st.image("https://img.icons8.com/fluency/96/000000/ocr.png", width=80)

# Page title and description with cleaner styling
with col2:
    st.markdown("<h1 style='color: #1E3A8A !important; font-weight: 700; margin-bottom: 10px;'>OCR Text Extractor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #374151 !important; font-weight: 500;'>A modern tool to extract text from images with precision and speed.</p>", unsafe_allow_html=True)

# Add a separator
st.markdown("<hr style='margin: 15px 0px; border: none; height: 2px; background-color: #D1D5DB;'>", unsafe_allow_html=True)

# Create a card-like container for the form
st.markdown("<div class='card'>", unsafe_allow_html=True)

# Input options - disabled during processing
input_method = st.radio("Select input method:", 
                      ["Upload Image", "Image URL/Google Drive Link"], 
                      disabled=st.session_state.processing)

image_path = None
uploaded_image = None

# Handle file upload
if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image file", 
                                    type=["jpg", "jpeg", "png", "bmp"],
                                    disabled=st.session_state.processing)
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            image_path = tmp_file.name
        
        # Create columns for image preview
        img_col1, img_col2 = st.columns([2, 1])
        
        # Display the uploaded image
        with img_col1:
            uploaded_image = Image.open(uploaded_file)
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
            
        # Show image info in the second column
        with img_col2:
            st.markdown("<h4 style='color: #4B5563; font-size: 16px;'>Image Information</h4>", unsafe_allow_html=True)
            if uploaded_image:
                st.markdown(f"""
                <ul style='font-size: 14px; color: #6B7280; list-style-type: none; padding-left: 0;'>
                    <li><strong>Size:</strong> {uploaded_image.size[0]} × {uploaded_image.size[1]} px</li>
                    <li><strong>Format:</strong> {uploaded_image.format if uploaded_image.format else "Unknown"}</li>
                    <li><strong>Mode:</strong> {uploaded_image.mode}</li>
                </ul>
                """, unsafe_allow_html=True)

# Handle URL input
else:
    url = st.text_input("Enter image URL or Google Drive share link", 
                       disabled=st.session_state.processing,
                       placeholder="https://example.com/image.jpg or Google Drive share link")
    if url:
        image_path = url
        st.markdown(f"""
        <div style='background-color: #EFF6FF; padding: 10px; border-radius: 6px; border-left: 4px solid #3B82F6;'>
            <p style='margin: 0; color: #1E40AF;'><strong>Image URL:</strong> {url}</p>
        </div>
        """, unsafe_allow_html=True)

# Close the card container
st.markdown("</div>", unsafe_allow_html=True)

# Add some space
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Process button - styled
extract_button_col1, extract_button_col2, extract_button_col3 = st.columns([1, 2, 1])
with extract_button_col2:
    extract_button = st.button("🔍 Extract Text", 
                              disabled=not image_path or st.session_state.processing,
                              use_container_width=True)

# Create placeholders for results
result_container = st.container()
with result_container:
    result_header = st.empty()
    result_text = st.empty()
    download_button = st.empty()
    error_message = st.empty()

if image_path and extract_button:
    try:
        # Set processing state to true to disable UI
        st.session_state.processing = True
        
        # Rerun to apply disabled state to UI elements
        st.experimental_rerun()
        
    except Exception as e:
        # This won't execute due to the rerun above, but kept for clarity
        pass

# Handle processing in a separate block to avoid duplicate processing
if st.session_state.processing and image_path:
    try:
        with st.spinner("Extracting text from image..."):
            result = extract_text_from_image(image_path)
            
        # Display results in a styled card
        result_header.markdown("<div class='card'>", unsafe_allow_html=True)
        result_header.markdown("<h3 style='color: #166534; margin-bottom: 15px;'>Extracted Text</h3>", unsafe_allow_html=True)
        
        # Display text in a formatted area
        result_text.markdown(f"""
        <div style='background-color: #F9FAFB; border-radius: 8px; padding: 15px; border: 1px solid #E5E7EB; margin-bottom: 15px; max-height: 300px; overflow-y: auto;'>
            <pre style='white-space: pre-wrap; word-break: break-word; color: #1F2937; font-family: monospace; margin: 0;'>{result}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a row for buttons
        download_col1, download_col2 = download_button.columns([1, 1])
        
        # Allow downloading the result as a text file
        with download_col1:
            st.download_button(
                label="💾 Download as Text File",
                data=result,
                file_name="extracted_text.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        # Add a copy button
        with download_col2:
            st.markdown("""
            <button 
                onclick="navigator.clipboard.writeText(document.querySelector('pre').innerText); this.innerText='✓ Copied!'; setTimeout(() => this.innerText='📋 Copy to Clipboard', 2000)" 
                style="border: 1px solid #D1D5DB; background-color: #F9FAFB; color: #374151; border-radius: 10px; padding: 12px 28px; cursor: pointer; font-weight: 600; width: 100%; transition: all 0.2s ease-in-out;"
                onmouseover="this.style.backgroundColor='#F3F4F6'"
                onmouseout="this.style.backgroundColor='#F9FAFB'">
                📋 Copy to Clipboard
            </button>
            """, unsafe_allow_html=True)
            
        # Close the results container
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Clean up temporary file if created from upload
        if input_method == "Upload Image" and os.path.exists(image_path):
            os.unlink(image_path)
            
    except Exception as e:
        error_message.error(f"Error: {str(e)}")
        if input_method == "Upload Image" and os.path.exists(image_path):
            os.unlink(image_path)
    
    # Reset processing state
    st.session_state.processing = False

# Footer
st.markdown("<hr style='margin-top: 30px; margin-bottom: 15px; border: none; height: 1px; background-color: #E5E7EB;'>", unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center;'>
        <p style='font-size: 14px; color: #6B7280;'>
            Powered by Ollama's llama3.2-vision model
        </p>
        <p style='font-size: 12px; color: #9CA3AF;'>
            © 2025 OCRNet Project
        </p>
    </div>
    """, unsafe_allow_html=True)