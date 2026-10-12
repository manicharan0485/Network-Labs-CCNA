# Notes: Routing — Static Routes, OSPF, EIGRP (CCNA Phase 3)

## Routing Fundamentals

### How a Router Forwards Packets
```
1. Check destination IP against routing table
2. Longest prefix match wins (most specific route)
3. If no match → drop (or send to default route 0.0.0.0/0)
```

### Route Sources (Administrative Distance)
| Source | AD | Notes |
|--------|-----|-------|
| Connected | 0 | Directly attached network |
| Static | 1 | Manually configured |
| EIGRP summary | 5 | |
| eBGP | 20 | External BGP |
| OSPF | 110 | |
| IS-IS | 115 | |
| RIP | 120 | |
| EIGRP (internal) | 90 | |
| Unknown | 255 | Never installed |

Lower AD = more trusted = preferred in routing table.

---

## Static Routes

```bash
# Basic static route
Router(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.2

# Default route (catch-all)
Router(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.1

# Floating static (backup route — higher AD)
Router(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.3 200  # AD=200 > OSPF 110

# Verify
Router# show ip route
Router# show ip route static
Router# show ip route 192.168.2.0
```

---

## OSPFv2 (Open Shortest Path First)

### Key Concepts
- **Link State** routing protocol — builds complete topology map
- Uses **Dijkstra's SPF** algorithm to calculate best paths
- **Metric = Cost** (reference bandwidth / interface bandwidth)
- Default reference bandwidth: 100 Mbps (change to 1000+ Mbps for modern links)
- **Areas** — Area 0 = backbone, all other areas must connect to Area 0
- **Hello interval:** 10s (broadcast), 30s (point-to-point)
- **Dead interval:** 40s (4× hello)

### OSPF Router Types
```
ABR  (Area Border Router)     — connects two areas
ASBR (Autonomous System BR)   — connects OSPF to external (e.g., RIP/BGP)
```

### DR/BDR Election (on broadcast networks)
```
Highest priority wins (default 1, range 0–255)
Tie → Highest Router ID (highest loopback IP, or highest active IP)
DR  = Designated Router  (all routers send updates to DR: 224.0.0.6)
BDR = Backup Designated Router
DROther = all other routers (send to 224.0.0.6, receive from 224.0.0.5)
```

### OSPF Configuration
```bash
# Single area
Router(config)# router ospf 1
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
Router(config-router)# network 10.0.0.0 0.0.0.3 area 0

# Router ID (set manually — recommended!)
Router(config-router)# router-id 1.1.1.1

# Passive interface (no hellos sent — for LAN-facing interfaces)
Router(config-router)# passive-interface GigabitEthernet0/0

# Adjust reference bandwidth (match ALL routers!)
Router(config-router)# auto-cost reference-bandwidth 1000

# Set priority (0 = never becomes DR)
Router(config-if)# ip ospf priority 100

# Verify
Router# show ip ospf
Router# show ip ospf neighbor
Router# show ip ospf interface
Router# show ip ospf database
Router# show ip route ospf
```

### OSPF Neighbor States
```
Down → Init → 2-Way → ExStart → Exchange → Loading → Full
```
- **2-Way**: Seen each other's Hello (DR/BDR election happens here)
- **Full**: Complete — adjacency established, database synchronized

### Multi-Area OSPF
```bash
Router(config)# router ospf 1
Router(config-router)# network 10.1.0.0 0.0.0.255 area 0     # Backbone
Router(config-router)# network 10.2.0.0 0.0.0.255 area 1     # Stub area
Router(config-router)# network 10.3.0.0 0.0.0.255 area 2
```

---

## EIGRP (Enhanced Interior Gateway Routing Protocol)

- **Cisco proprietary** (now open standard)
- **Hybrid** — distance vector with link-state features
- Uses **DUAL** algorithm (Diffusing Update Algorithm)
- **Metric:** Bandwidth + Delay (default); can include reliability, load, MTU
- **AD:** 90 (internal), 170 (external)

```bash
# EIGRP config
Router(config)# router eigrp 100            # AS number must match on neighbors
Router(config-router)# network 192.168.1.0 0.0.0.255
Router(config-router)# no auto-summary     # ALWAYS disable auto-summary!
Router(config-router)# passive-interface GigabitEthernet0/0

# Verify
Router# show ip eigrp neighbors
Router# show ip eigrp topology
Router# show ip route eigrp
```

---

## ACLs (Access Control Lists)

### Types
| Type | Range | Function |
|------|-------|----------|
| Standard | 1–99, 1300–1999 | Filter by source IP only |
| Extended | 100–199, 2000–2699 | Filter by src/dst IP, port, protocol |
| Named | Any name | Standard or extended with names |

### Placement Rule
- **Standard ACLs** → place as **close to the destination** as possible
- **Extended ACLs** → place as **close to the source** as possible

```bash
# Standard ACL — permit only 192.168.1.0/24
Router(config)# access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)# access-list 10 deny any      # Implicit deny already exists

# Extended ACL — block Telnet from any source to 192.168.2.0/24
Router(config)# access-list 110 deny tcp any 192.168.2.0 0.0.0.255 eq 23
Router(config)# access-list 110 permit ip any any

# Named extended ACL (best practice)
Router(config)# ip access-list extended BLOCK_TELNET
Router(config-ext-nacl)# deny tcp any 192.168.2.0 0.0.0.255 eq 23
Router(config-ext-nacl)# permit ip any any

# Apply to interface
Router(config-if)# ip access-group 110 in       # Inbound
Router(config-if)# ip access-group BLOCK_TELNET out  # Outbound

# Verify
Router# show access-lists
Router# show ip interface Gi0/0 | include access list
```

---

## NAT (Network Address Translation)

### Types
| Type | Description |
|------|-------------|
| Static NAT | 1:1 — one private IP → one public IP |
| Dynamic NAT | Pool of public IPs mapped to private IPs |
| PAT / NAT Overload | Many private IPs → one public IP (port tracking) |

```bash
# Static NAT — map 192.168.1.10 to 203.0.113.10
Router(config)# ip nat inside source static 192.168.1.10 203.0.113.10

# PAT / Overload (most common for home/small office)
Router(config)# ip nat pool PUBLIC 203.0.113.1 203.0.113.1 netmask 255.255.255.0
Router(config)# access-list 1 permit 192.168.1.0 0.0.0.255
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload

# Mark inside/outside interfaces
Router(config-if)# ip nat inside      # LAN-facing interface
Router(config-if)# ip nat outside     # WAN-facing interface

# Verify
Router# show ip nat translations
Router# show ip nat statistics
Router# debug ip nat              # Live debug (use carefully!)
```

---

## Common Exam Questions — Routing

1. **OSPF default cost for 100Mbps link?** → 1 (reference / bandwidth = 100/100)
2. **OSPF hello interval on broadcast network?** → 10 seconds
3. **What triggers DR/BDR election?** → Highest priority, then highest Router ID
4. **Standard ACL placement?** → Close to destination
5. **What does `no auto-summary` do in EIGRP?** → Prevents classful summarization (always disable)
6. **PAT uses what to track multiple connections?** → Port numbers
