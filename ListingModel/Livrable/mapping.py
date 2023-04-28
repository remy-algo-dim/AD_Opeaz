#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Remy Adda
# Created Date: 2023
# =============================================================================
"""Linting model which allow to extract relevant informations from listing documents"""
# =============================================================================

import ast

mapping = {
	
		   "reference": '["Code13Réf", "Code Produit", "CIP", "Code CIP", "Code", \
           "Gamme GAVISCONELL Désignation (CIP)", "Code produit", "Code produit (ou Code LPP)	", \
           "Code Article", "C.I.P / Article", "Code EAN"]',

		   "quantite": '["Qté", "Qté Vendue", "Nb unité", "Qt", "Qte Facturée", "Qte Délivrée", "quantité", \
           "Quantité", "Qt é", "Nombre Unités", "Nombre", "Quantité Lieu", "Cdée", "Qt e", "Unités", "Total"]',

		   "CA TTC": '["Montant TTC", "CA Brut TTC", "CA TTC brut", "PV TTC", "CA brut TTC", "PrixV TTC", \
           "Ch Affaire T.T.C.", "CA TTC", ]',

		   "CA HT": '["Rémunération HT", "Chiffre Affraire HT", "Chiffre", "Ch Affaire H.T.", "CA HT", \
           "Montant cdé", "Valeur", "Montant HT", ]',

           "CA": '["CA"]',

		   "prix unitaire HT": '["Prix Vente", "Prix Unitaire €", "Px vente", \
           "PU HT", "HT U Brut", "Prix HT unitaire", "Prix unitaire HT", ]',
           
           "prix unitaire TTC": '["Prix TTC", "Prix Vente TTC", "PVTTC REMISE"]'

          }



inversed_mapping = {value: key for key, value in mapping.items()}

final_inversed_mapping = {}

for key, value in inversed_mapping.items():
    key = ast.literal_eval(key)
    if type(key) == list:
        for item in key:
            final_inversed_mapping[item] = value
    else:
        final_inversed_mapping[key] = value
