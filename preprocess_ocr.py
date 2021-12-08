import streamlit as st
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import cv2
import numpy as np
import glob


def noise_removal(image):

    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)

    return image


def preprocess(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # convert the image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur the image slightly (Optional)
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply Otsu's automatic thresholding which automatically determines the best threshold value
    (T, threshImage) = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Remove the noise from the image
    cleaned_image = noise_removal(threshImage)

    return cleaned_image


def main_preprocess_ocr():
    # Set current working directory path
    cwd_path = os.getcwd() + '\\'

    for image_path in glob.glob(f'{cwd_path}Crop_Images\\*.jpg'):

        # Preprocess the image
        cleaned_image = preprocess(image_path)

        # Save the image
        cv2.imwrite(f'{cwd_path}Preprocessed_Crop_Images\\{os.path.basename(image_path)}', cleaned_image)

    # for image_path in glob.glob(f'{cwd_path}Preprocessed_Crop_Images\\*.jpg'):
    #
    #     # Perform OCR on the image
    #     text = pytesseract.image_to_string(Image.open(image_path))
