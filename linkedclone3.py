import libvirt
import sys
import os
import time

def create_linked_clone(vm_name, clone_name, snapshot_name=None):
    try:
        conn = libvirt.open('qemu:///system')
        if conn is None:
            print("Failed to open connection to qemu:///system")
            sys.exit(1)

        dom = conn.lookupByName(vm_name)
        if dom is None:
            print(f"Failed to find the domain {vm_name}")
            sys.exit(1)

        # Get the original disk path
        xml_desc = dom.XMLDesc()
        disk_path = None
        for line in xml_desc.splitlines():
            if "<source file=" in line:
                disk_path = line.split("'")[1]
                break
        
        if disk_path is None:
            print("Failed to find the original disk path")
            sys.exit(1)

        # Determine the backing file
        backing_file = disk_path

        if snapshot_name:
            snapshot = dom.snapshotLookupByName(snapshot_name)
            snapshot_xml = snapshot.getXMLDesc()
            for line in snapshot_xml.splitlines():
                if "<source file=" in line:
                    backing_file = line.split("'")[1]
                    break

        # Create a new qcow2 disk for the clone with a unique name based on the current timestamp
        timestamp = int(time.time())
        clone_disk_path = f"/var/lib/libvirt/images/{clone_name}_{timestamp}.qcow2"
        os.system(f"qemu-img create -f qcow2 -o backing_file={backing_file} {clone_disk_path}")

        # Create a new XML description for the cloned VM
        clone_xml = xml_desc.replace(vm_name, clone_name)
        clone_xml = clone_xml.replace(disk_path, clone_disk_path)

        # Modify the XML to add backingStore information
        clone_xml_lines = clone_xml.splitlines()
        new_clone_xml_lines = []
        for line in clone_xml_lines:
            new_clone_xml_lines.append(line)
            if f"<source file='{clone_disk_path}'" in line:
                new_clone_xml_lines.append(f"""
                <backingStore type='file' index='1'>
                    <format type='qcow2'/>
                    <source file='{backing_file}'/>
                    <backingStore/>
                </backingStore>
                """)
        new_clone_xml = "\n".join(new_clone_xml_lines)

        # Define the new domain
        conn.createXML(new_clone_xml, 0)

        print(f"Linked clone {clone_name} created for domain {vm_name}")

        conn.close()
    except libvirt.libvirtError as e:
        print(f"Failed to create linked clone: {e}", file=sys.stderr)
        sys.exit(1)

# Usage: create_linked_clone("your_vm_name", "your_clone_name", "optional_snapshot_name")
create_linked_clone("your_vm_name", "your_clone_name", "optional_snapshot_name")