#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import xml.etree.ElementTree as ET

CONF_DIR = os.path.expanduser("~/.local/VM/snapshots")
PREFIX = "_pre_"

def print_help():
    script_name = os.path.basename(__file__)
    help_message = f"""
    {script_name}: create and revert external libvirt snapshots easily

    Usage: {script_name} <action> <domain> [snapshot name]

    Actions:
    --------
    create, c           Create snapshot
                        If no snapshot name is provided, current date and time is used

    list, ls, l         List snapshots

    disks               Show active disks

    revert, rev, r      Revert snapshot and delete it (same as soft-revert + delete)

    soft-revert,
    srev, sr            Revert snapshot without deleting it (allows unrevert)

    unrevert,
    unrev, ur           Unrevert snapshot, i.e. make soft-reverted snapshot active again

    delete, del, rm     Delete snapshot

    help, h             This message

    Snapshots are created with metadata and will be shown with `virsh snapshot-list`
    """
    print(help_message)


def die(message):
    print(f"{message}. Exit.")
    sys.exit(1)


def yes_or_no(prompt):
    while True:
        yn = input(f"{prompt} [ enter + or - ]: ").strip()
        if yn == "+":
            return True
        elif yn == "-":
            return False


def has_disks(domain):
    result = subprocess.run(["virsh", "domblklist", domain, "--details"],
                            capture_output=True, text=True)
    return "file   disk" in result.stdout


def get_disks_path(domain):
    result = subprocess.run(["virsh", "domblklist", domain, "--details"],
                            capture_output=True, text=True)
    return [line.split()[3] for line in result.stdout.splitlines() if "file   disk" in line]


def create_snapshot(domain, name):
    if not has_disks(domain):
        die(f"'{domain}' has no disks, nothing to snapshot")

    domain_conf_dir = os.path.join(CONF_DIR, domain)
    base_conf = os.path.join(domain_conf_dir, f"{PREFIX}{name}.xml")
    snap_conf = os.path.join(domain_conf_dir, f"{name}.xml")

    for base_disk in get_disks_path(domain):
        snap_disk = f"{os.path.splitext(base_disk)[0]}.{name}.qcow2"
        if os.path.exists(snap_disk):
            die(f"Disk '{snap_disk}' already exists")
        if os.path.exists(snap_conf):
            die(f"Snapshot conf '{snap_conf}' already exists")
        print(f"Base disk: {base_disk}")
        print(f"Overlay disk: {snap_disk}")

        subprocess.run(["qemu-img", "create", "-f", "qcow2", "-b", base_disk, snap_disk])

    subprocess.run(["virsh", "dumpxml", domain], stdout=open(base_conf, 'w'))
    subprocess.run(["virsh", "snapshot-create-as", domain, name, "--disk-only", "--atomic"])
    subprocess.run(["virsh", "dumpxml", domain], stdout=open(snap_conf, 'w'))


def list_snapshots(domain):
    domain_conf_dir = os.path.join(CONF_DIR, domain)
    snapshots = [f[:-4] for f in os.listdir(domain_conf_dir) if f.endswith(".xml") and not f.startswith(PREFIX)]
    for snapshot in snapshots:
        conf_path = os.path.join(domain_conf_dir, f"{snapshot}.xml")
        tree = ET.parse(conf_path)
        root = tree.getroot()
        name = root.find('name').text
        timestamp = root.find('creationTime').text
        description = root.find('description').text if root.find('description') is not None else "No description"
        print(f"Name: {name}, Timestamp: {timestamp}, Description: {description}")


def delete_snapshot(domain, name):
    domain_conf_dir = os.path.join(CONF_DIR, domain)
    snap_conf = os.path.join(domain_conf_dir, f"{name}.xml")
    snap_parent_conf = os.path.join(domain_conf_dir, f"{PREFIX}{name}.xml")

    for disk in get_disks_path(domain):
        snap_disk = f"{os.path.splitext(disk)[0]}.{name}.qcow2"
        if disk == snap_disk:
            print("Looks like you are deleting the snapshot which is currently in use")
            print("You won't be able to revert if you delete it")
            if not yes_or_no("Are you sure?"):
                return
        if os.path.exists(snap_disk):
            os.remove(snap_disk)

    if os.path.exists(snap_conf):
        os.remove(snap_conf)
    if os.path.exists(snap_parent_conf):
        os.remove(snap_parent_conf)


def soft_revert(domain, name):
    domain_conf_dir = os.path.join(CONF_DIR, domain)
    subprocess.run(["virsh", "define", os.path.join(domain_conf_dir, f"{PREFIX}{name}.xml")])


def revert_snapshot(domain, name):
    soft_revert(domain, name)
    delete_snapshot(domain, name)


def unrevert_snapshot(domain, name):
    domain_conf_dir = os.path.join(CONF_DIR, domain)
    subprocess.run(["virsh", "define", os.path.join(domain_conf_dir, f"{name}.xml")])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    action = sys.argv[1]
    domain = sys.argv[2]
    domain_conf_dir = os.path.join(CONF_DIR, domain)
    os.makedirs(domain_conf_dir, exist_ok=True)

    if len(sys.argv) > 3:
        auto_name = False
        name = sys.argv[3]
    else:
        auto_name = True
        name = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')

    if action in ["create", "c"]:
        create_snapshot(domain, name)
    elif action in ["list", "ls", "l"]:
        list_snapshots(domain)
    elif action == "disks":
        print("\n".join(get_disks_path(domain)))
    elif action in ["delete", "del", "rm"]:
        delete_snapshot(domain, name)
    elif action in ["revert", "rev", "r"]:
        revert_snapshot(domain, name)
    elif action in ["soft-revert", "srev", "sr"]:
        soft_revert(domain, name)
    elif action in ["unrevert", "unrev", "ur"]:
        unrevert_snapshot(domain, name)
    elif action in ["help", "h"]:
        print_help()
    else:
        print_help()
        sys.exit(1)