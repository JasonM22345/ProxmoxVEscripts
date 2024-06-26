import libvirt
import sys
from xml.etree import ElementTree as ET

def attach_usb2_controller(vm_name, controller_id):
    # Connect to the local QEMU/KVM hypervisor
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        return

    # Find the VM
    try:
        vm = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        print(f'Failed to find the domain {vm_name}', file=sys.stderr)
        conn.close()
        return

    # Read the current XML configuration
    xml_desc = vm.XMLDesc(0)

    # Parse the XML description
    domain = ET.fromstring(xml_desc)

    # Create the USB 2 controller element with an ID
    usb2_controller_xml = f"""
    <controller type='usb' model='ich9-ehci' index='0'/>
    """
    usb2_controller = ET.fromstring(usb2_controller_xml)

    # Append the USB controller to the domain's devices
    devices = domain.find('devices')
    if devices is None:
        print(f'Failed to find devices section in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    devices.append(usb2_controller)

    # Convert the modified XML back to a string
    updated_xml_desc = ET.tostring(domain).decode()

    # Update the VM's configuration
    try:
        conn.defineXML(updated_xml_desc)
        print(f'USB 2 controller attached to VM {vm_name} successfully')
    except libvirt.libvirtError as e:
        print(f'Failed to attach USB 2 controller to VM {vm_name}: {e}', file=sys.stderr)

    # Close the connection
    conn.close()

def detach_usb2_controller(vm_name, controller_id):
    # Connect to the local QEMU/KVM hypervisor
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        return

    # Find the VM
    try:
        vm = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        print(f'Failed to find the domain {vm_name}', file=sys.stderr)
        conn.close()
        return

    # Read the current XML configuration
    xml_desc = vm.XMLDesc(0)

    # Parse the XML description
    domain = ET.fromstring(xml_desc)

    # Find and remove the USB 2 controller element with the specified ID
    devices = domain.find('devices')
    if devices is None:
        print(f'Failed to find devices section in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    usb2_controller = devices.find(f"controller[@type='usb'][@model='ich9-ehci']")
    if usb2_controller is not None:
        devices.remove(usb2_controller)
    else:
        print(f'No USB 2 controller found in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    # Convert the modified XML back to a string
    updated_xml_desc = ET.tostring(domain).decode()

    # Update the VM's configuration
    try:
        conn.defineXML(updated_xml_desc)
        print(f'USB 2 controller detached from VM {vm_name} successfully')
    except libvirt.libvirtError as e:
        print(f'Failed to detach USB 2 controller from VM {vm_name}: {e}', file=sys.stderr)

    # Close the connection
    conn.close()

# Example usage
if __name__ == '__main__':
    vm_name = 'your_vm_name'  # Replace with the name of the VM
    action = 'attach'  # Replace with 'detach' to detach the controller

    if action == 'attach':
        attach_usb2_controller(vm_name)
    elif action == 'detach':
        detach_usb2_controller(vm_name)
    
