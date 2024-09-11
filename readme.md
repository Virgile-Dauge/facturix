# Ce que l'on sait  

## Process

### Entrées 

- Un dossier `data_dir/input/` contenant des pdfs de factures.
- Un csv `data_dir/factur_data.csv` contant des infos sur les factures à traiter

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




