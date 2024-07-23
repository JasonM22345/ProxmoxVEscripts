To configure your Debian host as a router with specific VLAN and routing requirements, follow these steps:

### 1. **Install Necessary Packages**
Ensure your system has the necessary packages installed:

```sh
sudo apt-get update
sudo apt-get install vlan bridge-utils iptables-persistent
```

### 2. **Enable IP Forwarding**
Enable IP forwarding to allow the host to route traffic between interfaces:

```sh
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
```

Make this change permanent by editing `/etc/sysctl.conf` and adding:

```sh
net.ipv4.ip_forward=1
```

### 3. **Create VLAN Interfaces**
Create the VLAN interfaces. Assuming the physical interface is `bond0`:

```sh
sudo vconfig add bond0 16
sudo vconfig add bond0 15
sudo vconfig add bond0 13

sudo ip link set up bond0.16
sudo ip link set up bond0.15
sudo ip link set up bond0.13
```

### 4. **Assign IP Addresses**
Assign IP addresses to the VLAN interfaces:

```sh
sudo ip addr add 192.168.16.1/24 dev bond0.16
sudo ip addr add 192.168.15.1/24 dev bond0.15
sudo ip addr add 192.168.13.1/24 dev bond0.13
```

### 5. **Configure iptables Rules**
Set up iptables rules to enforce the routing and access control:

```sh
# Allow traffic from VLAN 15 and 13 to 192.168.16.8
sudo iptables -A FORWARD -i bond0.15 -d 192.168.16.8 -j ACCEPT
sudo iptables -A FORWARD -i bond0.13 -d 192.168.16.8 -j ACCEPT

# Drop traffic between VLANs
sudo iptables -A FORWARD -i bond0.15 -o bond0.13 -j DROP
sudo iptables -A FORWARD -i bond0.13 -o bond0.15 -j DROP

# Allow traffic within VLAN 15 and 13
sudo iptables -A FORWARD -i bond0.15 -o bond0.15 -j ACCEPT
sudo iptables -A FORWARD -i bond0.13 -o bond0.13 -j ACCEPT

# Allow traffic from VLAN 16 to anywhere
sudo iptables -A FORWARD -i bond0.16 -j ACCEPT
```

### 6. **Save iptables Rules**
Save the iptables rules to ensure they persist across reboots:

```sh
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### 7. **Configure Routing**
Ensure that the Debian host has the correct routes to forward traffic:

```sh
sudo ip route add 192.168.16.8/32 dev bond0.16
sudo ip route add 192.168.15.0/24 dev bond0.15
sudo ip route add 192.168.13.0/24 dev bond0.13
```

### 8. **Configure Network Interfaces Permanently**
Edit the network interfaces configuration file `/etc/network/interfaces` to make these settings persistent:

```sh
auto bond0
iface bond0 inet manual
    bond-slaves none
    bond-mode 802.3ad
    bond-miimon 100
    bond-downdelay 200
    bond-updelay 200

auto bond0.16
iface bond0.16 inet static
    address 192.168.16.1
    netmask 255.255.255.0
    vlan-raw-device bond0

auto bond0.15
iface bond0.15 inet static
    address 192.168.15.1
    netmask 255.255.255.0
    vlan-raw-device bond0

auto bond0.13
iface bond0.13 inet static
    address 192.168.13.1
    netmask 255.255.255.0
    vlan-raw-device bond0
```

### 9. **Restart Networking Service**
Restart the networking service to apply the changes:

```sh
sudo systemctl restart networking
```

This setup will ensure that your Debian host acts as a router, allowing VLANs 15 and 13 to reach the specific IP (192.168.16.8) in VLAN 16 while preventing inter-VLAN communication.