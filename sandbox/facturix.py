#!/usr/bin/env python
import argparse
import pandas as pd

from pathlib import Path
from facturx import generate_from_file

from extract_from_pdf import extraire_num_facture
from populate_xml import gen_xmls

def main():
    parser = argparse.ArgumentParser(description="Lister les fichiers PDF dans un dossier de données.")
    parser.add_argument('-i', '--input_dir', type=str, help='Le dossier contenant les fichiers PDF des factures.')
    parser.add_argument('-c', '--input_csv', type=str, help='Le fichier contenant les données des factures.')
    parser.add_argument('-o', '--output_dir', type=str, help='Le dossier où enregistrer les fichiers de sortie.')
    parser.add_argument('-f', '--force_recalc', action='store_true', help='Forcer le recalcul du CSV de lien facture-fichier.')
    args = parser.parse_args()

    # Prep Arboresence
    input_dir = Path(args.input_dir)
    
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
        print(num_fact)
        
        # Créer une DataFrame avec les couples pdfs et num_fact
        link_df = pd.DataFrame({
            'pdf': [str(f) for f in pdfs],
            'num_facture': num_fact
        })
        
        # Enregistrer la DataFrame dans un fichier CSV
        link_df.to_csv(link_csv, index=False)
        
        print(f"Les couples pdfs et num_fact ont été enregistrés dans {link_csv}")
    else:
        # Charger le fichier CSV existant
        link_df = pd.read_csv(link_csv)
        print(f"Le fichier {link_csv} a été chargé.")
    
    # On charge le fichier de données
    df = pd.read_csv(args.input_csv)
    print(df.head())
    
    # Convertir les colonnes en chaînes de caractères avant la fusion
    df['BT-1'] = df['BT-1'].astype(str)
    link_df['num_facture'] = link_df['num_facture'].astype(str)
    # Fusionner les DataFrames df et link_df sur la colonne 'num_facture'
    df_merged = df.merge(link_df[['pdf']], left_on='BT-1', right_on=link_df['num_facture'], how='left')

    # Afficher les premières lignes du DataFrame fusionné pour vérification
    print(df_merged.head())

    xml_template = Path('sandbox/minimum_template.xml')  # Chemin vers le modèle XML
    to_embed = gen_xmls(df_merged, xml_template, output_dir)
    print(to_embed)
    
    for p, x in to_embed:
        
        with open(x, 'rb') as xml_file:
            xml_bytes = xml_file.read()

        output_file = output_dir / p.name
        # Générer une facture Factur-X avec le fichier XML intégré dans le PDF
        facturx_pdf = generate_from_file(
            p,  # Le PDF original à transformer en PDF/A-3
            xml_bytes,
            #facturx_level='MINIMUM',  # Niveau Factur-X (BASIC, EN16931, etc.)
            output_pdf_file=str(output_file),  # Le fichier PDF/A-3 de sortie
        )


if __name__ == "__main__":
    main()

