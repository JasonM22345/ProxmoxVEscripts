# clone_vm.py
from proxmoxer import ProxmoxAPI
from config import PROXMOX_HOST, USER, PASSWORD, VERIFY_SSL

proxmox = ProxmoxAPI(PROXMOX_HOST, user=USER, password=PASSWORD, verify_ssl=VERIFY_SSL)

def clone_vm(node, vmid, newid, name=None, full=False, target=None, description=None, format=None, storage=None):
    params = {
        'newid': newid,
        'name': name,
        'full': full,
        'target': target,
        'description': description,
        'format': format,
        'storage': storage,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    proxmox.nodes(node).qemu(vmid).clone.create(**params)

# Example usage
clone_vm("node_name", 100, 101, name="cloned_vm", full=True, description="Cloned VM example", format="qcow2")

