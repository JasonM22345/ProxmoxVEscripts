import libvirt
import time
import sys
import os

def take_screenshot(vm_name, output_file):
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

    # Create a stream for the screenshot
    stream = conn.newStream(libvirt.VIR_STREAM_NONBLOCK)

    # Request a screenshot
    mime_type = vm.screenshot(stream, 0)
    
    # Open the output file
    with open(output_file, 'wb') as f:
        # Read the screenshot data from the stream and write it to the file
        while True:
            try:
                data = stream.recv(1024 * 1024)
                if data is None:
                    break
                f.write(data)
            except libvirt.libvirtError as e:
                print(f'Failed to receive screenshot data: {e}', file=sys.stderr)
                break

    # Close the stream and connection
    stream.finish()
    conn.close()

    print(f'Screenshot saved to {output_file}')

# Example usage
if __name__ == '__main__':
    vm_name = 'your_vm_name'
    output_file = 'screenshot.ppm'
    take_screenshot(vm_name, output_file)