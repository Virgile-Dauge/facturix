# import xml.etree.ElementTree as ET

# # Définir les espaces de noms
# namespaces = {
#     'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
#     'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
#     'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100',
# }

# # Enregistrer les préfixes des espaces de noms
# for prefix, uri in namespaces.items():
#     ET.register_namespace(prefix, uri)
    
import xmlschema

# Load the XSD schema
schema = xmlschema.XMLSchema('doc_reference/format/FACTUR-X_EN16931.xsd')

# Generate XML structure based on XSD (empty or filled with defaults)
xml_data = schema.to_dict()

print(xml_data)
# Convert the dict to XML string
xml_string = schema.encode(xml_data)

# Save the XML to a file
with open('output.xml', 'w') as file:
    file.write(xml_string)

print("XML generated successfully!")