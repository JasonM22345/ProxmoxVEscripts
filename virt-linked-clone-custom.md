Here's the modified code with comments indicating the new code added, ensuring the original VM remains usable and subsequent clones are based on the original disk:

```python
import contextlib
import copy
import pathlib
import subprocess
import time

import xml.etree.ElementTree as xml

import libvirt  # python package: libvirt-python


@contextlib.contextmanager
def libvirt_connection(name='qemu:///session'):
    """Libvirt connection context."""
    conn = libvirt.open(name)
    try:
        yield conn
    finally:
        conn.close()


def get_domain(conn, name):
    """Return libvirt domain object or None if not defined."""
    if name in conn.listDefinedDomains():
        return conn.lookupByName(name)


def shutdown_domain(domain):
    """Shutdown the domain, trying several times before giving up."""
    domain.shutdown()
    start = time.time()
    timeout = 3 * 60  # 3 minutes
    while (time.time() - start) < timeout:
        state, reason = domain.state()
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            break
        else:
            time.sleep(1)
    if state != libvirt.VIR_DOMAIN_SHUTOFF:
        raise RuntimeError(f'shutdown of {domain} unsuccessful, currently: {state}')


def ensure_shutdown(domain, shutdown=True):
    """Raise exception if domain is not or can not be shutdown."""
    state, reason = domain.state()
    if state == libvirt.VIR_DOMAIN_RUNNING:
        if shutdown:
            shutdown_domain(domain)
        else:
            raise RuntimeError(f'domain {source} must be shut down')
    state, reason = domain.state()
    if state != libvirt.VIR_DOMAIN_SHUTOFF:
        msg = f'domain {source} must be shut down, current state: {state}'
        raise RuntimeError(msg)


def list_cow_disks(domain):
    """Return a list of copy-on-write disks (qcow2) used by this domain."""
    result = []
    domain_xml = xml.fromstring(domain.XMLDesc(0))
    for disk in domain_xml.findall('devices/disk'):
        if disk.get('type') == 'file' and disk.get('device') == 'disk':
            driver = disk.find('driver')
            if driver.get('name') == 'qemu' and driver.get('type') == 'qcow2':
                source_file = pathlib.Path(disk.find('source').get('file'))
                target_dev = disk.find('target').get('dev')
                result.append((source_file, target_dev, disk))
    return result


def set_disk_readonly(domain, disk_xml, value=True):
    """Set/unset disk readonly attribute in the given domain."""
    readonly_tags = disk_xml.findall('readonly')
    if value and not readonly_tags:
        disk_xml.append(xml.Element('readonly'))
    elif not value and readonly_tags:
        for readonly_tag in readonly_tags:
            disk_xml.remove(readonly_tag)
    else:
        return
    disk_xml_str = xml.tostring(disk_xml, encoding='unicode')
    domain.updateDeviceFlags(disk_xml_str, 0)


def create_clone(source, target, skip_copy_devices):
    """Clone source to target, reusing the disks as-is (no copies)."""
    cmd = ['virt-clone', '--preserve-data', '--auto-clone']
    cmd += ['--original', source]
    cmd += ['--name', target]
    for disk_device in skip_copy_devices:
        cmd += ['--skip-copy', disk_device]
    subprocess.run(cmd, check=True)


def qemu_img_create(new_file, backing_file):
    """Create an overlay disk image based on another qcow2 image."""
    cmd = ['qemu-img', 'create', '-q', '-f', 'qcow2', '-F', 'qcow2']
    cmd += ['-o', f'backing_file={backing_file}']
    cmd += [new_file]
    subprocess.run(cmd, check=True)


def create_overlay_disks(domain, cow_disks):
    """Make existing disk in domain an overlay qcow2 image on the original."""
    domain_name = domain.name()
    for disk_file, disk_device, disk_xml in cow_disks:
        new_file = disk_file.parent / f'{domain_name}-{disk_device}.qcow2'
        qemu_img_create(new_file, backing_file=disk_file)

        set_disk_readonly(domain, disk_xml, value=False)

        disk_source = disk_xml.find('source')
        source_file = disk_source.get('file')

        disk_source.set('file', str(new_file))
        backing_store = xml.Element('backingStore', {'type': 'file'})
        backing_store.append(xml.Element('format', {'type': 'qcow2'}))
        backing_store.append(xml.Element('source', {'file': source_file}))
        if source_chain := disk_xml.find('backingStore'):
            backing_store.append(copy.copy(source_chain))
            disk_xml.remove(source_chain)
        disk_xml.append(backing_store)

        disk_xml_str = xml.tostring(disk_xml, encoding='unicode')
        domain.updateDeviceFlags(disk_xml_str, 0)


def ensure_original_vm_usable(source_domain, cow_disks):
    """Ensure the original VM is usable by creating overlay disks if necessary."""
    original_overlay_created = False
    for disk_file, disk_device, disk_xml in cow_disks:
        original_overlay = disk_file.parent / f'{source_domain.name()}-{disk_device}-original.qcow2'
        if not original_overlay.exists():
            qemu_img_create(original_overlay, backing_file=disk_file)
            original_overlay_created = True

        if original_overlay_created:
            disk_source = disk_xml.find('source')
            disk_source.set('file', str(original_overlay))
            set_disk_readonly(source_domain, disk_xml, value=False)

            disk_xml_str = xml.tostring(disk_xml, encoding='unicode')
            source_domain.updateDeviceFlags(disk_xml_str, 0)


def create_linked_clone(
    source, target, connection='qemu:///session', shutdown_source=True
):
    with libvirt_connection(connection) as conn:
        source_domain = get_domain(conn, source)
        if source_domain is None:
            raise ValueError(f'source libvirt domain "{source}" not found')

        if get_domain(conn, target) is not None:
            raise ValueError(f'target libvirt domain "{target}" already exists')

        cow_disks = list_cow_disks(source_domain)
        if not cow_disks:
            msg = f'source libvirt domain "{source}" has no copy-on-write disks'
            raise ValueError(msg)

        ensure_shutdown(source_domain, shutdown_source)

        # Ensure the original VM is usable
        ensure_original_vm_usable(source_domain, cow_disks)  # New code added

        for _, _, disk_xml in cow_disks:
            set_disk_readonly(source_domain, disk_xml, value=True)

        cow_disks_dev = [dev for _, dev, _ in cow_disks]
        create_clone(source, target, cow_disks_dev)

        target_domain = get_domain(conn, target)
        try:
            create_overlay_disks(target_domain, cow_disks)
        except:
            target_domain.undefine()
            raise
```

### Explanation of Changes
1. **`ensure_original_vm_usable` Function**: This function ensures that the original VM is still usable by creating overlay images for its disks if they don't already exist.
2. **Modifications in `create_linked_clone` Function**: Before making the original VM's disks read-only, it calls `ensure_original_vm_usable` to create the necessary overlay disks for the original VM, ensuring it remains usable.
3. **Overlay Disk Naming**: The original overlay disks are named with an `-original` suffix to differentiate them from the ones used by the clones.
4. **Comments**: Added comments to indicate the new code added for clarity.

With these modifications, the original VM will remain usable after the first clone and any subsequent clones will be created based on the original VM’s original read-only disks.