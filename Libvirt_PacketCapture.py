import libvirt
import subprocess
import sys
import os

def start_packet_capture(network_name, output_file):
    # Connect to the local QEMU/KVM hypervisor
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        return

    # Find the network
    try:
        network = conn.networkLookupByName(network_name)
    except libvirt.libvirtError:
        print(f'Failed to find the network {network_name}', file=sys.stderr)
        conn.close()
        return

    # Get the bridge name for the network
    network_xml = network.XMLDesc()
    bridge_name = None
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(network_xml)
        bridge_name = root.find("bridge").get("name")
    except Exception as e:
        print(f'Failed to parse network XML: {e}', file=sys.stderr)
        conn.close()
        return

    if not bridge_name:
        print(f'Failed to find the bridge name for network {network_name}', file=sys.stderr)
        conn.close()
        return

    # Start tcpdump to capture packets on the bridge interface
    try:
        cmd = ["sudo", "tcpdump", "-i", bridge_name, "-w", output_file]
        print(f'Starting packet capture on {bridge_name}, output will be saved to {output_file}')
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Failed to start packet capture: {e}', file=sys.stderr)
    finally:
        conn.close()

# Example usage
if __name__ == '__main__':
    network_name = 'default'  # Replace with your network name
    output_file = 'capture.pcap'  # Replace with your desired output file name
    start_packet_capture(network_name, output_file)
