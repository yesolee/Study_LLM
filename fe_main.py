import requests
import streamlit as st
from PIL import Image

st.title("Cat breed Classification API Test")

image = st.file_uploader("Choose an image")

if st.button("Prediction"):
    if image is not None:
        files= {"file": image.getvalue()}
        headers={"Content-Type":"multipart/form-data"}
        res = requests.post(f"http://127.0.0.1:8000/detect_labels", files=files)
        st.write(str(res.json()))
        st.image(image.getvalue(), width=240)