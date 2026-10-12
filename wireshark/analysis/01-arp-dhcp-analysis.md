# Wireshark Analysis — ARP & DHCP

## Capture 1: ARP Process Analysis

### Setup
- Topology: Two PCs on same subnet (192.168.1.0/24)
- PC1: 192.168.1.10 / PC2: 192.168.1.20
- Wireshark filter: `arp`

### Observations

**Frame 1 — ARP Request (Broadcast)**
```
Source MAC:      aa:bb:cc:00:00:01 (PC1)
Destination MAC: ff:ff:ff:ff:ff:ff (BROADCAST)
EtherType:       0x0806 (ARP)

ARP Header:
  Hardware type:    Ethernet (1)
  Protocol type:    IPv4 (0x0800)
  Opcode:           Request (1)
  Sender MAC:       aa:bb:cc:00:00:01
  Sender IP:        192.168.1.10
  Target MAC:       00:00:00:00:00:00 (unknown)
  Target IP:        192.168.1.20
```

**Frame 2 — ARP Reply (Unicast)**
```
Source MAC:      aa:bb:cc:00:00:02 (PC2)
Destination MAC: aa:bb:cc:00:00:01 (PC1)
EtherType:       0x0806 (ARP)

ARP Header:
  Opcode:      Reply (2)
  Sender MAC:  aa:bb:cc:00:00:02
  Sender IP:   192.168.1.20
  Target MAC:  aa:bb:cc:00:00:01
  Target IP:   192.168.1.10
```

### Key Findings
- ARP Request is always a **broadcast** (FF:FF:FF:FF:FF:FF)
- ARP Reply is always **unicast** back to requester
- After ARP completes, PC1's ARP cache has PC2's MAC
- Subsequent communication uses cached MAC (no more ARP)

### Follow-up: Gratuitous ARP
- Opcode = Reply, Sender IP = Target IP
- Used by: IP conflict detection, failover (HSRP/VRRP), after NIC replacement

---

## Capture 2: DHCP DORA Process

### Setup
- DHCP server: 192.168.1.1
- Client: Fresh boot, no IP address
- Wireshark filter: `dhcp` or `bootp`

### DORA Process — 4 Frames

**Frame 1 — DHCP Discover**
```
Source IP:      0.0.0.0       (client has no IP yet)
Destination IP: 255.255.255.255 (broadcast)
Source MAC:     client MAC
Destination MAC: ff:ff:ff:ff:ff:ff

DHCP:
  Message type: DHCP Discover (1)
  Transaction ID: 0x3d1c4b2e   (random, tracks this exchange)
  Client MAC: aa:bb:cc:dd:ee:ff
  Parameter Request List:
    - Subnet Mask
    - Router (Default Gateway)
    - DNS Servers
    - Domain Name
```

**Frame 2 — DHCP Offer**
```
Source IP:      192.168.1.1   (DHCP server)
Destination IP: 255.255.255.255 (still broadcast — client has no IP yet)

DHCP:
  Message type: DHCP Offer (2)
  Transaction ID: 0x3d1c4b2e  (same — matches Discover)
  Your IP:     192.168.1.100  (offered IP)
  Server IP:   192.168.1.1
  Lease time:  86400 seconds (24 hours)
  Options:
    - Subnet Mask: 255.255.255.0
    - Router: 192.168.1.1
    - DNS: 8.8.8.8
```

**Frame 3 — DHCP Request**
```
Source IP:      0.0.0.0       (still not officially assigned)
Destination IP: 255.255.255.255

DHCP:
  Message type: DHCP Request (3)
  Transaction ID: 0x3d1c4b2e
  Requested IP: 192.168.1.100
  Server Identifier: 192.168.1.1
! Broadcast so OTHER DHCP servers know this offer was accepted
```

**Frame 4 — DHCP Acknowledgment**
```
Source IP:      192.168.1.1
Destination IP: 255.255.255.255

DHCP:
  Message type: DHCP ACK (5)
  Transaction ID: 0x3d1c4b2e
  Your IP:     192.168.1.100   (confirmed!)
  Lease time:  86400 seconds
```

### Key Findings
- All DHCP frames are **broadcast** (client doesn't have IP yet)
- **Transaction ID** links all 4 frames together
- DHCP Request is broadcast to notify *all* DHCP servers
- ip helper-address routes DHCP broadcasts across router boundaries

---

## Capture 3: TCP Three-Way Handshake + HTTP

### Wireshark Filter: `tcp.port == 80`

**Frame 1 — SYN**
```
Src: 192.168.1.10:51234  →  Dst: 93.184.216.34:80
Flags: SYN
Seq: 0 (relative)
```

**Frame 2 — SYN-ACK**
```
Src: 93.184.216.34:80  →  Dst: 192.168.1.10:51234
Flags: SYN, ACK
Seq: 0, Ack: 1
```

**Frame 3 — ACK**
```
Src: 192.168.1.10:51234  →  Dst: 93.184.216.34:80
Flags: ACK
Seq: 1, Ack: 1
[Connection established — HTTP follows]
```

### Key Findings
- SYN starts connection, SYN-ACK acknowledges
- Each ACK = previous SEQ + 1
- `tcp.stream eq 0` filter follows entire conversation
- `Statistics > Flow Graph` shows timeline visually

---

## Useful Wireshark Tips

```
# Follow a TCP stream
Right-click frame → Follow → TCP Stream

# Statistics
Statistics > Protocol Hierarchy    (breakdown of all protocols)
Statistics > Conversations         (who talked to whom)
Statistics > IO Graphs             (traffic over time)
Statistics > Flow Graph            (SYN/ACK timeline)

# Export specific packets
File → Export Specified Packets → selected packets only

# Colorize rules
View → Coloring Rules
  Red background = TCP errors/retransmissions
  Yellow = Checksum errors
  Blue = DNS
```
