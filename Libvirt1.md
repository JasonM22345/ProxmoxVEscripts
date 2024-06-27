Got it. Here are the steps tailored for your specific setup with VLAN tags 15 and 16, and the physical interfaces `bond0` on Host A and `eno1` on Host B:

### Host A Configuration

1. **Create the OVS bridge and add bond0 to it**:
   ```sh
   sudo ovs-vsctl add-br ovsbridge0
   sudo ovs-vsctl add-port ovsbridge0 bond0
   ```

2. **Create VLAN interfaces on `ovsbridge0` for VLANs 15 and 16**:
   ```sh
   sudo ovs-vsctl add-port ovsbridge0 vlan15 tag=15 -- set Interface vlan15 type=internal
   sudo ovs-vsctl add-port ovsbridge0 vlan16 tag=16 -- set Interface vlan16 type=internal
   ```

3. **Assign VLAN interfaces to virtual machines in libvirt**:
   Edit each VM's XML configuration to include the appropriate VLAN tag:
   ```xml
   <interface type='bridge'>
     <mac address='52:54:00:6b:3c:58'/>
     <source bridge='ovsbridge0'/>
     <model type='virtio'/>
     <virtualport type='openvswitch'>
       <parameters interfaceid='vnet0'/>
     </virtualport>
     <vlan>
       <tag id='15'/>
     </vlan>
   </interface>
   ```

### Host B Configuration

1. **Create the OVS bridge and add eno1 to it**:
   ```sh
   sudo ovs-vsctl add-br ovsbridge0
   sudo ovs-vsctl add-port ovsbridge0 eno1
   ```

2. **Create VLAN interfaces on `ovsbridge0` for VLANs 15 and 16**:
   ```sh
   sudo ovs-vsctl add-port ovsbridge0 vlan15 tag=15 -- set Interface vlan15 type=internal
   sudo ovs-vsctl add-port ovsbridge0 vlan16 tag=16 -- set Interface vlan16 type=internal
   ```

3. **Assign VLAN interfaces to virtual machines in libvirt**:
   Edit each VM's XML configuration to include the appropriate VLAN tag:
   ```xml
   <interface type='bridge'>
     <mac address='52:54:00:6b:3c:58'/>
     <source bridge='ovsbridge0'/>
     <model type='virtio'/>
     <virtualport type='openvswitch'>
       <parameters interfaceid='vnet0'/>
     </virtualport>
     <vlan>
       <tag id='15'/>
     </vlan>
   </interface>
   ```

### Physical Switch Configuration

1. **Configure the physical switch ports to trunk mode**:
   Ensure the switch ports connected to `bond0` on Host A and `eno1` on Host B are set to trunk mode and allow VLANs 15 and 16 to pass through.

   Example configuration for a Cisco switch:
   ```sh
   interface GigabitEthernet0/1
     switchport trunk encapsulation dot1q
     switchport mode trunk
     switchport trunk allowed vlan 15,16
   ```

2. **Verify Trunking**:
   Ensure the physical switch allows VLAN tags 15 and 16 to pass through correctly between the hosts.

### Verification

1. **Check OVS bridge status**:
   On both hosts, run:
   ```sh
   sudo ovs-vsctl show
   ```
   Verify that the bridges, ports, and VLANs are correctly configured.

2. **Test Connectivity**:
   Ensure that VMs on the same VLAN (15 or 16) but on different hosts can communicate. Use `ping`, `traceroute`, or other networking tools to test connectivity between the VMs.

By following these tailored steps, you should be able to achieve VLAN-tagged communication between VMs on different libvirt hosts using OVS bridges.
