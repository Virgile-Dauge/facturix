from pathlib import Path
from lxml import etree
from lxml import isoschematron
import logging

logger = logging.getLogger(__name__)

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

def main():
    # Exemple d'utilisation
    xml_directory = Path('sandbox/populated_xmls')
    schematron_file = Path('validators/FACTUR-X_MINIMUM_custom.sch')
    xsd_file = Path('validators/FACTUR-X_MINIMUM.xsd')  # Remplacer par le chemin réel du XSD

    # Valider tous les fichiers XML dans le répertoire
    for xml_file in xml_directory.glob('*.xml'):
        logger.info(f"Validation du fichier : {xml_file}")
        
        # Valider d'abord contre le schéma XSD
        if validate_xml_with_xsd(xml_file, xsd_file):
            # Si la validation XSD passe, procéder à la validation Schematron
            validate_xml_with_schematron(xml_file, schematron_file)

if __name__ == "__main__":
    main()
