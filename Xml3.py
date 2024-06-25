from lxml import etree

def get_nested_element_text(xml_content, path):
    """
    Parses an XML document and retrieves the text of a nested element.
    
    Args:
        xml_content (str): The XML content as a string.
        path (str): The XPath to the nested element.

    Returns:
        str: The text content of the nested element, or None if the element is not found.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.XML(xml_content, parser)
    element = tree.xpath(path)
    
    if element and len(element) > 0:
        return element[0].text
    else:
        return None

if __name__ == "__main__":
    xml_content = """
    <root>
        <level1>
            <level2>
                <level3>Some nested text</level3>
            </level2>
        </level1>
    </root>
    """
    path = "/root/level1/level2/level3"
    nested_text = get_nested_element_text(xml_content, path)
    print(f"The nested text is: {nested_text}")
