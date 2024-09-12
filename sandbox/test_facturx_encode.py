from facturx import generate_from_file


# Chemin du fichier PDF d'origine (le fichier PDF à intégrer)
pdf_path = 'input.pdf'
xml_path = 'input.xml'

with open(xml_path, 'rb') as xml_file:
    xml_bytes = xml_file.read()
    # print(xml_bytes)

# Générer une facture Factur-X avec le fichier XML intégré dans le PDF
facturx_pdf = generate_from_file(
    pdf_path,  # Le PDF original à transformer en PDF/A-3
    xml_bytes,
    #facturx_level='EN16931',  # Niveau Factur-X (BASIC, EN16931, etc.)
    output_pdf_file='facture_facturx.pdf',  # Le fichier PDF/A-3 de sortie
)

print("Facture Factur-X générée avec succès !")