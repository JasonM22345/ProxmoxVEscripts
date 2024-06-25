import paramiko
import xml.etree.ElementTree as ET
from io import StringIO

def ssh_command(hostname, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    ssh.close()
    if error:
        raise Exception(f"Error executing command: {error}")
    return output

def edit_vm_xml(xml_content, vram=None, cpus=None, network_bridge=None):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    # Edit vram
    if vram:
        video_element = root.find("./devices/video/model")
        if video_element is not None:
            video_element.set("vram", str(vram))

    # Edit CPUs
    if cpus:
        cpu_element = root.find("vcpu")
        if cpu_element is not None:
            cpu_element.text = str(cpus)

    # Edit network bridge
    if network_bridge:
        interface_element = root.find("./devices/interface/source")
        if interface_element is not None:
            interface_element.set("bridge", network_bridge)
    
    new_xml = StringIO()
    tree.write(new_xml, encoding="unicode")
    return new_xml.getvalue()

def update_vm_configuration(hostname, username, password, vm_name, vram=None, cpus=None, network_bridge=None):
    # Step 1: Retrieve the VM's XML definition
    command_get_xml = f"virsh dumpxml {vm_name}"
    xml_content = ssh_command(hostname, username, password, command_get_xml)

    # Step 2: Edit the VM's XML definition
    new_xml_content = edit_vm_xml(xml_content, vram, cpus, network_bridge)

    # Step 3: Define the VM with the new XML
    command_edit_xml = f"echo '{new_xml_content}' | virsh define /dev/stdin"
    ssh_command(hostname, username, password, command_edit_xml)

if __name__ == "__main__":
    # Example usage
    hostname = "your_remote_server"
    username = "your_username"
    password = "your_password"
    vm_name = "your_vm_name"
    
    vram = 16384  # Set the VRAM (e.g., 16384 KB)
    cpus = 4      # Set the number of CPUs (e.g., 4)
    network_bridge = "virbr1"  # Set the network bridge (e.g., "virbr1")

    update_vm_configuration(hostname, username, password, vm_name, vram, cpus, network_bridge)
