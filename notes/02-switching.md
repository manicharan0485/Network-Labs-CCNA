# Notes: Switching — VLANs, STP, MAC Tables (CCNA Phase 2)

## VLANs (Virtual LANs)

### Why VLANs?
- Segment broadcast domains without physical separation
- Improve security (HR traffic isolated from Finance)
- Reduce unnecessary broadcast traffic
- Logical grouping regardless of physical location

### VLAN Types
| Type | Description |
|------|-------------|
| Data VLAN | Carries user traffic |
| Voice VLAN | Dedicated for VoIP (QoS priority) |
| Management VLAN | Switch management (SSH/Telnet) — never VLAN 1 in production |
| Native VLAN | Untagged traffic on trunk (default VLAN 1 — change this!) |

### VLAN Configuration
```bash
# Create VLANs
Switch(config)# vlan 10
Switch(config-vlan)# name SALES
Switch(config)# vlan 20
Switch(config-vlan)# name IT
Switch(config)# vlan 30
Switch(config-vlan)# name MGMT

# Access port (single VLAN)
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10

# Trunk port (multiple VLANs)
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk encapsulation dot1q   # on older switches
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# switchport trunk native vlan 999       # change native VLAN!

# Verify
Switch# show vlan brief
Switch# show interfaces trunk
Switch# show interfaces Fa0/1 switchport
```

### Inter-VLAN Routing — Router on a Stick
```bash
# Router subinterfaces
Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0

Router(config)# interface GigabitEthernet0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
```

### Inter-VLAN Routing — Layer 3 Switch (SVIs)
```bash
# Enable IP routing on L3 switch
Switch(config)# ip routing

# Create SVI per VLAN
Switch(config)# interface vlan 10
Switch(config-if)# ip address 192.168.10.1 255.255.255.0
Switch(config-if)# no shutdown

Switch(config)# interface vlan 20
Switch(config-if)# ip address 192.168.20.1 255.255.255.0
Switch(config-if)# no shutdown
```

---

## MAC Address Table

```bash
# View MAC table
Switch# show mac address-table
Switch# show mac address-table dynamic
Switch# show mac address-table vlan 10

# Clear dynamic entries
Switch# clear mac address-table dynamic

# How it works:
# 1. Frame arrives on Fa0/1 from MAC aa:bb:cc:dd:ee:ff
# 2. Switch LEARNS: aa:bb:cc:dd:ee:ff → Fa0/1 (added to table)
# 3. If destination MAC known → UNICAST forward
# 4. If destination MAC unknown → FLOOD out all ports (except source)
# 5. If destination is broadcast → FLOOD all ports (except source)
```

---

## STP — Spanning Tree Protocol

### Why STP?
Prevents Layer 2 loops (broadcast storms) when redundant links exist.

### STP Port States (802.1D)
```
Blocking → Listening (15s) → Learning (15s) → Forwarding
```
| State | Forwards Frames? | Learns MACs? |
|-------|-----------------|--------------|
| Blocking | No | No |
| Listening | No | No |
| Learning | No | Yes |
| Forwarding | Yes | Yes |
| Disabled | No | No |

### Root Bridge Election
```
1. Switch with lowest Bridge ID (Priority + MAC) wins
2. Default priority = 32768
3. Lower priority = more likely to be Root Bridge

# Set root bridge manually
Switch(config)# spanning-tree vlan 10 priority 4096    # Must be multiples of 4096
# OR use macro:
Switch(config)# spanning-tree vlan 10 root primary     # Sets priority to 24576
Switch(config)# spanning-tree vlan 10 root secondary   # Sets priority to 28672
```

### RSTP (Rapid STP — 802.1w)
- Converges in ~1–2 seconds vs 30–50s for 802.1D
- Port roles: Root, Designated, Alternate, Backup
- Replaces Listening/Blocking with Discarding state

```bash
# Enable RSTP (recommended)
Switch(config)# spanning-tree mode rapid-pvst

# Verify
Switch# show spanning-tree
Switch# show spanning-tree vlan 10
Switch# show spanning-tree summary
```

### PortFast & BPDU Guard
```bash
# PortFast — skip STP states for access ports (host-facing only!)
Switch(config-if)# spanning-tree portfast

# BPDU Guard — shut port if BPDU received on PortFast port
Switch(config-if)# spanning-tree bpduguard enable

# Enable globally on all PortFast ports
Switch(config)# spanning-tree portfast default
Switch(config)# spanning-tree portfast bpduguard default
```

---

## EtherChannel

Bundles multiple physical links into one logical link.
- Load balancing across member links
- Redundancy — if one link fails, others continue

```bash
# LACP (IEEE 802.3ad — recommended)
Switch(config)# interface range GigabitEthernet0/1-2
Switch(config-if-range)# channel-group 1 mode active    # LACP active
Switch(config-if-range)# channel-protocol lacp

# Configure the port-channel
Switch(config)# interface Port-channel1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30

# PAgP (Cisco proprietary)
Switch(config-if-range)# channel-group 1 mode desirable # PAgP

# Verify
Switch# show etherchannel summary
Switch# show etherchannel port-channel
```

---

## DHCP Snooping (Layer 2 Security)

Prevents rogue DHCP servers on the network.

```bash
# Enable DHCP snooping
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10,20,30

# Trusted port (uplink to real DHCP server)
Switch(config-if)# ip dhcp snooping trust

# Rate-limit untrusted ports (prevent DHCP exhaustion)
Switch(config-if)# ip dhcp snooping limit rate 10

# Verify
Switch# show ip dhcp snooping
Switch# show ip dhcp snooping binding
```

---

## Common Exam Questions — Switching

1. **What is the default STP priority?** → 32768
2. **Which port state learns MAC addresses but does NOT forward?** → Learning
3. **What command enables RSTP?** → `spanning-tree mode rapid-pvst`
4. **Native VLAN default?** → VLAN 1 (security best practice: change it)
5. **DTP (Dynamic Trunking Protocol)** — auto-negotiates trunk; disable in prod: `switchport nonegotiate`
6. **VTP modes:** Server (default), Client, Transparent — VTP is dangerous; use Transparent or disable
