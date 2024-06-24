import paramiko
import xml.etree.ElementTree as ET
import io

def ssh_replace_nested_xml_content(hostname, port, username, password, file_path, parent_tag, parent_attr, nested_tag, nested_attr, new_content):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote server
        ssh.connect(hostname, port, username, password)

        # Read the XML file from the remote server
        sftp = ssh.open_sftp()
        file = sftp.file(file_path, mode='r')
        xml_content = file.read()
        file.close()

        # Parse the XML content
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        # Find the parent tag with the specified attribute
        parent = None
        for elem in root.findall(f".//{parent_tag}"):
            if elem.attrib.get(parent_attr[0]) == parent_attr[1]:
                parent = elem
                break

        if parent is None:
            print(f"Error: Parent tag '{parent_tag}' with attribute '{parent_attr}' not found.")
            return

        # Find the nested tag with the specified attribute
        nested = None
        for elem in parent.findall(f".//{nested_tag}"):
            if elem.attrib.get(nested_attr[0]) == nested_attr[1]:
                nested = elem
                break

        if nested is None:
            print(f"Error: Nested tag '{nested_tag}' with attribute '{nested_attr}' not found.")
            return

        # Replace the content of the nested tag
        nested.text = new_content

        # Write the modified XML content back to the remote file
        new_xml_content = io.BytesIO()
        tree.write(new_xml_content, encoding='utf-8', xml_declaration=True)
        new_xml_content.seek(0)

        file = sftp.file(file_path, mode='w')
        file.write(new_xml_content.read())
        file.close()

        # Close the SFTP and SSH connections
        sftp.close()
        ssh.close()

        print(f"Content of tag '{nested_tag}' with attribute '{nested_attr}' updated successfully in '{file_path}' on '{hostname}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Usage example
hostname = "remote.server.com"
port = 22
username = "your_username"
password = "your_password"
file_path = "/path/to/your/file.xml"
parent_tag = "x"
parent_attr = ("y", "z")  # Attribute name and value pair
nested_tag = "a"
nested_attr = ("b", "c")  # Attribute name and value pair
new_content = "new content for the nested tag"

ssh_replace_nested_xml_content(hostname, port, username, password, file_path, parent_tag, parent_attr, nested_tag, nested_attr, new_content)
