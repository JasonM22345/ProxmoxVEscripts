import libvirt
import sys
from xml.etree import ElementTree

def add_serial_tcp(vm_name, host, port, mode):
    try:
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print('Failed to open connection to qemu:///system', file=sys.stderr)
            exit(1)

        dom = conn.lookupByName(vm_name)
        if dom is None:
            print(f'Failed to find the domain {vm_name}', file=sys.stderr)
            exit(1)

        dom_xml = dom.XMLDesc(0)
        tree = ElementTree.fromstring(dom_xml)

        devices = tree.find('devices')
        serial = ElementTree.SubElement(devices, 'serial', type='tcp')
        source = ElementTree.SubElement(serial, 'source', mode=mode, host=host, service=port)
        protocol = ElementTree.SubElement(serial, 'protocol', type='raw')
        target = ElementTree.SubElement(serial, 'target', port='0')

        new_dom_xml = ElementTree.tostring(tree).decode('utf-8')

        conn.defineXML(new_dom_xml)
        print(f'Successfully added serial port to {vm_name}')

        conn.close()
    except libvirt.libvirtError as e:
        print(f'Failed to add serial port to {vm_name}: {e}', file=sys.stderr)

if __name__ == "__main__":
    vm_name_1 = "vm1"
    vm_name_2 = "vm2"
    tcp_host = "0.0.0.0"
    tcp_port = "1234"

    # VM 1 binds to the TCP port
    add_serial_tcp(vm_name_1, tcp_host, tcp_port, "bind")

    # VM 2 connects to VM 1
    add_serial_tcp(vm_name_2, "192.168.122.1", tcp_port, "connect")
