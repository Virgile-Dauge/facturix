#!/usr/bin/env python
import argparse
import pandas as pd
import pandas.testing as pdt

from pandas import DataFrame
from pathlib import Path

from facturx import generate_from_file

from to_pdfa3 import process_pdfs_with_progress
from extract_from_pdf import extraire_num_facture
from populate_xml import gen_xmls
from validate_xml import validate_xml
from zipper import create_zip_batches

import logging

# Configurer le logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('factur-x').setLevel(logging.WARN)


logger = logging.getLogger(__name__)

def make_or_get_linked_data(dir: Path, pdfs: list[Path], 
                            input_csv: Path, 
                            force_recalc: bool=False) -> DataFrame:
    """
    Crée ou récupère les données liées entre des fichiers PDF et un fichier CSV d'entrée.

    Args:
        dir (Path): Le répertoire de travail.
        pdfs (list[Path]): Liste des chemins vers les fichiers PDF.
        input_csv (Path): Chemin vers le fichier CSV d'entrée.
        force_recalc (bool): Force le recalcul si True, même si le fichier de liens existe déjà.

    Returns:
        DataFrame: Une DataFrame fusionnée contenant les informations issues des PDF et du CSV d'entrée.
    
    Raises:
        ValueError: Si le fichier CSV d'entrée n'existe pas.
    """
    link_csv = dir / 'lien_pdf_factID.csv'
    if not input_csv.exists():
        raise ValueError(f"Le fichier CSV d'entrée {input_csv} n'existe pas.")

    if force_recalc or not link_csv.exists():
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

    # Chargement des fichiers
    data_df = pd.read_csv(input_csv).replace('–', '-', regex=True)
    link_df = pd.read_csv(link_csv)

    # On ne garde que les colonnes BT
    data_df = data_df.loc[:, data_df.columns.str.startswith('BT-')].dropna(subset=['BT-1'])

    # Convertir les colonnes en chaînes de caractères avant la fusion
    data_df['BT-1'] = data_df['BT-1'].astype(int).astype(str)
    link_df['num_facture'] = link_df['num_facture'].astype(str)

    # Fusionner les DataFrames df et link_df sur la colonne 'num_facture'
    df = data_df.merge(link_df,
                       left_on='BT-1',
                       right_on='num_facture', 
                       how='left').drop(columns=['num_facture'])
    
    # Filter rows where PDF is not NaN and log warnings for NaN entries
    nan_pdfs = df[df['pdf'].isna()]
    if not nan_pdfs.empty:
        logging.warning(f"Found {len(nan_pdfs)} rows with NaN PDF values:")
        for index, row in nan_pdfs.iterrows():
            logging.warning(f"Facture #{row['BT-1']}")

    df = df.dropna(subset=['pdf'])
    return df

def main():

    # ==== Étape 0 : Récup args et setup arborescence ====
    parser = argparse.ArgumentParser(description="Lister les fichiers PDF dans un dossier de données.")
    parser.add_argument('-i', '--input_dir', required=True, type=str, help='Le dossier contenant les fichiers PDF des factures.')
    parser.add_argument('-c', '--input_csv', required=True, type=str, help='Le fichier contenant les données des factures.')
    parser.add_argument('-o', '--output_dir', required=True, type=str, help='Le dossier où enregistrer les fichiers de sortie.')
    parser.add_argument('-b', '--batch_name', required=True, type=str, help='Le nom du lot de traitement.')
    parser.add_argument('-fr', '--force_recalc', action='store_true', help='Forcer le recalcul du CSV de lien facture-fichier.')
    parser.add_argument('-fp', '--force_pdfa3', action='store_true', help='Forcer le reprocess des pdf vers pdf/A-3.')
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
    

    # ==== Étape 1 : Lister les fichiers PDF d'entrée ============
    
    pdfa3_dir = output_dir / 'pdfa3'

    if not pdfa3_dir.exists() or args.force_pdfa3:
        pdfa3_dir.mkdir(parents=True, exist_ok=True)

        pdfs = [f for f in input_dir.glob('*.pdf')]
        # Transformer les fichiers PDF en PDF/A-3
        original_pdfs = [f for f in input_dir.glob('*.pdf')]
        process_pdfs_with_progress(original_pdfs, pdfa3_dir, 'sRGB_ICC_v4_Appearance.icc')
    
    # Lister les nouveaux fichiers PDF/A-3
    pdfs = [f for f in pdfa3_dir.glob('*.pdf')]
    print(f'Found {len(pdfs)} PDF files in {pdfa3_dir}')
    
    # ==== Étape 2 : Faire le lien données - pdf =================
    df = make_or_get_linked_data(pdfa3_dir, pdfs, 
                                 Path(args.input_csv), 
                                 args.force_recalc)
    print(df)
    
    # ==== Étape 3 : Generation des XML CII ======================
    xml_template = Path('templates/minimum_template_without_bt31_bt13.xml')  # Chemin vers le modèle XML
    to_embed = gen_xmls(df, output_dir, xml_template)
    
    # ==== Étape 4 : Validation des XMLs générés =================
    schematron_file = Path('validators/FACTUR-X_MINIMUM_custom.sch')
    xsd_file = Path('validators/FACTUR-X_MINIMUM.xsd')  # Remplacer par le chemin réel du XSD
    produced_xml = output_dir.glob('*.xml')
    
    invalid = validate_xml(produced_xml, schematron_file, xsd_file)

    if invalid:
        logger.error(f"Les fichiers XML suivants ne sont pas valides : {invalid}")
    
    # ==== Étape 5 : Intégration des xml dans les pdfs ===========
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

    # ==== Étape 6 : Création des archives zip ====================
    zip_dir = output_dir / 'zipped'
    create_zip_batches(list(output_dir.glob('*.pdf')), zip_dir, 
                       max_files=500, max_size_mo=500,
                       name=args.batch_name)

if __name__ == "__main__":
    main()