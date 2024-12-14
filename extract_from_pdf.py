import re
import time

# import pdfplumber
from pathlib import Path
from pypdf import PdfReader

def extraire_num_facture(pdf_path: Path, pattern: str=r'N° de facture\s*:\s*(\d{14})') -> str | None:
    """
    Extrait le numéro de facture d'un fichier PDF spécifié.

    Args:
        pdf_path (Path): Le chemin vers le fichier PDF.
        pattern (str): L'expression régulière pour capturer le numéro de facture.

    Returns:
        str | None: Le numéro de facture si trouvé, sinon None.
    """
    # Ouvrir le fichier PDF avec PyPDF
    reader = PdfReader(pdf_path)

    # Extraire le texte de la première page
    texte_premiere_page = reader.pages[0].extract_text()
    
    # Utiliser l'expression régulière passée en argument pour capturer le numéro de facture
    match = re.search(pattern, texte_premiere_page)
    
    if match:
        return match.group(1)  # Retourner le numéro de facture

    return None

# def extraire_num_facture_detail(pdf_path):
#     # Ouvrir le PDF
#     with pdfplumber.open(pdf_path) as pdf:
#         # Lire la première page
#         texte_complet = pdf.pages[0].extract_text() if pdf.pages else ''
#         # for page in pdf.pages:
#         #     texte_complet += page.extract_text()

#         # Expression régulière pour capturer le numéro de facture
#         pattern = r'N° de facture\s*:\s*(\d{14})'
#         match = re.search(pattern, texte_complet)

#         if match:
#             return match.group(1)
#         else:
#             return "Numéro de facture non trouvé."

def main():
    import argparse
    import pandas as pd
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Extract invoice numbers from PDF files.")
    parser.add_argument('-i', "--input_dir", required=True, type=str, help="Directory containing PDF files")
    parser.add_argument('-o', "--output_dir", required=True, type=str, help="Directory to save the output CSV file")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    start_time = time.time()

    results = [
        {'filename': pdf_file.name, 'invoice_number': extraire_num_facture(pdf_file)}
        for pdf_file in input_dir.rglob('*.pdf')
    ]


    df = pd.DataFrame(results)
    
    print(f"Processing completed in {time.time() - start_time:.2f} seconds")
    print(df)

    print(list(input_dir.rglob('*.pdf')))

    # Optionally, save the DataFrame to a CSV file
    df.to_csv(output_dir / 'invoice_numbers.csv', index=False)


if __name__ == "__main__":
    main()
