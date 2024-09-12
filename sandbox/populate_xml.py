import pandas as pd
from lxml import etree
from pathlib import Path
# Fonction pour remplacer les placeholders dans le modèle XML
def populate_xml(xml_file, output_file, placeholders):
    # Parse le fichier XML (modèle)
    tree = etree.parse(xml_file)
    
    # Convertit l'arbre XML en chaîne pour faire un remplacement de texte
    xml_str = etree.tostring(tree, pretty_print=True, encoding='unicode')
    
    # Remplace les placeholders par des valeurs réelles
    for placeholder, value in placeholders.items():
        xml_str = xml_str.replace(placeholder, value)
    
    # Enregistre le fichier XML modifié dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"XML modifié enregistré dans {output_file}")

# Fonction pour lire le CSV et générer plusieurs fichiers XML
def populate_xmls_from_csv(csv_file: Path, xml_template: Path, output_dir: Path):
    # Lire le fichier CSV
    df = pd.read_csv(csv_file)
    output_dir.mkdir(exist_ok=True)
    # Parcourir chaque ligne du dataframe
    for index, row in df.iterrows():
        # Créer un dictionnaire de placeholders à partir de la ligne
        placeholders = {"{{"+str(col)+"}}": str(row[col]) for col in df.columns}
        
        # Définir le nom de fichier de sortie
        output_file = f"{output_dir}/populated_{index+1}.xml"
        
        # Appeler la fonction pour générer le XML avec les valeurs de cette ligne
        populate_xml(xml_template, output_file, placeholders)

# Exemple d'utilisation
csv_file = Path('sandbox/random_data.csv')  # Chemin vers ton fichier CSV
xml_template = Path('sandbox/minimum_template.xml')  # Chemin vers le modèle XML
output_dir = Path('sandbox/populated_xmls')  # Dossier où enregistrer les fichiers XML générés

# Générer les fichiers XML à partir du CSV
populate_xmls_from_csv(csv_file, xml_template, output_dir)
