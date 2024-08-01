sequenceDiagram
    participant User
    participant Script
    participant libvirt

    User->>Script: Call create_linked_clone(vm_name, clone_name, snapshot_name)
    Script->>libvirt: Open connection to qemu:///system
    libvirt-->>Script: Connection opened
    Script->>libvirt: Lookup VM by name (vm_name)
    libvirt-->>Script: VM object (dom)

    alt VM not found
        Script-->>User: Error: Failed to find the domain
    else
        Script->>Script: Get original disk path from VM XML
        alt Disk path not found
            Script-->>User: Error: Failed to find the original disk path
        else
            alt Snapshot name provided
                Script->>libvirt: Lookup snapshot by name (snapshot_name)
                libvirt-->>Script: Snapshot object (snapshot)
                Script->>Script: Get backing file path from snapshot XML
            else
                Script->>Script: Use original disk path as backing file
            end

            Script->>os: Create qcow2 disk for clone with backing file
            Script->>Script: Create new XML description for cloned VM
            Script->>libvirt: Define new domain with clone XML
            libvirt-->>Script: Clone defined

            Script-->>User: Linked clone (clone_name) created for domain (vm_name)
        end
    end
    Script->>libvirt: Close connection
    libvirt-->>Script: Connection closed