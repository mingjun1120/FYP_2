import shutil
import streamlit as st
import os
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


def mark_region(image_path):
    image = cv2.imread(image_path)

    # define threshold of regions to ignore
    THRESHOLD_REGION_IGNORE = 40

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV + cv2.THRESH_BINARY, 11, 30)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    line_items_coordinates = []
    for c in cnts:
        # area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)

        if w < THRESHOLD_REGION_IGNORE or h < THRESHOLD_REGION_IGNORE:
            continue

        image = cv2.rectangle(image, (x, y), (x + w, y + h), color=(255, 0, 255), thickness=3)
        line_items_coordinates.append([(x, y), (x + w, y + h)])

    # Sort the coordinates in the 'line_items_coordinates' list
    sort_coordinates_dict = {}
    for each_bounding_box in line_items_coordinates:
        sort_coordinates_dict[each_bounding_box[0][0]] = each_bounding_box
    line_items_coordinates = list(dict(sorted(sort_coordinates_dict.items(), key=lambda item: item[0])).values())  # sort by keys

    return image, line_items_coordinates


def created_row_headers(cwd_path):
    rowHeaderLst = []
    for image_path in glob.glob(f'{cwd_path}Preprocessed_Crop_Images\\*.jpg'):
        if 'HeaderRow_' in os.path.basename(image_path):
            img = cv2.imread(f'{image_path}')
            text = pytesseract.image_to_string(image=img, lang='eng', config='--psm 4 --oem 3')
            rowHeaderLst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None][1].split()

            for count, x in enumerate(rowHeaderLst):
                if x == 'Date':
                    rowHeaderLst[count - 1] = rowHeaderLst.pop(count - 1) + ' ' + x
                elif x == 'No.':
                    rowHeaderLst[count - 1] = rowHeaderLst.pop(count - 1) + ' ' + x
                elif x == 'Credit':
                    rowHeaderLst[count - 1] = rowHeaderLst.pop(count - 1) + ' ' + x
                else:
                    pass
            break

    return rowHeaderLst


