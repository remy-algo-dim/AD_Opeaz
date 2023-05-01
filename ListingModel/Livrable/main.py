#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Remy Adda
# Created Date: 2023
# =============================================================================
"""Linting model which allow to extract relevant informations from listing documents"""
# =============================================================================


from ExtractTable import ExtractTable
import os
import random
import ast
from pdf2image import convert_from_path
import pandas as pd
import logging
import sys
import pytesseract
import re
import argparse
from PIL import Image

from preprocessing import pipeline
from config_safe import *


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(lineno)d %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    # Run the full pipeline function located in preprocessing.py

    parser = argparse.ArgumentParser(description='path of the doc')
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    format_file = args.file.split("/")[-1].split(".")[-1]
    file_path = "/".join(args.file.split(".")[0].split("/")[:-1])
    filename = args.file.split("/")[-1].split(".")[0]

    logger.info(format_file)
    if format_file == "jpg" or format_file == "jpeg":
        logger.info("Convert image to PDF")
        image_file = Image.open(args.file)
        im_1 = image_file.convert('RGB')
        im_1.save("{}/{}.pdf".format(file_path, filename))
        args.file = "{}/{}.pdf".format(file_path, filename)

    df, dic, table_data = pipeline(
        args.file, pp=False, api=True, df_info=False, api_key=api_key)

    next_table = 1

    while len(dic) == 0:
        logger.info(
            "Nothing deteted. Lets test on next table: table {}".format(next_table))
        logger.info("{} tables detected".format(len(table_data)))
        df, dic, _ = pipeline(filename, pp=False, api=False,
                              df_info=table_data[next_table], api_key=api_key)
        next_table += 1

    print(150*"=")
    print("Final outputs: \n")
    print(dic)
    dic.to_excel("test12.xlsx", engine="openpyxl", index=False)
