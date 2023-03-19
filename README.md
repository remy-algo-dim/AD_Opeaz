# AD_Opeaz

## 1 - ListingModel

Le ListingModel est un modèle permettant d'extraire les données des listing de ventes:

Input: fichier pdf, jpeg ...

Output: 
- référence des produits vendus
- quantitté
- CA ...


### Contenu:

- requirements.txt: contient les librairies python nécessaires
- config_safe.py: api_key pour l'API ExtractTable permettant de récupérer les tables d'un document au format pandas
- mapping.py: contient un mappping fait à la main pour mapper les différents éléments extraits, aux noms des targets:
exemple: si CIP est reperé dans le document, le mapping se chargera de renomer cette colonne: référence.
- proccessing.py: fichier contenant plusieurs fonctions python permettant de clean les dataframes, convertir les jpeg en pdf par exemple,
ainsi que toutes les fonctions nécessaires à l'implémentation de la pipiline
- main.py: fichier à run pour obtenir les résultats


### Utilisation:

- choisir un listing de vente
- se rendre dans la directory de ce projet
- entrer la commande: python main.py "chemin du fichier"
- un dictionnaire est print en sortie



### Parties manquantes:

- Ce projet traite beaucoup de cas de listings mais pas la totalité. Il est important de relever tous les cas non fonctionnels afin de pouvoir améliorer le modèle dans le temps
- les dates (périodes): sujet pas encore clair avec Opeaz. Pour l'instant je ne retourne pas les dates. (J'ai testé chatGpt et ce dernier a extrait parfaitement les périodes). A preciser
- certains types ne sont pas encore pris en comptes: csv, xlsx ... la difficulté concernant les pdf et jpg, je ne me suis focus que sur ceux la pour l'instant