import libvirt
import sys
from xml.etree import ElementTree as ET

def attach_usb3_controller(vm_name, controller_id):
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

    # Create the USB 3 controller element with an ID
    usb3_controller_xml = f"""
    <controller type='usb' model='nec-xhci' id='{controller_id}'/>
    """
    usb3_controller = ET.fromstring(usb3_controller_xml)

    # Append the USB controller to the domain's devices
    devices = domain.find('devices')
    if devices is None:
        print(f'Failed to find devices section in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    devices.append(usb3_controller)

    # Convert the modified XML back to a string
    updated_xml_desc = ET.tostring(domain).decode()

    # Update the VM's configuration
    try:
        vm.updateDeviceFlags(updated_xml_desc, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        print(f'USB 3 controller with ID {controller_id} attached to VM {vm_name} successfully')
    except libvirt.libvirtError as e:
        print(f'Failed to attach USB 3 controller to VM {vm_name}: {e}', file=sys.stderr)

    # Close the connection
    conn.close()

def detach_usb3_controller(vm_name, controller_id):
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

    # Find and remove the USB 3 controller element with the specified ID
    devices = domain.find('devices')
    if devices is None:
        print(f'Failed to find devices section in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    usb3_controller = devices.find(f"controller[@type='usb'][@model='nec-xhci'][@id='{controller_id}']")
    if usb3_controller is not None:
        devices.remove(usb3_controller)
    else:
        print(f'No USB 3 controller with ID {controller_id} found in the XML for {vm_name}', file=sys.stderr)
        conn.close()
        return

    # Convert the modified XML back to a string
    updated_xml_desc = ET.tostring(domain).decode()

    # Update the VM's configuration
    try:
        vm.updateDeviceFlags(updated_xml_desc, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        print(f'USB 3 controller with ID {controller_id} detached from VM {vm_name} successfully')
    except libvirt.libvirtError as e:
        print(f'Failed to detach USB 3 controller from VM {vm_name}: {e}', file=sys.stderr)

    # Close the connection
    conn.close()

# Example usage
if __name__ == '__main__':
    vm_name = 'your_vm_name'  # Replace with the name of the VM
    action = 'attach'  # Replace with 'detach' to detach the controller
    controller_id = '1'  # Replace with the desired controller ID

    if action == 'attach':
        attach_usb3_controller(vm_name, controller_id)
    elif action == 'detach':
        detach_usb3_controller(vm_name, controller_id)