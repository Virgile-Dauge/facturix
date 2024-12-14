#!/usr/bin/env python
# import argparse
import pandas as pd
import pandas.testing as pdt
from lxml import isoschematron
from lxml import etree
from pandas import DataFrame
from pathlib import Path
from pkg_resources import resource_filename

from facturx import generate_from_file
import logging

SUPPORTED_LEVELS = {'MINIMUM'}
# Configurer le logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('factur-x').setLevel(logging.WARN)
logger = logging.getLogger(__name__)

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

def validate_xml_with_xsd(xml_file: Path, xsd_file: Path) -> bool:
    # Charger le XML et le XSD
    with open(xsd_file, 'r') as xsd_f:
        xsd_doc = etree.parse(xsd_f)
        xsd_schema = etree.XMLSchema(xsd_doc)

    with open(xml_file, 'r') as xml_f:
        xml_doc = etree.parse(xml_f)

    # Valider contre le XSD
    is_valid_xsd = xsd_schema.validate(xml_doc)
    
    if not is_valid_xsd:
        logger.error(f"Le fichier {xml_file} n'est pas valide selon le schéma XSD.")
        logger.error(xsd_schema.error_log)
    
    return is_valid_xsd

def validate_xml_with_schematron(xml_file: Path, schematron_file: Path) -> bool:
    # Charger le fichier XML
    with open(xml_file, 'r') as xml_f:
        xml_doc = etree.parse(xml_f)
    
    # Charger et compiler le fichier Schematron
    with open(schematron_file, 'r') as sch_f:
        schematron_doc = etree.parse(sch_f)
    
    # Créer une instance Schematron
    schematron = isoschematron.Schematron(schematron_doc)

    # Valider le fichier XML
    is_valid = schematron.validate(xml_doc)

    if not is_valid:
        logger.error(f"Le fichier {xml_file} n'est pas valide selon les règles du Schematron.")
        logger.error(f"Erreurs : {schematron.error_log}")
    
    return is_valid 

def validate_xml(xml_files: list[Path], schematron_file: Path=None, xsd_file: Path=None) -> list[Path]:
    """
    Generate and validate the XML files against XSD and Schematron.

    Parameters:
    - xml_files: xml files to validate
    - schematron_file: Path to the Schematron validation file
    - xsd_file: Path to the XSD validation file


    Returns:
    - invalid: List of invalid XML file paths
    """
    if schematron_file is None:
        schematron_file = Path(__file__).parent / 'validators/FACTUR-X_MINIMUM_custom.sch'
    if xsd_file is None:
        xsd_file = Path(__file__).parent / 'validators/FACTUR-X_MINIMUM.xsd'
    return [x for x in xml_files 
               if not (validate_xml_with_xsd(x, xsd_file) 
                       and validate_xml_with_schematron(x, schematron_file))]

# def make_or_get_linked_data(dir: Path, pdfs: list[Path], 
#                             input_csv: Path, 
#                             force_recalc: bool=False) -> DataFrame:
#     """
#     Crée ou récupère les données liées entre des fichiers PDF et un fichier CSV d'entrée.

#     Args:
#         dir (Path): Le répertoire de travail.
#         pdfs (list[Path]): Liste des chemins vers les fichiers PDF.
#         input_csv (Path): Chemin vers le fichier CSV d'entrée.
#         force_recalc (bool): Force le recalcul si True, même si le fichier de liens existe déjà.

#     Returns:
#         DataFrame: Une DataFrame fusionnée contenant les informations issues des PDF et du CSV d'entrée.
    
#     Raises:
#         ValueError: Si le fichier CSV d'entrée n'existe pas.
#     """
#     link_csv = dir / 'lien_pdf_factID.csv'
#     if not input_csv.exists():
#         raise ValueError(f"Le fichier CSV d'entrée {input_csv} n'existe pas.")

#     if force_recalc or not link_csv.exists():
#         # On extrait le num de facture pour chaque pdf
#         num_fact = [extraire_num_facture(f) for f in pdfs]
        
#         # On s'assure qu'on a bien récup tous les nums de facture
#         assert len(pdfs) == len([n for n in num_fact if n is not None])
        
#         # Créer une DataFrame avec les couples pdfs et num_fact
#         link_df = pd.DataFrame({
#             'pdf': pdfs,
#             'num_facture': num_fact
#         })
        
#         # Enregistrer la DataFrame dans un fichier CSV
#         link_df.to_csv(link_csv, index=False)
#         print(f"Les couples pdfs et num_fact ont été enregistrés dans {link_csv}")

