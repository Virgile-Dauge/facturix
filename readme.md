# Ce que l'on sait  

## Process

### Entrées 

- Un dossier `data_dir/input/` contenant des pdfs de factures.
- Un csv `data_dir/factur_data.csv` contant des infos sur les factures à traiter


Les infos minimales sont les suivantes : 
BT = dénomination dd'une donnée métier dans la norme sémantique européenne

| Numéro BT | Description |
|-----------|-------------|
| BT-23 | Process Chorus A1 (dépôt facture), A2 (dépôt
facture déjà payée) |
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

### Sorties Attendues
Pour chaque pdf dans `data_dir/input/`, si présent dans `data_dir/factur_data.csv` (la manière de l'identifier reste à définir), un pdf au format `PDF/A-3` contenant un xml `factur-x.xml` permetant son traitement. 
Le xml pourra varier pour se conformer à la plateforme de destination. Les pdfs de sortie seront dans `data_dir/output/pdf`

Dans un second temps, les pdfs générés pourront êtres zippés par groupes, afin de respecter la taille max imposée par la plateforme de destination. Les zip produits seront enregistrés dans `data_dir/output/zip`

## Factur-x
Le format Factur-X est un standard hybride de facture électronique combinant un fichier PDF lisible et des données structurées au format XML. Il permet de faciliter l'automatisation du traitement des factures, tout en conservant une version visuelle pour la consultation humaine, conforme aux normes européennes de facturation électronique `EN16931`. 

Le XML embarqué dans une facture Factur-X est toujours conforme au standard CII (Cross Industry Invoice) de l'UN/CEFACT.

https://fnfe-mpe.org/factur-x/

### Que vaut https://github.com/akretion/factur-x ? 
- **facturx-pdfgen**: generate a Factur-X or Order-X PDF file from a regular PDF file and an XML file
- **facturx-pdfextractxml**: extract the XML file from a Factur-X or Order-X PDF file
- **facturx-xmlcheck**: check a Factur-X or Order-X XML file against the official XML Schema Definition
 
Cette lib python est capable de générer le Factur-X à partir d'un pdf et d'un xml. Puis de vérifier que le résultat est conforme à la norme définie par xsd.

Reste donc à générer le xml. 

### CII (Cross Industry Invoice)

Le CII (Cross Industry Invoice) est un schéma XML normé par l'UN/CEFACT qui permet de structurer des informations de facturation de manière détaillée et interopérable. Il inclut des éléments couvrant des données essentielles telles que les informations de l'acheteur et du vendeur, les articles facturés, les montants, les taxes, ainsi que des métadonnées spécifiques au processus de facturation. Le modèle CII est conçu pour être extensible, permettant l'ajout de champs spécifiques à certaines industries tout en garantissant la conformité avec les standards internationaux d'échange de données commerciales.

Comme il est extensible, il va probablement falloir un générateur de CII par plateforme de destination des factur-x.

#### Chorus

La doc chorus est fournie, mais il est difficile de trouver le xml le plus simple à emnbarquer. 

Donc, en cherchant parmi les exemples de pdf donnés, on en séléctionne un qui ressemble à la version minimale que l'on veut implémenter et on extrait le xml embarqué.

https://communaute.chorus-pro.gouv.fr/documentation/exemples-de-flux/

Deux sources d'exemples, les flux en CII complets, mieux décrits : 

|FSO1116A_P01| Facture simple - Cas nominal avec uniquement les champs obligatoires et une ligne de facturation|
|FSO1116A_P02| Facture simple - Cas Nominal avec tous les champs obligatoires et facultatifs|
|FSO1116A_P20| Facture simple avec 3 taux de TVA, dont une ligne à 0|

Mon intuition est que la structure est la même pour le xml des deux flux E1 CII et E2 factur-x.
Idée : prendre le xml le plus simple tiré d'un flux factur-x et y ajouter les balises nécessaires pour ajouter toutes nos infos en duplicant la structure des CII complexes d'exemple


# Process 
Idée simple : on dispose d'un xml modèle, que l'on va venir peupler avec nos données
## Peupler le xml
Je vois deux facons
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

On le 
## Validation

On liste les xml d'un dossier, puis on les valide avec le XSD, si ça fonctionne on fait pareil avec le SCH


