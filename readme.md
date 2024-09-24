# Usage du script `facturix.py`

Ce script permet de générer des factures au format Factur-X à partir de fichiers PDF et d'un fichier CSV contenant les données des factures.

## Arguments et Options

### `-i` ou `--input_dir`

- **Description :** Obligatoire. Spécifie le dossier contenant les fichiers PDF des factures.
- **Exemple :** `-i /chemin/vers/dossier`

### `-c` ou `--input_csv`

- **Description :** Obligatoire. Spécifie le fichier CSV contenant les données des factures.
- **Exemple :** `-c /chemin/vers/fichier.csv`

### `-o` ou `--output_dir`

- **Description :** Obligatoire. Spécifie le dossier où les fichiers de sortie seront enregistrés.
- **Exemple :** `-o /chemin/vers/dossier_de_sortie`

### `-f` ou `--force_recalc`

- **Description :** Optionnel. Si spécifié, force le recalcul du CSV de lien facture-fichier.
- **Exemple :** `-f` (pour forcer le recalcul)

### `-v` ou `--verbose`

- **Description :** Optionnel. Augmente le niveau de verbosité. Peut être utilisé jusqu'à deux fois pour obtenir plus de détails dans les messages de sortie.
- **Exemple :** `-v` ou `-vv` (pour augmenter le niveau de verbosité)

## Exemple de commande

Pour exécuter le script avec les options ci-dessus, utilisez une commande comme celle-ci :

```sh
python facturix.py -i /chemin/vers/dossier -c /chemin/vers/fichier.csv -o /chemin/vers/dossier_de_sortie -f -v
```

## Fichier CSV d'entrée

Le tableau ci-dessous décrit les colonnes attendues dans le fichier CSV d'entrée. Chaque ligne du fichier CSV représente une facture et doit contenir les informations requises. Un PDf Factur-X sera généré pour chaque ligne du fichier CSV, si le pdf correspondant est trouvé dans le dossier d'entrée (aka il existe un pdf contenant le numéro de facture dans le fichier).
_BT = dénomination dd'une donnée métier dans la norme sémantique européenne_