#     # Chargement des fichiers
#     data_df = pd.read_csv(input_csv).replace('–', '-', regex=True)
#     link_df = pd.read_csv(link_csv)

#     # On ne garde que les colonnes BT
#     data_df = data_df.loc[:, data_df.columns.str.startswith('BT-')].dropna(subset=['BT-1'])

#     # Convertir les colonnes en chaînes de caractères avant la fusion
#     data_df['BT-1'] = data_df['BT-1'].astype(int).astype(str)
#     link_df['num_facture'] = link_df['num_facture'].astype(str)

#     # Fusionner les DataFrames df et link_df sur la colonne 'num_facture'
#     df = data_df.merge(link_df,
#                        left_on='BT-1',
#                        right_on='num_facture', 
#                        how='left').drop(columns=['num_facture'])
    
#     # Filter rows where PDF is not NaN and log warnings for NaN entries
#     nan_pdfs = df[df['pdf'].isna()]
#     if not nan_pdfs.empty:
#         logging.warning(f"Found {len(nan_pdfs)} rows with NaN PDF values:")
#         for index, row in nan_pdfs.iterrows():
#             logging.warning(f"Facture #{row['BT-1']}")

#     df = df.dropna(subset=['pdf'])
#     return df

def process_invoices(df: DataFrame, work_dir: Path, output_dir: Path, level: str='MINIMUM', conform_pdf: bool=True):
    """
    Process invoices by generating XMLs, validating them, and embedding them into PDFs.

    Args:
    df (pandas.DataFrame): DataFrame containing invoice data.
    input_dir (str or Path): Directory containing input PDF files.
    output_dir (str or Path): Directory to save output files.
    level (str): Factur-X level (e.g., 'MINIMUM', 'BASIC', 'EN16931', 'EXTENDED'). Only 'MINIMUM' is currently supported.

    Returns:
    list: List of invalid XML files, if any.

    Raises:
    ValueError: If the specified level is not supported.
    FileNotFoundError: If required files are not found.
    """
    # Check if the level is supported
    if level not in SUPPORTED_LEVELS:
        raise ValueError(f"Unsupported Factur-X level: {level}. Supported levels are: {', '.join(SUPPORTED_LEVELS)}")
    
    # Convert to Path objects if they're not already
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    icc_profile = resource_filename('facturix', 'color_profiles/sRGB_ICC_v4_Appearance.icc')
    if conform_pdf:
        # to_convert = [Path(f) for f in df['pdf'] if pd.notna(f) and f]
        # process_pdfs_with_progress(to_convert, work_dir, icc_profile)
        # # Update the 'pdf' column with the new path while keeping the original filename
        # df['pdf'] = df['pdf'].apply(lambda x: str(work_dir / Path(x).name) if pd.notna(x) and x else x)
        # df = df.dropna(subset=['pdf'])
        ...
    xml_template = resource_filename('facturix', f'templates/template_{level}.xml')
    logger.info(f"Using template : {xml_template}")
    if Path(xml_template).is_file() is False:
        #raise FileNotFoundError(f"The XML template for Factur-X level {level} could not be found.")
        logger.error(f"The following XML files are not found: {xml_template}")
    # Step 1: Generate XMLs
    to_embed = gen_xmls(df, work_dir, xml_template)
    
    # Step 2: Validate generated XMLs
    schematron_file = resource_filename('facturix', f'validators/FACTUR-X_{level}.sch')
    xsd_file = resource_filename('facturix', f'validators/FACTUR-X_{level}.xsd')
    produced_xml = work_dir.glob('*.xml')
    
    invalid = validate_xml(produced_xml, schematron_file, xsd_file)

    if invalid:
        logger.error(f"The following XML files are not valid: {invalid}")
    
    # Step 3: Integrate XMLs into PDFs
    for pdf_file, xml_file in to_embed:
        with open(xml_file, 'rb') as xml_file:
            xml_bytes = xml_file.read()

        output_file = output_dir / pdf_file.name
        logger.debug(f"Processing file {pdf_file}.")
        # Generate a Factur-X invoice with the XML file embedded in the PDF
        generate_from_file(
            pdf_file,  # The original PDF to transform into PDF/A-3
            xml_bytes,
            output_pdf_file=str(output_file),  # The output PDF/A-3 file
            flavor=f'factur-x_{level.lower()}'
        )
    
    return invalid

