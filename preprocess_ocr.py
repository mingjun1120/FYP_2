import streamlit as st
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import cv2


def preprocess(image_path):
    # Load the image and display it
    image = cv2.imread(image_path)

    # convert the image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Blur the image slightly (Optional)
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply Otsu's automatic thresholding which automatically determines the best threshold value
    (T, threshImage) = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return threshImage


def main_preprocess_ocr():
    pass
