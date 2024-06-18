import libvirt
import sys
import xml.etree.ElementTree as ET

def connect_to_hypervisor():
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        sys.exit(1)
    return conn

def lookup_vm(conn, vm_name):
    try:
        vm = conn.lookupByName(vm_name)
        return vm
    except libvirt.libvirtError:
        print(f'Failed to find the domain {vm_name}', file=sys.stderr)
        conn.close()
        sys.exit(1)

def update_vm_xml(vm, update_fn):
    xml_desc = vm.XMLDesc(0)
    root = ET.fromstring(xml_desc)
    update_fn(root)
    new_xml = ET.tostring(root).decode()
    try:
        vm.defineXML(new_xml)
        print(f'Successfully updated the VM {vm.name()}')
    except libvirt.libvirtError as e:
        print(f'Failed to update the VM {vm.name()}: {e}', file=sys.stderr)

def update_ram(root, memory_size_mb):
    memory_size_kb = memory_size_mb * 1024
    memory = root.find('memory')
    current_memory = root.find('currentMemory')
    memory.text = str(memory_size_kb)
    current_memory.text = str(memory_size_kb)

def update_vcpus(root, vcpu_count):
    vcpu = root.find('vcpu')
    vcpu.text = str(vcpu_count)

def update_network_interface(root, new_network):
    devices = root.find('devices')
    interface = devices.find('interface')
    if interface is not None:
        source = interface.find('source')
        source.attrib['network'] = new_network

def modify_vm_resources(vm_name, memory_size_mb=None, vcpu_count=None, new_network=None):
    conn = connect_to_hypervisor()
    vm = lookup_vm(conn, vm_name)
    
    if memory_size_mb:
        update_vm_xml(vm, lambda root: update_ram(root, memory_size_mb))
    if vcpu_count:
        update_vm_xml(vm, lambda root: update_vcpus(root, vcpu_count))
    if new_network:
        update_vm_xml(vm, lambda root: update_network_interface(root, new_network))
    
    conn.close()

# Example usage
if __name__ == '__main__':
    vm_name = 'your_vm_name'  # Replace with the name of your VM
    memory_size_mb = 2048  # Memory size in MB (e.g., 2GB = 2048MB)
    vcpu_count = 4  # Number of VCPUs
    new_network = 'new_network_name'  # Replace with the name of the new network

    modify_vm_resources(vm_name, memory_size_mb, vcpu_count, new_network)
