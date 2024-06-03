# shutdown_vm.py
from proxmoxer import ProxmoxAPI
from config import PROXMOX_HOST, USER, PASSWORD, VERIFY_SSL

proxmox = ProxmoxAPI(PROXMOX_HOST, user=USER, password=PASSWORD, verify_ssl=VERIFY_SSL)

def shutdown_vm(node, vmid, forceStop=False, keepActive=False, skiplock=False, timeout=None):
    params = {
        'forceStop': forceStop,
        'keepActive': keepActive,
        'skiplock': skiplock,
        'timeout': timeout,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    proxmox.nodes(node).qemu(vmid).status.shutdown.post(**params)

# Example usage
shutdown_vm("node_name", 100, forceStop=True)

