# create_snapshot.py
from proxmoxer import ProxmoxAPI
from config import PROXMOX_HOST, USER, PASSWORD, VERIFY_SSL

proxmox = ProxmoxAPI(PROXMOX_HOST, user=USER, password=PASSWORD, verify_ssl=VERIFY_SSL)

def create_snapshot(node, vmid, snapname, **kwargs):
    proxmox.nodes(node).qemu(vmid).snapshot.post(snapname=snapname, **kwargs)

# Example usage
create_snapshot("node_name", 100, "snapshot_name", description="Snapshot before update")

