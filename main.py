# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from upload_label_crop import main_upload_label_crop
from preprocess_ocr import main_preprocess_ocr

def main():
    # Upload an PDF, label some parts in an image and crop them
    main_upload_label_crop()

    # Preprocess the image and do OCR
    main_preprocess_ocr()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
