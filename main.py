# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from upload_label_crop import main_upload_label_crop
import streamlit as st
import os
from pdf2image import convert_from_path
from PIL import Image
from detect2 import main_detect2


def main():
    main_upload_label_crop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
