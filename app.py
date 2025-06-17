import streamlit as st
import cv2
from PIL import Image
import pytesseract
import numpy as np
import pandas as pd
import pickle
from datetime import datetime

# Configure Tesseract executable path if needed (uncomment and modify if necessary)
# pytesseract.pytesseract.tesseract_cmd = r'path_to_your_tesseract_executable'

# Load pickle data (replace with your actual data loading logic)
def load_data():
    with open(r'C:\Users\JO Ron\Documents\MinorMajor Project\Major Project\data.pkl', 'rb') as f:
        data = pickle.load(f)
    return data

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Failed to open the camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        st.error("Failed to capture image.")
        return None
    return frame

def extract_text_from_image(image, data):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    text = pytesseract.image_to_string(pil_image)
    text = text.strip().upper()
    
    plate_numbers = []
    if 'Plate_ID' in data.columns:
        words = text.split()
        for word in words:
            if word in data['Plate_ID'].values:
                plate_numbers.append(word)
    return plate_numbers

def main():
    st.title("Number Plate Detection Using Image-To-Text Processing")

    # State to keep track of captured image, extracted text, and loaded data
    if 'camera_opened' not in st.session_state:
        st.session_state.camera_opened = False
    if 'captured_image' not in st.session_state:
        st.session_state.captured_image = None
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = []
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    if not st.session_state.camera_opened:
        if st.button("Open Camera"):
            st.session_state.camera_opened = True
            frame = capture_image()
            if frame is not None:
                st.session_state.captured_image = frame
                st.session_state.extracted_text = []

    if st.session_state.captured_image is not None:
        st.image(st.session_state.captured_image, channels="BGR")

        if st.button("Extract Text From Image"):
            plate_numbers = extract_text_from_image(st.session_state.captured_image, st.session_state.data)
            if plate_numbers:
                st.session_state.extracted_text = plate_numbers
            else:
                st.error("No matching Plate Number found in the dataset.")

        st.subheader("Detected Text")
        for plate in st.session_state.extracted_text:
            st.write(plate)

        if st.button("Check Plate Number"):
            df = pd.DataFrame(st.session_state.data)
            if 'Plate_ID' in df.columns and 'Expiration_Date' in df.columns:
                for plate in st.session_state.extracted_text:
                    match = df[df['Plate_ID'] == plate]
                    if not match.empty:
                        expiration_date = match['Expiration_Date'].values[0]
                        expiration_date = pd.to_datetime(expiration_date)
                        current_date = datetime.now()

                        if expiration_date < current_date:
                            st.markdown(f"<span style='color:red'>Plate Number: {plate}   Vehicle is NOT Registered!</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:green'>Plate Number: {plate}   Vehicle is Registered!</span>", unsafe_allow_html=True)
                        
                        st.write(match)
                    else:
                        st.error(f"Plate Number {plate} not found in data.")
            else:
                st.error("Data format error: 'Plate_ID' or 'Expiration_Date' column not found.")
        
        if st.button("Retake Image"):
            st.session_state.camera_opened = False
            st.session_state.captured_image = None
            st.session_state.extracted_text = []

if __name__ == "__main__":
    main()