| Numéro BT | Description |
|-----------|-------------|
| BT-23 | Process Chorus A1 (dépôt facture), A2 (dépôt facture déjà payée) |
| BT-24 | Identification de spécification : référence au format et profil utilisé (pas besoin pour l'instant)|
| BT-1 | numéro de facture |
| BT-3 | type de facture ex 380 : Facture commerciale|
| BT-2 | date d’émission de la facture |
| BT-10 | référence acheteur |
| BT-27 | nom (raison sociale) du fournisseur |
| BT-30 | identification légale du vendeur |
| BT-31 | numéro de TVA intracommunautaire |
| BT-47 | identification légale de l’acheteur |
| BT-44 | nom de l’acheteur (raison sociale) |
| BT-13 | numéro de commande fourni par l’acheteur |
| BT-5 | devise de la facture (toujours EUR)|
| BT-109 | montant HT |
| BT-110 | montant de la TVA où currencyID = BT-5 |
| BT-112 | montant TTC |
| BT-115 | montant net à payer |

Pour le détail des colones : se référer à la section **Description sémantique du Profil MINIMUM** plus bas dans ce readme.

## Résumé des étapes principales

1. **Lister les fichiers PDF d'entrée** :
    - Balayage du dossier spécifié pour lister tous les fichiers PDF présents.

2. **Faire le lien données - PDF** :
    - Extraction des numéros de facture des fichiers PDF.
    - Fusion des informations extraites des PDF avec celles contenues dans le fichier CSV d'entrée.

3. **Génération des XML CII** :
    - Production des fichiers XML à partir des données fusionnées, en utilisant un modèle XML.

4. **Validation des XML générés** :
    - Validation des fichiers XML générés contre un fichier Schematron et un schéma XSD spécifique.

5. **Intégration des XML dans les PDF** :
    - Incorporation des fichiers XML validés dans les fichiers PDF originaux pour produire des PDF conformes au standard Factur-X.

6. **Création des archives ZIP** :
    - Archivage des fichiers PDF intégrés dans des fichiers ZIP en respectant des contraintes de nombre de fichiers et de taille maximale.

## Choix arbitraires réalisés

### Comment Peupler le xml

Je vois deux façons de peupler le xml :

- mettre des placeholder et les replace dans un str, facile
- mettre des id dans les balises du xml modèle, puis remplacer les valeurs des balises correspondantes, plus carré, mais plus lourd

| Critère                 | **Placeholders (Approche 1)**                                   | **XPath (Approche 2)**                                        |
|-------------------------|-----------------------------------------------------------------|---------------------------------------------------------------|
| **Facilité de mise en œuvre**  | **Plus facile** : Simple recherche et remplacement des placeholders. | **Plus difficile** : Nécessite une compréhension d'XML et XPath. |
| **Maintenabilité**       | **Faible** : Nécessite une gestion minutieuse des placeholders à mesure que l'XML grandit. | **Élevée** : Conscient de la structure et plus facile à adapter avec le temps. |
| **Précision**            | **Faible** : Le remplacement de chaînes peut entraîner des erreurs. | **Élevée** : XPath garantit que les bons éléments sont mis à jour. |
| **Performance**          | **Rapide pour les petits fichiers XML** : Basé sur des chaînes, plus rapide pour les tâches simples. | **Optimal pour les grands fichiers XML** : Peut gérer des fichiers complexes et volumineux de manière structurée. |
| **Robustesse**           | **Faible** : Ne gère pas bien les changements de structure.      | **Élevée** : Gère mieux les changements de structure en ciblant précisément les éléments. |
| **Flexibilité**          | **Faible** : Limité à des remplacements simples.                | **Élevée** : Peut manipuler des XML complexes.               |
| **Professionnalisme**    | **Basique** : Adapté aux cas d'utilisation plus simples.         | **Plus professionnel** : Meilleur pour les projets complexes et à long terme. |

Je dirais dans un premier temps go easy !

Principe : On met des balises `{{BT-XX}}` dans notre `MINIMUM_template.xml`, on le parse avec _xmltree_ on le transforme en str, puis on fait un simple replace de la balise par la bonne valeur issue de la dataframe d'entrée

## Connaissances et sources

### Factur-x

Le format Factur-X est un standard hybride de facture électronique combinant un fichier PDF lisible et des données structurées au format XML. Il permet de faciliter l'automatisation du traitement des factures, tout en conservant une version visuelle pour la consultation humaine, conforme aux normes européennes de facturation électronique `EN16931`.

Le XML embarqué dans une facture Factur-X est toujours conforme au standard CII (Cross Industry Invoice) de l'UN/CEFACT.

https://fnfe-mpe.org/factur-x/

#### Que vaut https://github.com/akretion/factur-x ?

- **facturx-pdfgen**: generate a Factur-X or Order-X PDF file from a regular PDF file and an XML file
- **facturx-pdfextractxml**: extract the XML file from a Factur-X or Order-X PDF file
- **facturx-xmlcheck**: check a Factur-X or Order-X XML file against the official XML Schema Definition

Cette lib python est capable de générer le Factur-X à partir d'un pdf et d'un xml. Puis de vérifier que le résultat est conforme à la norme définie par xsd.

Reste donc à générer le xml.

### CII (Cross Industry Invoice)

Le CII (Cross Industry Invoice) est un schéma XML normé par l'UN/CEFACT qui permet de structurer des informations de facturation de manière détaillée et interopérable. Il inclut des éléments couvrant des données essentielles telles que les informations de l'acheteur et du vendeur, les articles facturés, les montants, les taxes, ainsi que des métadonnées spécifiques au processus de facturation. Le modèle CII est conçu pour être extensible, permettant l'ajout de champs spécifiques à certaines industries tout en garantissant la conformité avec les standards internationaux d'échange de données commerciales.

Comme il est extensible, il va probablement falloir un générateur de CII par plateforme de destination des factur-x.

### Plateforme Chorus

Chorus est l'ERP 100% dématérialisé de l'État. Il permet de gérer l'ensemble des processus de facturation et de paiement électroniques entre les administrations et leurs fournisseurs.


### Format factures

La doc chorus est fournie, mais il est difficile de trouver le xml le plus simple à embarquer.

#### E1 VS E2

source https://communaute.chorus-pro.gouv.fr/documentation/specifications-externes/ Annexe EDI page 18
**Flux structuré Facture (E1)** :

- Ce flux contient toutes les données de facturation au format structuré XML.
- Il est destiné aux systèmes comptables et financiers de l'État, des collectivités locales ou des établissements publics nationaux.
- Les données sont suffisamment détaillées pour permettre une gestion complète de la facture par les systèmes informatiques de l'administration.
- Il est recommandé pour les entreprises ayant un processus de facturation très structuré, capable de générer toutes les informations sous un format XML détaillé et adapté aux besoins des administrations .

**Flux mixte Facture (E2)** :

- Ce flux combine des données structurées et des pièces jointes non structurées (comme des fichiers PDF).
- Il transmet le lot minimal de données nécessaires au traitement de la facture, avec la possibilité d'ajouter des pièces jointes pour représenter la facture dans d'autres formats (hors PDF/A3).
- Il est recommandé pour les fournisseurs qui souhaitent utiliser à la fois des formats structurés et des pièces jointes non structurées, par exemple lorsque le système du fournisseur ne permet pas une structuration complète des données .

**En Gros, si on a la possibilité de tout mettre en XML, Il vaut mieux choisir E1.**

Dans notre cas, **E2 est le choix du moindre effort**, car on aura pas besoin **d'extraire les données des factures du PDF

#### Choix du format pour le flux E2

| Format                       | Bibliothèque/Lien                                | Commentaire                                                                                                                                                                                           | +                                             | -                               |
| ---------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------- |
| UBL-Invoice                  | Rien de probant                                  | International                                                                                                                                                                                         | International                                 | pas de lib                      |
| CPP Factures Minimal         | VIDE                                             | Spécifique CHORUS                                                                                                                                                                                     | Format de Flower                              | pas de lib et spécifique chorus |
| Cross Industry Invoice (CII) | VIDE                                             | Plus complexe                                                                                                                                                                                         |                                               | pas de lib et complexe          |
| Factur-X                     | [factur-x](https://github.com/akretion/factur-x) | Franco-German complies with the European e-invoicing standard [EN 16931](https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/Obtaining+a+copy+of+the+European+standard+on+eInvoicing). | déjà lib* + supporté par Odoo + doc détaillée | Franco-German                   |

_A première vue, je dirais que Factur-X est plus simple car il existe déjà une implémentation, il faudrait voir exactement ce qu'elle fait._

#### Description sémantique du Profil MINIMUM

Source : la documentation de la norme Factur-X _VERSION 1.0.06 (ZUGFeRD V2.2) – 1er Mars 2022_ disponible ici [https://fnfe-mpe.org/factur-x/](https://fnfe-mpe.org/factur-x/) contient un exemple de facture Factur-X avec le XML associé, et évoque son utilisation pour Chorus
L’ensemble des données du profil MINIMUM sont présentées ci-dessous :

- **BG-2** : groupe « Contrôle de Processus » : entête de message, **groupe Obligatoire** :
  - **BT-23** : identification du business process utilisé, donnée _facultative_, permet d’indiquer quel cas métier est utilisé. Ceci peut servir par exemple pour ouvrir vers une facturation B2C où les règles de calcul ne sont pas les mêmes que pour une facture B2B.
  - **BT-24** : Identification de spécification : référence au format et profil utilisé : donnée **Obligatoire**
- **BT-1** : numéro de facture, donnée **Obligatoire**
- **BT-2** : date d’émission de la facture, donnée **Obligatoire** (ainsi que le format de date)
- **BT-3** : type de facture (facture ou avoir), donnée **Obligatoire**, appartenant à la liste UNTDID 1001. Dans le cadre du profil MINIMUM, le code retenu peut être 751 (en particulier pour l’Allemagne) car le fichier de données ne comporte pas toutes les mentions obligatoires d’une facture, mais uniquement des données permettant sa comptabilisation. Il en résulte que les avoirs doivent être codifiés sous forme de factures négatives pour ce profil. Toutefois, pour la France, il est autorisé d’utiliser l’ensemble des codes disponibles (codes de facture et codes d’avoir).
- **BT-10** : référence acheteur fournie par l’acheteur, permettant d’adresser la facture vers le bon service de l’acheteur. C’est une donnée _facultative_, mais qui peut être exigée par l’acheteur. Pour le Secteur Public, cette donnée est **obligatoire** et correspond au « Service Exécutant ».
- **BT-13** : numéro de Commande fourni par l’acheteur. C’est une donnée _facultative_, mais qui peut être exigée par l’acheteur. Pour le Secteur Public, cette donnée est **obligatoire** et correspond à « l’Engagement Juridique ».
- **BG-4** : groupe de données relatives au vendeur : **groupe Obligatoire**
  - **BT-27** : nom du fournisseur (dénomination légale sous laquelle le fournisseur est enregistré), donnée **Obligatoire**
  - **BT-30** : identification légale du vendeur (n° de SIREN / SIRET), donnée **Obligatoire** si le vendeur n’a pas de Numéro de TVA intracommunautaire, fortement recommandé sinon. Cette donnée fait l’objet d’un attribut venant indiquer le référentiel de l’identification.
  - **BT-31** : numéro de TVA intracommunautaire du vendeur, donnée **Obligatoire** si le vendeur dispose d’un N° de TVA intracommunautaire.
  - **BG-5** : sous-groupe d’information sur l’adresse postale du Vendeur, **groupe Obligatoire**
    - **BT-40** : code Pays du vendeur, donnée **Obligatoire** (qui permet d’identifier la territorialité de la facture)
- **BG-7** : groupe de données relatives à l’acheteur, **groupe Obligatoire**.
  - **BT-44** : Nom de l’acheteur (raison sociale), donnée **Obligatoire**.
  - **BT-47** : identification légale de l’acheteur (n° de SIREN / SIRET), donnée _facultative fortement recommandée_ car permettant d‘identifier le destinataire de façon plus fiable qu’un nom. Pour le Secteur Public, cette donnée est **obligatoire** et correspond au numéro de SIRET de l’entité facturée. Cette donnée fait l’objet d’un attribut venant indiquer le référentiel de l’identification (SIRET recommandé).
- **BT-5** : code de la devise de facturation, donnée **Obligatoire**
- **BG-22** : groupe des montants totaux de la facture (ou avoir), **bloc Obligatoire** :
  - **BT-109** : montant Total HT de la facture (y compris remises et charges de pied de facture), donnée **Obligatoire**
  - **BT-110** : montant Total de la TVA de la facture, donnée **Obligatoire** si la facture n’est pas hors champ d’application de la TVA. Ce montant s’accompagne d’un attribut précisant la monnaie de comptabilisation de la TVA.
  - **BT-112** : montant Total TTC, donnée **Obligatoire**
  - **BT-115** : montant Net à Payer de la facture, donnée **Obligatoire**

_Source : Factur-X 1.0.06  
© FNFE-MPE | FeRD – droits réservés – 1er mars 2022  
Pages 36 et 37 / 133_