def main_preprocess_ocr():
    # Set current working directory path
    cwd_path = os.getcwd() + '\\'

    # Initialize to Tesseract-OCR engine
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Preprocess the image and saved into "Preprocessed_Crop_Images" folder
    for image_path in glob.glob(f'{cwd_path}Crop_Images\\*.jpg'):
        # Preprocess the image
        cleaned_image = preprocess(image_path)

        # Save the image
        cv2.imwrite(f'{cwd_path}Preprocessed_Crop_Images\\{os.path.basename(image_path)}', cleaned_image)

    # Create the row headers
    rowHeaderLst = created_row_headers(cwd_path)
    if len(rowHeaderLst) == 0 or len(rowHeaderLst) != 6:
        rowHeaderLst = ['Txn. Date', 'Val. Date', 'Description', 'Cheque No.', 'Debit/Credit', 'Balance']

    saldo_awal = None
    saldo_awal_val = None
    startingPage = 1
    table_row_list = []
    for image_path in glob.glob(f'{cwd_path}Crop_Images\\*.jpg'):

        # Check if the image name is start with 'Header' or header followed by a digit. If return not None, means true. Otherwise, false.
        if re.search(pattern='^((r|R)ow_page\d)', string=os.path.basename(image_path).lower()) is not None:

            # Mark the region of interest
            image, line_items_coordinates = mark_region(image_path)

            first_column_val = None
            second_column_val = None
            third_column_val = None
            forth_column_val = None
            fifth_column_val = None
            sixth_column_val = None

            for counter, each_image_coord in enumerate(line_items_coordinates, start=1):

                x1, y1 = each_image_coord[0]
                x2, y2 = each_image_coord[1]

                # Crop the image
                crop_img = image[y1:y2, x1:x2]

                # Save the image
                img_path = f'{cwd_path}Test_Image\\{os.path.basename(image_path).replace(".jpg", f"_{counter}.jpg")}'
                cv2.imwrite(f'{img_path}', crop_img)

                # Read the image
                crop_img = cv2.imread(f'{img_path}')

                # Preprocess the image_path
                # cleaned_image = preprocess(img_path)

                text = pytesseract.image_to_string(image=crop_img, lang='msa+ind', config='--psm 6 --oem 3')
                text2 = pytesseract.image_to_string(image=crop_img, lang='msa+ind', config='--psm 4 --oem 3')

                if img_path.endswith('_1.jpg'):
                    print(f'First column value: {text}')
                    try:
                        first_column_val = [x for x in text.split() if x == "Total" or re.search(pattern="^(\d{2}\/\d{2})$", string=x)][0]
                    except IndexError:
                        print(f'First column value 2: {text2}')
                        try:
                            first_column_val = [x for x in text2.split() if x == "Total" or re.search(pattern="^(\d{2}\/\d{2})$", string=x)][0]
                        except:
                            first_column_val = None

                elif img_path.endswith('_2.jpg'):
                    print(f'Second column value: {text}')
                    try:
                        second_column_val = [x for x in text.split() if re.search(pattern="^(\d{2}\/\d{2})$", string=x)][0]
                    except IndexError:
                        print(f'Second column value 2: {text2}')
                        try:
                            second_column_val = [x for x in text2.split() if re.search(pattern="^(\d{2}\/\d{2})$", string=x)][0]
                        except:
                            second_column_val = None

                elif img_path.endswith('_3.jpg'):
                    third_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in third_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if 'saldo awal' in temp.lower():
                        saldo_awal = 'SALDO AWAL'
                    else:
                        third_column_val = temp

                elif img_path.endswith('_4.jpg'):
                    forth_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in forth_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if saldo_awal is not None and img_path.startswith('Row_page1_1'):
                        third_column_val = temp
                    elif saldo_awal is None and 'saldo awal' in temp.lower():
                        saldo_awal = 'SALDO AWAL'
                    elif temp.isdecimal() and forth_column_val is None:
                        forth_column_val = temp
                    elif (',' in temp or '.' in temp) and fifth_column_val is None:
                        fifth_column_val = temp
                    else:
                        pass

                elif img_path.endswith('_5.jpg'):
                    fifth_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in fifth_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if forth_column_val is None and temp.isdecimal():
                        forth_column_val = temp
                    elif forth_column_val is not None and (',' in temp or '.' in temp) and fifth_column_val is None:
                        fifth_column_val = temp
                    elif fifth_column_val is not None and (',' in temp or '.' in temp) and sixth_column_val is None:
                        sixth_column_val = temp
                    else:
                        pass

                elif img_path.endswith('_6.jpg'):
                    sixth_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in sixth_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if fifth_column_val is None and (',' in temp or '.' in temp):
                        fifth_column_val = temp
                    elif fifth_column_val is not None and (',' in temp or '.' in temp) and sixth_column_val is None:
                        sixth_column_val = temp
                    else:
                        pass

                elif img_path.endswith('_7.jpg'):
                    seventh_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in seventh_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if sixth_column_val is None and (',' in temp or '.' in temp) and forth_column_val is not None:
                        sixth_column_val = temp
                    else:
                        saldo_awal_val = temp

                elif img_path.endswith('_8.jpg'):
                    eighth_column_val_lst = [x.strip() for x in text.splitlines() if x.strip() != '' and x.strip() is not None]
                    new_str = ''
                    for each_val in eighth_column_val_lst:
                        new_str += each_val + '\n'
                    temp = new_str[:-1]

                    if sixth_column_val is not None and (',' in temp or '.' in temp) and forth_column_val is not None:
                        saldo_awal_val = temp

            rowHeaderDict = {rowHeaderLst[0]: first_column_val, rowHeaderLst[1]: second_column_val,
                             rowHeaderLst[2]: third_column_val, rowHeaderLst[3]: forth_column_val,
                             rowHeaderLst[4]: fifth_column_val, rowHeaderLst[5]: sixth_column_val}

            # Save each row of data into a dictionary
            print(f'\nTxn. Date: {rowHeaderDict[rowHeaderLst[0]]}')
            print(f'Val. Date: {rowHeaderDict[rowHeaderLst[1]]}')
            print(f'Description: {rowHeaderDict[rowHeaderLst[2]]}')
            print(f'Cheque No.: {rowHeaderDict[rowHeaderLst[3]]}')
            print(f'Debit/Credit: {rowHeaderDict[rowHeaderLst[4]]}')
            print(f'Balance: {rowHeaderDict[rowHeaderLst[5]]}')
            print("--------------------------------------------------\n")

            # Example: the actual filename is "Row_page1_1.jpg" and then becomes "Row_page1"
            currentPage = os.path.basename(image_path)
            currentPage = currentPage[:currentPage.rfind('_')]
            currentPage = int(currentPage.replace('Row_page', ''))

            if currentPage - startingPage == 1:
                startingPage += 1
                pd.DataFrame(table_row_list).to_csv(f'{cwd_path}Results_for_user\\Page{startingPage-1}.csv', index=False)
                table_row_list = []
                table_row_list.append(rowHeaderDict)
            else:
                table_row_list.append(rowHeaderDict)

    # Save the last page of data
    pd.DataFrame(table_row_list).to_csv(f'{cwd_path}Results_for_user\\Page{startingPage}.csv', index=False)

    if saldo_awal_val is not None and saldo_awal is not None:
        df1 = pd.read_csv(f'{cwd_path}Results_for_user\\Page1.csv')
        df1.loc[0] = np.array(['', '', saldo_awal, '', '', saldo_awal_val])
        df1.to_csv(f'{cwd_path}Results_for_user\\Page1.csv', index=False)

    if os.path.isfile(f"{cwd_path}Results_for_user\\Page1.csv"): # If the file exist
        st.markdown("***")
        st.markdown(f'**Example table results for Page 1:**')
        st.dataframe(pd.read_csv(f'{cwd_path}Results_for_user\\Page1.csv'))

        # Create the zip file for the "Results_for_user" folder
        shutil.make_archive(base_name=f'{cwd_path}Results_for_user', format='zip', root_dir=f'{cwd_path}Results_for_user')

    # Delete the images in "Crop_Images" folder
    for image_path in glob.glob(f'{cwd_path}Crop_Images\\*.jpg'):
        os.remove(image_path)

    # Delete the "Detection_Results" folder
    shutil.rmtree(f'{cwd_path}Detection_Results')

    # Delete the images in "PDF_Source" folder
    for image_path in glob.glob(f'{cwd_path}PDF_Source\\*.jpg'):
        os.remove(image_path)

    # Delete the images in "PDF_Images" folder
    for image_path in glob.glob(f'{cwd_path}PDF_Images\\*.jpg'):
        os.remove(image_path)

    # Delete the images in "Preprocessed_Crop_Images" folder
    for image_path in glob.glob(f'{cwd_path}Preprocessed_Crop_Images\\*.jpg'):
        os.remove(image_path)

    # Delete the images in "Results_for_user" folder
    for image_path in glob.glob(f'{cwd_path}Results_for_user\\*.jpg'):
        os.remove(image_path)

    # Delete the images in "Test_Image" folder
    for image_path in glob.glob(f'{cwd_path}Test_Image\\*.jpg'):
        os.remove(image_path)

    with open(f"Results_for_user.zip", "rb") as fp:
        btn = st.download_button(
            label="Download Results",
            data=fp,
            file_name="Results_for_user.zip",
            mime="application/zip"
        )
