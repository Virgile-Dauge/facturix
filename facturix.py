#!/usr/bin/env python
import argparse
import pandas as pd
import pandas.testing as pdt

from pathlib import Path
from facturx import generate_from_file

from extract_from_pdf import extraire_num_facture
from populate_xml import gen_xmls
from validate_xml import validate_xml_with_xsd, validate_xml_with_schematron
from zipper import create_zip_batches

import logging

# Configurer le logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('factur-x').setLevel(logging.WARN)


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Lister les fichiers PDF dans un dossier de données.")
    parser.add_argument('-i', '--input_dir', required=True, type=str, help='Le dossier contenant les fichiers PDF des factures.')
    parser.add_argument('-c', '--input_csv', required=True, type=str, help='Le fichier contenant les données des factures.')
    parser.add_argument('-o', '--output_dir', required=True, type=str, help='Le dossier où enregistrer les fichiers de sortie.')
    parser.add_argument('-f', '--force_recalc', action='store_true', help='Forcer le recalcul du CSV de lien facture-fichier.')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Augmenter le niveau de verbosité (peut être utilisé jusqu\'à 2 fois).')
    args = parser.parse_args()

    # Configurer le niveau de log en fonction de l'option -v
    if args.verbose == 1:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose >= 2:
        logging.getLogger().setLevel(logging.NOTSET)

    args = parser.parse_args()

    # Prep Arboresence
    input_dir = Path(args.input_dir).expanduser()
    
    if not input_dir.exists():
        print(f'{input_dir} does not exists, exiting.')
        exit(1)

    input_csv = Path(args.input_csv)
    
    if not input_csv.exists():
        print(f'{input_csv} does not exists, exiting.')
        exit(1)
        
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)        
    
    # On liste les PDF d'entrée
    pdfs = [f for f in input_dir.rglob('*.pdf')]
    
    link_csv = output_dir / 'lien_pdf_factID.csv'
    
    if args.force_recalc or not link_csv.exists():
        # On extrait le num de facture pour chaque pdf
        num_fact = [extraire_num_facture(f) for f in pdfs]
        
        # On s'assure qu'on a bien récup tous les nums de facture
        assert len(pdfs) == len([n for n in num_fact if n is not None])
        
        # Créer une DataFrame avec les couples pdfs et num_fact
        link_df = pd.DataFrame({
            'pdf': pdfs,
            'num_facture': num_fact
        })
        
        # Enregistrer la DataFrame dans un fichier CSV
        link_df.to_csv(link_csv, index=False)
        print(f"Les couples pdfs et num_fact ont été enregistrés dans {link_csv}")

    # Charger le fichier CSV
    link_df = pd.read_csv(link_csv)
    print(f"Le fichier {link_csv} a été chargé.")

    # On charge le fichier de données
    df = pd.read_csv(args.input_csv)
    
    # Convertir les colonnes en chaînes de caractères avant la fusion
    df['BT-1'] = df['BT-1'].astype(str)
    link_df['num_facture'] = link_df['num_facture'].astype(str)
    # Fusionner les DataFrames df et link_df sur la colonne 'num_facture'
    df_merged = df.merge(link_df, left_on='BT-1', right_on='num_facture', how='left').drop(columns=['num_facture'])

    # Afficher les premières lignes du DataFrame fusionné pour vérification
    # print(df_merged.head())

    # Validation des XMLs générés
    xml_template = Path('templates/minimum_template.xml')  # Chemin vers le modèle XML
    to_embed = gen_xmls(df_merged, xml_template, output_dir)
    
    schematron_file = Path('validators/FACTUR-X_MINIMUM_custom.sch')
    xsd_file = Path('validators/FACTUR-X_MINIMUM.xsd')  # Remplacer par le chemin réel du XSD

    produced_xml = output_dir.glob('*.xml')
    
    invalid = [x for x in produced_xml if not (validate_xml_with_xsd(x, xsd_file) and validate_xml_with_schematron(x, schematron_file))]

    if invalid:
        logger.error(f"Les fichiers XML suivants ne sont pas valides : {invalid}")
    
    # Embed XMLs in PDFs
    for p, x in to_embed:
        
        with open(x, 'rb') as xml_file:
            xml_bytes = xml_file.read()

        output_file = output_dir / p.name
        # Générer une facture Factur-X avec le fichier XML intégré dans le PDF
        facturx_pdf = generate_from_file(
            p,  # Le PDF original à transformer en PDF/A-3
            xml_bytes,
            output_pdf_file=str(output_file),  # Le fichier PDF/A-3 de sortie
        )

    # Zipping files 
    zip_dir = output_dir / 'zipped'
    create_zip_batches(list(output_dir.glob('*.pdf')), zip_dir, max_files=500, max_size_mo=20)

if __name__ == "__main__":
    main()

