from lxml import etree

def update_nested_element(xml_content, level1_id=None, new_x_value=None, level_id=None, level_x_value=None, new_text=None):
    """
    Updates specific elements in the XML content based on given criteria.

    Args:
        xml_content (str): The XML content as a string.
        level1_id (int, optional): The id attribute value for <level1> element to search for.
        new_x_value (int, optional): The new value for the x attribute in the found <level69> element.
        level_id (int, optional): The id attribute value for an element to search for.
        level_x_value (int, optional): The x attribute value for the <level69> element to search for.
        new_text (str, optional): The new text content for the found <level69> element.

    Returns:
        str: The updated XML content as a string.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.XML(xml_content, parser)

    # Update the x attribute in <level69> element where <level1> has id=level1_id
    if level1_id is not None and new_x_value is not None:
        level1_element = tree.xpath(f"//level1[@id='{level1_id}']")
        if level1_element:
            level69_element = level1_element[0].find("level69")
            if level69_element is not None:
                level69_element.set("x", str(new_x_value))

    # Update the text content of <level69> element where id=level_id and x=level_x_value
    if level_id is not None and level_x_value is not None and new_text is not None:
        level69_elements = tree.xpath(f"//level1[@id='{level_id}']/level69[@x='{level_x_value}']")
        for element in level69_elements:
            element.text = new_text

    return etree.tostring(tree, pretty_print=True, encoding="unicode")

if __name__ == "__main__":
    xml_content = """
    <root>
        <level1>
            <level2>
                <level3>Some nested text</level3>
            </level2>
        </level1>
        <level1 id="10">
            <level69 x="7"> y </level69>
        </level1>
    </root>
    """

    # Update <level69 x=7> inside <level1 id=10> to have x=9
    updated_xml = update_nested_element(xml_content, level1_id=10, new_x_value=9)
    print("Updated XML after first change:\n", updated_xml)

    # Update <level69 x=7> to have text "M" inside <level1 id=10>
    updated_xml = update_nested_element(xml_content, level_id=10, level_x_value=7, new_text="M")
    print("Updated XML after second change:\n", updated_xml)
