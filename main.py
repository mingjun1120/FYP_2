# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import streamlit as st
import os
from pdf2image import convert_from_path
from PIL import Image

from detect2 import main_detect2


def main():
    # Set current working directory path
    cwd_path = os.getcwd() + '\\'
    print(f'Current Working Directory: {cwd_path}')

    st.title("PDF Bank Statement Extractor")
    st.markdown("**This app can help you to extract certain contents from your uploaded PDF file.**")

    # Upload a file to "PDF Source" for finding the ROIs
    uploaded_file = st.file_uploader(label="Upload a PDF bank document", type=["pdf"])

    if uploaded_file is not None:
        # Save the uploaded file to the PDF Source directory
        with open(os.path.join(f"{cwd_path}PDF Source\\", f"{uploaded_file.name}"), 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Get the uploaded file name
        filename = uploaded_file.name.replace('.pdf', '')

        # Convert each page of the uploaded PDF file into images using "convert_from_path function" from "pdf2image"
        with st.spinner(text="Converting each page of the PDF to an image..."):
            images = convert_from_path(pdf_path=f"{cwd_path}PDF Source\\{filename}.pdf", dpi=350)
            for index, img in enumerate(images):
                img.save(f'PDF_Images\page{index + 1}.jpg', 'JPEG')
        # st.success('Successfully converted to images!')

        # Display an image of the first page of the uploaded PDF file
        st.text("")
        st.markdown(f'**Example image converted from the first page of the uploaded PDF file:**')
        image = Image.open(f"{cwd_path}PDF_Images/page1.jpg")
        st.image(image, caption=f"First page of the uploaded PDF file", use_column_width='auto')

        st.markdown("***")

        # Rum object detection for the images converted from the uploaded PDF file
        with st.spinner(text="Labeling the images..."):
            # os.popen(f'python detect.py --weights best.pt --img-size 416 --conf-thres 0.5 --source {cwd_path}PDF_Images')
            main_detect2()

        # Display the labeling results for an image (first page of the uploaded PDF file)
        st.markdown(f'**Example labeling results for the first page of the uploaded PDF file:**')
        image = Image.open(f"{cwd_path}Results/page1.jpg")
        st.image(image, caption=f"Detection results for the first page of the uploaded PDF file", use_column_width='auto')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
