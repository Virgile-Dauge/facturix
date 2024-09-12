from lxml import etree
from lxml import isoschematron

def validate_xml_with_xsd(xml_file, xsd_file):
    # Load the XML and XSD
    with open(xsd_file, 'r') as xsd_f:
        xsd_doc = etree.parse(xsd_f)
        xsd_schema = etree.XMLSchema(xsd_doc)

    with open(xml_file, 'r') as xml_f:
        xml_doc = etree.parse(xml_f)

    # Validate against the XSD
    is_valid_xsd = xsd_schema.validate(xml_doc)
    
    if is_valid_xsd:
        print("Le fichier XML est valide selon le schéma XSD.")
    else:
        print("Le fichier XML n'est pas valide selon le schéma XSD.")
        print(xsd_schema.error_log)
    
    return is_valid_xsd

def validate_xml_with_schematron(xml_file, schematron_file):
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

    if is_valid:
        print("Le fichier XML est valide selon les règles du Schematron.")
    else:
        print("Le fichier XML n'est pas valide selon les règles du Schematron.")
        print("Erreurs :", schematron.error_log)

from pathlib import Path

# Exemple d'utilisation
xml_directory = Path('sandbox/populated_xmls')
schematron_file = Path('validators/FACTUR-X_MINIMUM_custom.sch')
xsd_file = Path('validators/FACTUR-X_MINIMUM.xsd')  # Remplacer par le chemin réel du XSD

# Valider tous les fichiers XML dans le répertoire
for xml_file in xml_directory.glob('*.xml'):
    print(f"Validation du fichier : {xml_file}")
    
    # Valider d'abord contre le schéma XSD
    if validate_xml_with_xsd(xml_file, xsd_file):
        # Si la validation XSD passe, procéder à la validation Schematron
        validate_xml_with_schematron(xml_file, schematron_file)
