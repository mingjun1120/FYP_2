import streamlit as st
import os
from PIL import Image
import pytesseract
import cv2
import numpy as np
import glob
import pandas as pd
import re


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


def save_header_content(headers_content, cwd_path):
    header_df = pd.DataFrame(data=headers_content)
    header_df.drop_duplicates(subset=0, keep="first", inplace=True, ignore_index=True)

    '''Check the existence of ':' for each string'''
    header_dict = {}
    for index, each_header_contents in enumerate(header_df.to_numpy()):
        header_dict[index + 1] = list(each_header_contents)

    for key, value in header_dict.items():
        new_dict = {}
        # Remove None values in the list
        value = [x.strip() for x in value if x is not None]  # list(filter(None.__ne__, value))

        # Check the existence of ':' for each string
        punc_num = len(header_dict[key])
        punc_num_ori = punc_num
        for x in value:
            if ':' in x or ';' in x:
                punc_num -= 1

        temp_str = None
        temp_str2 = None
        if punc_num == 0 or punc_num < punc_num_ori:
            for count, x in enumerate(value):
                if ':' in x or ';' in x:
                    lst = x.split(':')
                    temp_str = lst[0].strip()
                    new_dict[temp_str] = lst[1].strip()
                else:
                    if count > 0:
                        temp_str2 = new_dict[temp_str]
                        new_dict[temp_str] = f'{temp_str2}\n{x}'

            for new_dict_key, new_dict_val in new_dict.items():
                new_dict[new_dict_key] = [new_dict_val]
            pd.DataFrame(data=new_dict).to_csv(f'{cwd_path}Results_for_user\\Header{key}.csv', index=False)
        else:
            if os.path.isfile(f"{cwd_path}Results_for_user\\Header{key}.txt"):
                open(f'{cwd_path}Results_for_user\\Header{key}.txt', 'w').close()

            with open(f'{cwd_path}Results_for_user\\Header{key}.txt', 'a') as f:
                for line in value:
                    if type(line) is str:
                        f.write(line)
                        f.write('\n')


def main_preprocess_ocr():
    # Set current working directory path
    cwd_path = os.getcwd() + '\\'

    # Initialize to Tesseract-OCR engine
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for image_path in glob.glob(f'{cwd_path}Crop_Images\\*.jpg'):

        # Preprocess the image
        cleaned_image = preprocess(image_path)

        # Save the image
        cv2.imwrite(f'{cwd_path}Preprocessed_Crop_Images\\{os.path.basename(image_path)}', cleaned_image)

    headers_content = []
    for image_path in glob.glob(f'{cwd_path}Preprocessed_Crop_Images\\*.jpg'):
        # Read the image
        image = cv2.imread(image_path)

        # Check if the image name is start with 'Header' or header followed by a digit. If return not None, means true. Otherwise, false.
        if re.search(pattern='^((H|h)eader\d)', string=os.path.basename(image_path).lower()) is not None:
            text = pytesseract.image_to_string(image=image, lang='eng+ind+msa', config='--psm 4')

            headers_content.append([" ".join(x.split()) for x in text.splitlines() if any(map(str.isdigit, x)) or any(map(str.isalpha, x))])
        # else:
        #     text = pytesseract.image_to_string(image=image, lang='eng+ind+msa', config='--psm 6')

    # # Save the header contents extracted from pytesseract
    # save_header_content(headers_content, cwd_path)

