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

from mapping import final_inversed_mapping
from config_safe import *


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(lineno)d %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



def from_pdf_to_jpg(filename_path):
    """Input: pdf file
    Ouput: Jpg file, usign tesseract"""
    logger.info(filename_path)
    pages = convert_from_path(filename_path)
    file = filename_path.split("/")[-1][:-4]

    for i in range(len(pages)):
        pages[i].save(file + str(i) +'.jpg', 'JPEG')
    # Tesseract
    path_image = file+ str(i) +'.jpg'
    text_image = pytesseract.image_to_string(path_image)   


def pytesseract_for_ref(filename_pdf):
    """
    filename_pdf: filename input PDF
    output: sequence of 13 numbers (reference)
    """
    pages = convert_from_path(filename_pdf)
    for i in range(len(pages)):
        file = '{}_page_{}.jpg'.format(filename_pdf[:-4], i)
        pages[i].save(file, 'JPEG')
    # On lit seulement la page 0 (on ne prend pas en compte les cas ou les pdf > 1 page)
    file = '{}_page_{}.jpg'.format(filename_pdf[:-4], 0)
    text = pytesseract.image_to_string(file)
    # Expression régulière pour les séquences de 13 chiffres
    regex = r"\d{13}"
    matches = re.findall(regex, text.replace(" ", ""))[0]

    return matches


def sanity_check_just_after_API(df_outputs):
    # Need to use the df BEFORE cleaning name (after applying mapping)
    
    # 1 - Goal: chose the correct columns in case of duplicates
    # parfois certains noms de colonnes sont des duplicates ... exemple (proofs-picture_proof-6962_la pharmatheque ratarieux-listing_listerine.pdf)
    duplicates_columns = list(set([col for col in df_outputs.columns.tolist() if df_outputs.columns.tolist().count(col) > 1]))
    if len(duplicates_columns) > 0:
        logger.info("Duplicates columns detected")
        df_outputs = df_outputs.iloc[:, 0:4] # on garde les 3 premieres colonnes. Cette technique est hardcoée sur le document exemple
       
    return df_outputs, df_outputs.to_dict()


def sanity_checks_after_API_and_cleaning(dict_outputs, filename_pdf):
    """
    Input: Dict output after cleaning
    Output: new dict with sanity check
    """
    # Need to use the df AFTER cleaning name (after applying mapping)
    df_outputs = pd.DataFrame(dict_outputs)
    
    # 1 - Check that reference number contains 13 digits
    if "reference" in df_outputs.columns.tolist():
        mask = (df_outputs['reference'].str.replace(' ', '').str.len() == 13)
        df_outputs = df_outputs.loc[mask]
    else:
        logger.info("reference not detected")
        reference_pytesseract = pytesseract_for_ref(filename_pdf)
        df_outputs["reference"] = [reference_pytesseract for i in range(len(df_outputs))]
    
    return df_outputs


def update_retrieved_dictionnary(d, final_inversed_mapping):
    """
    Input:
    - d: dictionnary retireved by ExtractTable API (via retrieve_info() function)
    - final_inversed_mapping: mapping dictionnary which we inversed so that we can do the mapping
    Output:
    cleaned dict
    """

    keys2rename = []
    values2add = []
    keysNotFound = []
    
    # 1. Mapping
    for key, value in d.items():
        if key in list(final_inversed_mapping.keys()):
            keys2rename.append(key)
            values2add.append(value)
        else:
            keysNotFound.append(key)
    
    # 2. For renaming the keys with the correct ones, we need to remove the old ones and add the new ones
    # 2.1 Remove old
    for key in keys2rename:
        del d[key]
    
    # 2.2 Add new
    for key, value in zip(keys2rename, values2add):
        d[final_inversed_mapping[key]] = value
    
    # 3. Remove the non mapped key (maybe we did not succeeded to match - Tests word similarity)
    for key in keysNotFound:
        del d[key]
    return d


def instanceExtractApi(api_key):
    session = ExtractTable(api_key)
    # Checks the API Key validity as well as shows associated plan usage 
    print(session.check_usage())
    return session


def retrieve_info(path_image, pp, api_key=api_key):
    """
    Input: document pdf
    pp: if True, print all the extractions
    Output: dictionnary with all info
    PS:To process PDF, make use of pages ("1", "1,3-4", "all") params in the read_pdf function

    """
    session = instanceExtractApi(api_key)
    table_data = session.process_file(filepath=path_image, output_format="df", pages="all")
    logger.info(session.check_usage())
    if pp:
        print(table_data)
    df = table_data[0]
    df.columns = df.loc[0]
    # for i in range(1,len(table_data)):
    #     df = df.join(table_data[i])
    # # df = pd.concat(table_data, axis=0)
    print(df)
    return df, df[2:].to_dict(), table_data


def pipeline(filename_path, pp=False, api=True, df_info=False, api_key=api_key):
    """
    Pipeline
    Input: Filename
    pp: if True, print all the extractions
    api: if True, we apply ExtractTable API. If False, it means that we already applied it and want
    to apply the function on the extraced df
    df_info: exists only if we already applied the function with api = True the first time
    Output: df & dictionnary with the relevant informations (ExtractTable API + mapping)"""
    # Check few things before applying API
    logger.info("Filename path: {} \n".format(filename_path))
    
    if api:
        df_info, dict_info, table_data = retrieve_info(filename_path, pp, api_key)
    else:
        table_data = None
    df_info, dict_info = sanity_check_just_after_API(df_info)
    #print(df_info.head())
    
    # On a souvent des pb de colonnes, c'est a dire que parfois, les bons noms de colonnes se situent dans les
    # lignes, dûs à des noms de colonnes trop longs repérés par l'API. On utilise une while loop dans laquelle
    # on remonte les lignes petit à petit jusqu'à ce que le code reconnaisse des noms labels
    final_dict = {}
    # Tant que le final_dict (output) est vide ou bien tant que la df output n'est pas 1 (ce qui signifie
    # qu'il reste encore des lignes à remonter pour les faire devenir columns name, on continue)
    i = 1
    while len(final_dict) == 0 and len(df_info) != 1:
        logger.info("Apply function update_retrieved_dictionnary: time {}".format(i))
        final_dict = update_retrieved_dictionnary(dict_info, final_inversed_mapping)
        df_info.columns = df_info.loc[0]
        df_info = df_info[1:]
        dict_info = df_info.to_dict()
        df_info.reset_index(drop=True, inplace=True)
        i+=1
     
    
    # Check few things after applying API
    final_dict = sanity_checks_after_API_and_cleaning(final_dict, filename_path)
    return df_info, final_dict, table_data
    




    