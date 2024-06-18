import libvirt
import sys
import uuid
from xml.etree import ElementTree as ET

def clone_vm(source_vm_name, new_vm_name):
    # Connect to the local QEMU/KVM hypervisor
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        return

    # Find the source VM
    try:
        source_vm = conn.lookupByName(source_vm_name)
    except libvirt.libvirtError:
        print(f'Failed to find the source domain {source_vm_name}', file=sys.stderr)
        conn.close()
        return

    # Get the XML description of the source VM
    source_xml = source_vm.XMLDesc(0)
    source_dom = ET.fromstring(source_xml)

    # Modify the XML for the new VM
    new_dom = source_dom
    new_dom.find('name').text = new_vm_name
    new_dom.find('uuid').text = str(uuid.uuid4())

    # Modify the disk source files
    disks = new_dom.findall('devices/disk[@device="disk"]/source')
    for disk in disks:
        old_file = disk.get('file')
        if old_file:
            new_file = old_file.replace(source_vm_name, new_vm_name)
            disk.set('file', new_file)

            # Clone the disk image
            try:
                cmd = f'qemu-img create -f qcow2 -b {old_file} {new_file}'
                print(f'Executing: {cmd}')
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f'Failed to clone disk image: {e}', file=sys.stderr)
                conn.close()
                return

    # Define the new VM
    new_xml = ET.tostring(new_dom).decode()
    try:
        new_vm = conn.defineXML(new_xml)
        if new_vm is None:
            print('Failed to define the new domain', file=sys.stderr)
            conn.close()
            return
    except libvirt.libvirtError as e:
        print(f'Failed to define the new domain: {e}', file=sys.stderr)
        conn.close()
        return

    # Start the new VM
    try:
        new_vm.create()
        print(f'Successfully cloned {source_vm_name} to {new_vm_name}')
    except libvirt.libvirtError as e:
        print(f'Failed to start the new domain: {e}', file=sys.stderr)

    # Close the connection
    conn.close()

# Example usage
if __name__ == '__main__':
    source_vm_name = 'source_vm'  # Replace with the name of the source VM
    new_vm_name = 'cloned_vm'  # Replace with the desired name for the new VM
    clone_vm(source_vm_name, new_vm_name)