def main():
    ...
    # # ==== Étape 0 : Récup args et setup arborescence ====
    # parser = argparse.ArgumentParser(description="Lister les fichiers PDF dans un dossier de données.")
    # parser.add_argument('-i', '--input_dir', required=True, type=str, help='Le dossier contenant les fichiers PDF des factures.')
    # parser.add_argument('-c', '--input_csv', required=True, type=str, help='Le fichier contenant les données des factures.')
    # parser.add_argument('-o', '--output_dir', required=True, type=str, help='Le dossier où enregistrer les fichiers de sortie.')
    # parser.add_argument('-b', '--batch_name', required=True, type=str, help='Le nom du lot de traitement.')
    # parser.add_argument('-fr', '--force_recalc', action='store_true', help='Forcer le recalcul du CSV de lien facture-fichier.')
    # parser.add_argument('-fp', '--force_pdfa3', action='store_true', help='Forcer le reprocess des pdf vers pdf/A-3.')
    # parser.add_argument('-v', '--verbose', action='count', default=0, help='Augmenter le niveau de verbosité (peut être utilisé jusqu\'à 2 fois).')
    # args = parser.parse_args()

    # # Configurer le niveau de log en fonction de l'option -v
    # if args.verbose == 1:
    #     logging.getLogger().setLevel(logging.DEBUG)
    # elif args.verbose >= 2:
    #     logging.getLogger().setLevel(logging.NOTSET)

    # args = parser.parse_args()

    # # Prep Arboresence
    # input_dir = Path(args.input_dir).expanduser()
    
    # if not input_dir.exists():
    #     print(f'{input_dir} does not exists, exiting.')
    #     exit(1)

    # input_csv = Path(args.input_csv)
    
    # if not input_csv.exists():
    #     print(f'{input_csv} does not exists, exiting.')
    #     exit(1)
        
    # output_dir = Path(args.output_dir)
    # output_dir.mkdir(exist_ok=True, parents=True)        
    

    # # ==== Étape 1 : Lister les fichiers PDF d'entrée ============
    
    # pdfa3_dir = output_dir / 'pdfa3'

    # if not pdfa3_dir.exists() or args.force_pdfa3:
    #     pdfa3_dir.mkdir(parents=True, exist_ok=True)

    #     pdfs = [f for f in input_dir.glob('*.pdf')]
    #     # Transformer les fichiers PDF en PDF/A-3
    #     original_pdfs = [f for f in input_dir.glob('*.pdf')]
    #     process_pdfs_with_progress(original_pdfs, pdfa3_dir, 'sRGB_ICC_v4_Appearance.icc')
    
    # # Lister les nouveaux fichiers PDF/A-3
    # pdfs = [f for f in pdfa3_dir.glob('*.pdf')]
    # print(f'Found {len(pdfs)} PDF files in {pdfa3_dir}')
    
    # # ==== Étape 2 : Faire le lien données - pdf =================
    # df = make_or_get_linked_data(pdfa3_dir, pdfs, 
    #                              Path(args.input_csv), 
    #                              args.force_recalc)
    # print(df)
    
    # # ==== Étape 3 : Generation des XML CII ======================
    # xml_template = Path('templates/minimum_template_without_bt31_bt13.xml')  # Chemin vers le modèle XML
    # to_embed = gen_xmls(df, output_dir, xml_template)
    
    # # ==== Étape 4 : Validation des XMLs générés =================
    # schematron_file = Path('validators/FACTUR-X_MINIMUM_custom.sch')
    # xsd_file = Path('validators/FACTUR-X_MINIMUM.xsd')  # Remplacer par le chemin réel du XSD
    # produced_xml = output_dir.glob('*.xml')
    
    # invalid = validate_xml(produced_xml, schematron_file, xsd_file)

    # if invalid:
    #     logger.error(f"Les fichiers XML suivants ne sont pas valides : {invalid}")
    
    # # ==== Étape 5 : Intégration des xml dans les pdfs ===========
    # for p, x in to_embed:
        
    #     with open(x, 'rb') as xml_file:
    #         xml_bytes = xml_file.read()

    #     output_file = output_dir / p.name
    #     # Générer une facture Factur-X avec le fichier XML intégré dans le PDF
    #     facturx_pdf = generate_from_file(
    #         p,  # Le PDF original à transformer en PDF/A-3
    #         xml_bytes,
    #         output_pdf_file=str(output_file),  # Le fichier PDF/A-3 de sortie
    #     )

    # # # ==== Étape 6 : Création des archives zip ====================
    # # zip_dir = output_dir / 'zipped'
    # # create_zip_batches(list(output_dir.glob('*.pdf')), zip_dir, 
    # #                    max_files=500, max_size_mo=500,
    # #                    name=args.batch_name)

if __name__ == "__main__":
    main()