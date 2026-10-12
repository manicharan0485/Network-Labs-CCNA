# Lab 04 — OSPFv2 Single & Multi-Area

## Objective
Configure OSPFv2 in a single-area topology, verify neighbor adjacency,
then extend to multi-area and observe LSA types and ABR behaviour.

## Topology
```
[R1: 1.1.1.1]----10.0.12.0/30----[R2: 2.2.2.2]----10.0.23.0/30----[R3: 3.3.3.3]
     |                                  |                                  |
192.168.1.0/24                   192.168.2.0/24                    192.168.3.0/24
(Area 0)                         (Area 0)                          (Area 1)
```

## Addressing Table
| Device | Interface | IP | Area |
|--------|-----------|-----|------|
| R1 | Gi0/0 | 192.168.1.1/24 | 0 |
| R1 | Gi0/1 | 10.0.12.1/30 | 0 |
| R1 | Loopback0 | 1.1.1.1/32 | 0 |
| R2 | Gi0/0 | 192.168.2.1/24 | 0 |
| R2 | Gi0/1 | 10.0.12.2/30 | 0 |
| R2 | Gi0/2 | 10.0.23.1/30 | 0 |
| R2 | Loopback0 | 2.2.2.2/32 | 0 |
| R3 | Gi0/0 | 192.168.3.1/24 | 1 |
| R3 | Gi0/1 | 10.0.23.2/30 | 1 |
| R3 | Loopback0 | 3.3.3.3/32 | 1 |

## Part 1 — Single Area OSPF (Area 0)

### R1 Configuration
```bash
R1(config)# router ospf 1
R1(config-router)# router-id 1.1.1.1
R1(config-router)# auto-cost reference-bandwidth 1000
R1(config-router)# network 192.168.1.0 0.0.0.255 area 0
R1(config-router)# network 10.0.12.0 0.0.0.3 area 0
R1(config-router)# passive-interface GigabitEthernet0/0
```

### R2 Configuration
```bash
R2(config)# router ospf 1
R2(config-router)# router-id 2.2.2.2
R2(config-router)# auto-cost reference-bandwidth 1000
R2(config-router)# network 192.168.2.0 0.0.0.255 area 0
R2(config-router)# network 10.0.12.0 0.0.0.3 area 0
R2(config-router)# network 10.0.23.0 0.0.0.3 area 0
R2(config-router)# passive-interface GigabitEthernet0/0
```

## Part 2 — Multi-Area OSPF (R3 in Area 1)

### R3 Configuration
```bash
R3(config)# router ospf 1
R3(config-router)# router-id 3.3.3.3
R3(config-router)# auto-cost reference-bandwidth 1000
R3(config-router)# network 192.168.3.0 0.0.0.255 area 1
R3(config-router)# network 10.0.23.0 0.0.0.3 area 1
R3(config-router)# passive-interface GigabitEthernet0/0
```

### R2 — Add Area 1 network
```bash
R2(config)# router ospf 1
R2(config-router)# network 10.0.23.0 0.0.0.3 area 1
! R2 is now an ABR (Area Border Router)
```

## Verification

```bash
! Verify neighbors
R1# show ip ospf neighbor
R2# show ip ospf neighbor

! Expected output on R2:
! Neighbor ID    Pri  State    Dead Time  Address       Interface
! 1.1.1.1        1    FULL/DR  00:00:38   10.0.12.1     Gi0/1
! 3.3.3.3        1    FULL/DR  00:00:35   10.0.23.2     Gi0/2

! Check routing table
R1# show ip route ospf
! Should see: O 192.168.2.0/24 [110/2] via 10.0.12.2
!             O IA 192.168.3.0/24 [110/3] via 10.0.12.2  (IA = inter-area)

! Check OSPF database
R2# show ip ospf database
! LSA Types: Router (Type 1), Network (Type 2), Summary (Type 3)

! Ping test
R1# ping 192.168.3.1 source 192.168.1.1
```

## Common OSPF Issues
| Problem | Cause | Fix |
|---------|-------|-----|
| Neighbors stuck in EXSTART | MTU mismatch | `ip mtu 1500` or `ip ospf mtu-ignore` |
| Neighbors stuck in INIT | ACL blocking multicast 224.0.0.5 | Check ACLs |
| Route not appearing | Network statement wrong | Check wildcard mask |
| Route flapping | Duplicate Router ID | Set unique `router-id` on each router |
| High cost on GigE | Reference bandwidth too low | `auto-cost reference-bandwidth 1000` |

## Questions to Answer After Lab
1. Which router is the DR on the 10.0.12.0/30 link? Why?
2. What type of LSA does R2 generate as an ABR?
3. What does "O IA" mean in the routing table?
4. What happens if you change R1's OSPF priority to 0?
