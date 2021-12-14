# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from upload_label_crop import main_upload_label_crop
import streamlit as st
from streamlit import cli as stcli
import sys
import os


def main():
    # Set current working directory path
    cwd_path = os.getcwd() + '\\'

    # Upload an PDF, label some parts in an image and crop them
    main_upload_label_crop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

