# Notes: Network Fundamentals (CCNA Phase 1)

## OSI Model — 7 Layers

| Layer | Name | PDU | Protocols / Examples |
|-------|------|-----|----------------------|
| 7 | Application | Data | HTTP, HTTPS, FTP, SMTP, DNS, DHCP |
| 6 | Presentation | Data | SSL/TLS, JPEG, ASCII |
| 5 | Session | Data | NetBIOS, RPC |
| 4 | Transport | Segment | TCP, UDP |
| 3 | Network | Packet | IP, ICMP, OSPF, EIGRP |
| 2 | Data Link | Frame | Ethernet, 802.11, PPP |
| 1 | Physical | Bit | Cables, hubs, repeaters |

**Mnemonic (top-down):** All People Seem To Need Data Processing

---

## TCP/IP Model (4-Layer)

| TCP/IP Layer | OSI Equivalent |
|---|---|
| Application | Layers 5, 6, 7 |
| Transport | Layer 4 |
| Internet | Layer 3 |
| Network Access | Layers 1, 2 |

---

## IPv4 Addressing

### Address Classes
| Class | Range | Default Mask | Usage |
|-------|-------|-------------|-------|
| A | 1–126 | /8 (255.0.0.0) | Large networks |
| B | 128–191 | /16 (255.255.0.0) | Medium networks |
| C | 192–223 | /24 (255.255.255.0) | Small networks |
| D | 224–239 | — | Multicast |

### Private Ranges (RFC 1918)
```
10.0.0.0/8          (10.x.x.x)
172.16.0.0/12       (172.16–31.x.x)
192.168.0.0/16      (192.168.x.x)
```

### Special Addresses
```
127.0.0.1           Loopback
169.254.x.x         APIPA (no DHCP response)
0.0.0.0             Default route / unspecified
255.255.255.255     Limited broadcast
```

---

## Subnetting Quick Reference

| CIDR | Subnet Mask | Hosts |
|------|-------------|-------|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /27 | 255.255.255.224 | 30 |
| /28 | 255.255.255.240 | 14 |
| /29 | 255.255.255.248 | 6 |
| /30 | 255.255.255.252 | 2 (point-to-point links) |

**Formula:** Usable hosts = 2^(32 − prefix) − 2

---

## Ethernet Fundamentals

### Frame Structure
```
| Preamble (7B) | SFD (1B) | Dst MAC (6B) | Src MAC (6B) | EtherType (2B) | Data | FCS (4B) |
```

### MAC Address Format
- 48 bits / 6 bytes — written XX:XX:XX:XX:XX:XX
- First 3 bytes = OUI (manufacturer ID)
- Last 3 bytes = device-unique identifier
- FF:FF:FF:FF:FF:FF = Ethernet broadcast

### ARP Process (Layer 2 → Layer 3 resolution)
```
1. Host A wants to reach 192.168.1.10 but doesn't know its MAC
2. Sends ARP Request (broadcast): "Who has 192.168.1.10? Tell 192.168.1.1"
3. Host B replies (unicast): "192.168.1.10 is at aa:bb:cc:dd:ee:ff"
4. Host A caches result → show arp
```

---

## TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | 3-way handshake | Connectionless |
| Reliability | Guaranteed delivery | Best effort |
| Order | Sequenced | No ordering |
| Speed | Slower | Faster |
| Use cases | HTTP, SSH, FTP | DNS, DHCP, VoIP, streaming |

### TCP 3-Way Handshake
```
Client --SYN--> Server
Client <--SYN-ACK-- Server
Client --ACK--> Server
[Connection established]
```

---

## Cisco IOS Basics

```bash
# Privilege levels
Router>            # User EXEC (limited)
Router#            # Privileged EXEC  → enable
Router(config)#    # Global config    → configure terminal
Router(config-if)# # Interface config → interface Gi0/0

# Essential show commands
show version
show ip interface brief           # Quick IP status of all interfaces
show running-config
show ip route
show arp
show mac address-table            # On switches
show interfaces GigabitEthernet0/0

# Save configuration
copy running-config startup-config
write memory                      # Shortcut

# Basic interface config
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 description "Link to Core Switch"
```

---

## Key Wireshark Filters

```
arp                         Show all ARP traffic
icmp                        Show ICMP (ping, traceroute)
tcp.port == 80              HTTP traffic only
tcp.port == 443             HTTPS traffic only
ip.addr == 192.168.1.1      Traffic to/from specific IP
tcp.flags.syn == 1          TCP SYN packets (new connections)
dns                         DNS queries and responses
dhcp                        DHCP DORA process
tcp.analysis.retransmission Retransmissions (performance issues)
http.request.method == GET  HTTP GET requests only
```

---

## Study Resources

- Jeremy's IT Lab: https://www.youtube.com/@JeremysITLab
- Cisco NetAcad: https://www.netacad.com
- Subnetting practice: https://subnettingpractice.com
- Packet Tracer: Free via NetAcad registration
