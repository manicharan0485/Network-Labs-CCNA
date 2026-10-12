# Lab 02 — VLANs, Trunking & Inter-VLAN Routing

## Objective
Configure VLANs on two switches, set up an 802.1Q trunk between them,
and enable inter-VLAN routing using a Router-on-a-Stick configuration.

## Topology
```
                    [Router R1]
                     Gi0/0.10
                     Gi0/0.20
                     Gi0/0.30
                         |
                    (trunk link)
                         |
              [SW1 - Core Switch]
             /         |          \
       Fa0/1          Fa0/2        trunk→[SW2]
   (VLAN 10)       (VLAN 20)           |
   PC-SALES-1      PC-IT-1        Fa0/1 (VLAN 10)
                                  Fa0/2 (VLAN 20)
                                  Fa0/3 (VLAN 30)
                                  PC-SALES-2 / PC-IT-2 / PC-HR-1
```

## Addressing Table
| Device | Interface | IP Address | VLAN | Subnet |
|--------|-----------|------------|------|--------|
| R1 | Gi0/0.10 | 192.168.10.1 | 10 (SALES) | /24 |
| R1 | Gi0/0.20 | 192.168.20.1 | 20 (IT) | /24 |
| R1 | Gi0/0.30 | 192.168.30.1 | 30 (HR) | /24 |
| PC-SALES-1 | NIC | 192.168.10.10 | 10 | /24 |
| PC-SALES-2 | NIC | 192.168.10.11 | 10 | /24 |
| PC-IT-1 | NIC | 192.168.20.10 | 20 | /24 |
| PC-IT-2 | NIC | 192.168.20.11 | 20 | /24 |
| PC-HR-1 | NIC | 192.168.30.10 | 30 | /24 |

## Step-by-Step Configuration

### SW1 — Core Switch
```bash
! Create VLANs
SW1(config)# vlan 10
SW1(config-vlan)# name SALES
SW1(config)# vlan 20
SW1(config-vlan)# name IT
SW1(config)# vlan 30
SW1(config-vlan)# name HR
SW1(config)# vlan 999
SW1(config-vlan)# name NATIVE_UNUSED

! Access ports
SW1(config)# interface Fa0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# spanning-tree portfast

SW1(config)# interface Fa0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20
SW1(config-if)# spanning-tree portfast

! Trunk to R1
SW1(config)# interface GigabitEthernet0/1
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,30
SW1(config-if)# switchport trunk native vlan 999

! Trunk to SW2
SW1(config)# interface GigabitEthernet0/2
SW1(config-if)# switchport mode trunk
SW1(config-if)# switchport trunk allowed vlan 10,20,30
SW1(config-if)# switchport trunk native vlan 999
SW1(config-if)# switchport nonegotiate
```

### SW2 — Access Switch
```bash
SW2(config)# vlan 10
SW2(config-vlan)# name SALES
SW2(config)# vlan 20
SW2(config-vlan)# name IT
SW2(config)# vlan 30
SW2(config-vlan)# name HR
SW2(config)# vlan 999
SW2(config-vlan)# name NATIVE_UNUSED

SW2(config)# interface Fa0/1
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 10
SW2(config-if)# spanning-tree portfast

SW2(config)# interface Fa0/2
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 20
SW2(config-if)# spanning-tree portfast

SW2(config)# interface Fa0/3
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 30
SW2(config-if)# spanning-tree portfast

! Trunk uplink to SW1
SW2(config)# interface GigabitEthernet0/1
SW2(config-if)# switchport mode trunk
SW2(config-if)# switchport trunk allowed vlan 10,20,30
SW2(config-if)# switchport trunk native vlan 999
SW2(config-if)# switchport nonegotiate
```

### R1 — Router on a Stick
```bash
! Enable physical interface (no IP on main interface)
R1(config)# interface GigabitEthernet0/0
R1(config-if)# no shutdown

! Subinterface for VLAN 10
R1(config)# interface GigabitEthernet0/0.10
R1(config-subif)# encapsulation dot1Q 10
R1(config-subif)# ip address 192.168.10.1 255.255.255.0
R1(config-subif)# description SALES_VLAN

! Subinterface for VLAN 20
R1(config)# interface GigabitEthernet0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.20.1 255.255.255.0
R1(config-subif)# description IT_VLAN

! Subinterface for VLAN 30
R1(config)# interface GigabitEthernet0/0.30
R1(config-subif)# encapsulation dot1Q 30
R1(config-subif)# ip address 192.168.30.1 255.255.255.0
R1(config-subif)# description HR_VLAN
```

## Verification Steps

```bash
! On switches
SW1# show vlan brief
SW1# show interfaces trunk
SW1# show interfaces Fa0/1 switchport

! On router
R1# show ip interface brief
R1# show ip route

! From PCs
PC-SALES-1> ping 192.168.10.1      ! Gateway — should PASS
PC-SALES-1> ping 192.168.20.10     ! Cross-VLAN — should PASS (via router)
PC-SALES-1> ping 192.168.30.10     ! Cross-VLAN — should PASS (via router)
```

## Expected Results
- Same-VLAN pings: ✅ Pass (switched locally)
- Cross-VLAN pings: ✅ Pass (routed via R1 subinterfaces)
- VLAN 10 to VLAN 30: ✅ Pass

## Troubleshooting Tips
| Symptom | Check |
|---------|-------|
| Same-VLAN ping fails | `show vlan brief` — is port in correct VLAN? |
| Cross-VLAN ping fails | `show ip route` on R1 — are subinterfaces up? |
| Trunk not working | `show interfaces trunk` — VLANs in "VLANs allowed" list? |
| Native VLAN mismatch | `show interfaces trunk` — native VLAN must match on both sides |
