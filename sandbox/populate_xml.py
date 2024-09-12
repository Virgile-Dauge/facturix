from lxml import etree

def generate_xml_from_template(template_path, replacements):
    # Charger le fichier XML en tant que modèle
    tree = etree.parse(template_path)
    root = tree.getroot()

    # Remplacer dynamiquement les valeurs
    for xpath, value in replacements.items():
        element = root.xpath(xpath, namespaces=root.nsmap)
        if element:
            element[0].text = value

    # Retourner le XML modifié sous forme de string
    return etree.tostring(root, pretty_print=True, encoding='utf-8').decode()

# Exemple d'utilisation
template_path = './minimal.xml'  # Le chemin de ton fichier XML
replacements = {
    "//ram:ID[.='NUMFACT']": "INV12345",
    "//ram:DateTimeString[.='AAAAMMJJ']": "20230912",
    "//ram:BuyerReference": "BR12345",
    "//ram:Name[.='SUPPLIERNAME']": "My Company",
    "//ram:TaxBasisTotalAmount": "500.00",
    "//ram:TaxTotalAmount": "100.00",
    "//ram:GrandTotalAmount": "600.00",
    "//ram:DuePayableAmount": "600.00"
}

modified_xml = generate_xml_from_template(template_path, replacements)
print(modified_xml)