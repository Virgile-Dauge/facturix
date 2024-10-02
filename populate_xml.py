import pandas as pd
from pandas import DataFrame
from lxml import etree
from pathlib import Path

# Fonction pour remplacer les placeholders dans le modèle XML
def populate_xml(xml_file, output_file, placeholders, optionnal = ['BT-10', 'BT-13', 'BT-31']):
    # Parse le fichier XML (modèle)
    tree = etree.parse(xml_file)
    
    # Convertit l'arbre XML en chaîne pour faire un remplacement de texte
    xml_str = etree.tostring(tree, pretty_print=True, encoding='unicode')
    
    # filtre valeurs vides :
    placeholders = {k: str(v) for k, v in placeholders.items() if v != ''}
    for k in optionnal:
        if '{{'+k+'}}' in placeholders:
            xml_str = xml_str.replace(f'<!--{k}', '').replace(f'{k}-->', '')
    
    # Remplace les placeholders par des valeurs réelles
    for placeholder, value in placeholders.items():
        xml_str = xml_str.replace(placeholder, value)
    
    # Enregistre le fichier XML modifié dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)

# Fonction pour lire le CSV et générer plusieurs fichiers XML
def populate_xmls_from_csv(csv_file: Path, output_dir: Path, xml_template: Path=Path('templates/minimum_template_modular.xml')):
    # Lire le fichier CSV
    df = pd.read_csv(csv_file)
    output_dir.mkdir(exist_ok=True)
    # Parcourir chaque ligne du dataframe
    for index, row in df.iterrows():
        # Créer un dictionnaire de placeholders à partir de la ligne
        placeholders = {"{{"+str(col)+"}}": str(row[col]) for col in df.columns if col.startswith('BT')}
        
        # Définir le nom de fichier de sortie
        output_file = output_dir / (Path(row['pdf']).stem + '.xml')
        
        # Appeler la fonction pour générer le XML avec les valeurs de cette ligne
        populate_xml(xml_template, output_file, placeholders)


def gen_xmls(df: DataFrame, output_dir: Path, xml_template: Path=None) -> list[tuple[Path, Path]]:
    if xml_template is None:
        script_dir = Path(__file__).parent
        xml_template = script_dir / 'templates/minimum_template_modular.xml'
    
    files: list[tuple[Path, Path]] = []
    output_dir.mkdir(exist_ok=True)
    df_completed = df.copy().dropna(subset=['pdf', 'BT-1'])
    # Parcourir chaque ligne du dataframe
    for index, row in df_completed.iterrows():
        # Créer un dictionnaire de placeholders à partir de la ligne
        placeholders = {"{{"+str(col)+"}}": str(row[col]) for col in df.columns if col.startswith('BT') and not pd.isna(row[col])}

        # Définir le nom de fichier de sortie
        input_file = Path(row['pdf'])
        output_file = output_dir / (input_file.stem + '.xml')
        
        # Appeler la fonction pour générer le XML avec les valeurs de cette ligne
        populate_xml(xml_template, output_file, placeholders)
        files += [(input_file, output_file)]

    return files

def main():
    # Exemple d'utilisation
    csv_file = Path('sandbox/random_data.csv')  # Chemin vers ton fichier CSV
    xml_template = Path('sandbox/minimum_template.xml')  # Chemin vers le modèle XML
    output_dir = Path('sandbox/populated_xmls')  # Dossier où enregistrer les fichiers XML générés

    # Générer les fichiers XML à partir du CSV
    populate_xmls_from_csv(csv_file, output_dir, xml_template)

if __name__ == "__main__":
    main()
