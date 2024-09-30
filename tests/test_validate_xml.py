import pytest
from pathlib import Path
from lxml import etree
from unittest.mock import mock_open, patch
import logging

from validate_xml import validate_xml_with_xsd  # Replace 'your_module' with the actual module name

@pytest.fixture
def valid_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <element>Test</element>
    </root>"""

@pytest.fixture
def invalid_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <invalid>Test</invalid>
    </root>"""

@pytest.fixture
def xsd_schema():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <xs:element name="root">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="element" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""

def test_validate_xml_with_xsd_valid(valid_xml, xsd_schema):
    with patch("builtins.open", mock_open(read_data=xsd_schema)) as mock_xsd_file, \
         patch("builtins.open", mock_open(read_data=valid_xml)) as mock_xml_file:
        
        result = validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))
        assert result == True

def test_validate_xml_with_xsd_invalid(invalid_xml, xsd_schema):
    with patch("builtins.open", mock_open(read_data=xsd_schema)) as mock_xsd_file, \
         patch("builtins.open", mock_open(read_data=invalid_xml)) as mock_xml_file, \
         patch("logging.error") as mock_logger:
        
        result = validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))
        assert result == False
        mock_logger.assert_called()

def test_validate_xml_with_xsd_file_not_found():
    with pytest.raises(FileNotFoundError):
        validate_xml_with_xsd(Path("nonexistent.xml"), Path("nonexistent.xsd"))

def test_validate_xml_with_xsd_invalid_xml():
    invalid_xml = "This is not XML"
    with patch("builtins.open", mock_open(read_data=invalid_xml)) as mock_file:
        with pytest.raises(etree.XMLSyntaxError):
            validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))

def test_validate_xml_with_xsd_invalid_xsd():
    invalid_xsd = "This is not XSD"
    with patch("builtins.open", mock_open(read_data=invalid_xsd)) as mock_file:
        with pytest.raises(etree.XMLSchemaParseError):
            validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))

@patch('logging.error')
def test_validate_xml_with_xsd_logging(mock_logger, invalid_xml, xsd_schema):
    with patch("builtins.open", mock_open(read_data=xsd_schema)) as mock_xsd_file, \
         patch("builtins.open", mock_open(read_data=invalid_xml)) as mock_xml_file:
        
        validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))
        assert mock_logger.call_count == 2

def test_validate_xml_with_xsd_empty_files():
    with patch("builtins.open", mock_open(read_data="")) as mock_file:
        with pytest.raises(etree.XMLSyntaxError):
            validate_xml_with_xsd(Path("empty.xml"), Path("empty.xsd"))

@pytest.mark.parametrize("xml_content,xsd_content,expected", [
    ("<?xml version='1.0'?><root></root>", "<?xml version='1.0'?><xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='root'/></xs:schema>", True),
    ("<?xml version='1.0'?><root><child/></root>", "<?xml version='1.0'?><xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'><xs:element name='root'/></xs:schema>", False),
])
def test_validate_xml_with_xsd_parametrized(xml_content, xsd_content, expected):
    with patch("builtins.open", mock_open(read_data=xsd_content)) as mock_xsd_file, \
         patch("builtins.open", mock_open(read_data=xml_content)) as mock_xml_file:
        
        result = validate_xml_with_xsd(Path("test.xml"), Path("test.xsd"))
        assert result == expected

