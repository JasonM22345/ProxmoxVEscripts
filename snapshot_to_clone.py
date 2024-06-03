# snapshot_to_clone.py
from proxmoxer import ProxmoxAPI
from config import PROXMOX_HOST, USER, PASSWORD, VERIFY_SSL

proxmox = ProxmoxAPI(PROXMOX_HOST, user=USER, password=PASSWORD, verify_ssl=VERIFY_SSL)

def create_snapshot(node, vmid, snapname, description=None):
    params = {
        'snapname': snapname,
        'description': description,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    proxmox.nodes(node).qemu(vmid).snapshot.post(**params)

def clone_snapshot(node, vmid, snapname, newid, name=None, full=False, target=None, description=None, format=None, storage=None):
    # Rollback to snapshot
    proxmox.nodes(node).qemu(vmid).snapshot(snapname).rollback.post()

    # Clone the VM
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
node = "node_name"
vmid = 100
snapname = "snapshot_name"
newid = 101
create_snapshot(node, vmid, snapname, description="Snapshot before cloning")
clone_snapshot(node, vmid, snapname, newid, name="cloned_vm_from_snapshot", full=True)

