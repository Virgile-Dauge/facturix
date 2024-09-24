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
    # Exemple d'utilisation
    pdf_path = Path("~/data/enargia/batch_1/output/results/20240904-CAPB-CAPB - ASST S2.pdf").expanduser()

    # start_time = time.time()
    # numero_facture = extraire_num_facture_detail(pdf_path)

    # end_time = time.time()

    # # Calcul du temps d'exécution
    # execution_time = end_time - start_time
    # print(f"Temps d'exécution extraire_num_facture_detail : {execution_time:.4f} secondes")
    # print(f"Le numéro de facture est : {numero_facture}")

    start_time = time.time()
    numero_facture = extraire_num_facture(pdf_path)

    end_time = time.time()

    # Calcul du temps d'exécution
    execution_time = end_time - start_time
    print(f"Temps d'exécution extraire_num_facture : {execution_time:.4f} secondes")
    print(f"Le numéro de facture est : {numero_facture}")

if __name__ == "__main__":
    main()
