# delete_snapshot.py
from proxmoxer import ProxmoxAPI
from config import PROXMOX_HOST, USER, PASSWORD, VERIFY_SSL

proxmox = ProxmoxAPI(PROXMOX_HOST, user=USER, password=PASSWORD, verify_ssl=VERIFY_SSL)

def delete_snapshot(node, vmid, snapname):
    proxmox.nodes(node).qemu(vmid).snapshot(snapname).delete()

# Example usage
delete_snapshot("node_name", 100, "snapshot_name")

