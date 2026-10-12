# Lab 03 — Spanning Tree Protocol (STP / RSTP)

## Objective
Observe default STP root bridge election, manually control root bridge placement,
verify port states, and enable PortFast + BPDU Guard on access ports.

## Topology (Redundant Switched Network)
```
           [SW1]
          /     \
      Gi0/1    Gi0/2
        /         \
      [SW2]-----[SW3]
       Gi0/2---Gi0/1
```

## Part 1 — Observe Default Root Bridge Election

```bash
! Check current STP state BEFORE any config
SW1# show spanning-tree vlan 1
SW2# show spanning-tree vlan 1
SW3# show spanning-tree vlan 1

! Note: Which switch has the lowest Bridge ID?
! Bridge ID = Priority (32768 default) + VLAN ID + MAC address
! Lowest MAC (all same priority) wins root election
```

## Part 2 — Manually Control Root Bridge

Best practice: Core/distribution switch should be root bridge.

```bash
! Make SW1 root for VLAN 10 and 20 (primary)
SW1(config)# spanning-tree vlan 10 priority 4096
SW1(config)# spanning-tree vlan 20 priority 4096

! Make SW2 secondary root (backup)
SW2(config)# spanning-tree vlan 10 priority 8192
SW2(config)# spanning-tree vlan 20 priority 8192

! OR use macro (simpler):
SW1(config)# spanning-tree vlan 10 root primary
SW1(config)# spanning-tree vlan 20 root primary
SW2(config)# spanning-tree vlan 10 root secondary
SW2(config)# spanning-tree vlan 20 root secondary
```

## Part 3 — Enable RSTP

```bash
! Change from 802.1D to 802.1w Rapid PVST+ on ALL switches
SW1(config)# spanning-tree mode rapid-pvst
SW2(config)# spanning-tree mode rapid-pvst
SW3(config)# spanning-tree mode rapid-pvst
```

## Part 4 — PortFast and BPDU Guard on Access Ports

```bash
! Enable on individual access ports (host-facing only — NEVER on trunk ports)
SW2(config)# interface range Fa0/1-10
SW2(config-if-range)# spanning-tree portfast
SW2(config-if-range)# spanning-tree bpduguard enable

! Enable globally on all PortFast-enabled ports
SW2(config)# spanning-tree portfast default
SW2(config)# spanning-tree portfast bpduguard default

! Set BPDU guard auto-recovery (optional)
SW2(config)# errdisable recovery cause bpduguard
SW2(config)# errdisable recovery interval 300
```

## Verification

```bash
SW1# show spanning-tree vlan 10
! Look for: "This bridge is the root"
! Root ID should show SW1's Bridge ID

SW2# show spanning-tree vlan 10
! Look for: Root Port (which port connects toward SW1)
! Alternate/Blocking port (redundant path blocked by STP)

SW1# show spanning-tree summary
! Shows counts of ports in each state per VLAN

SW2# show spanning-tree interface Fa0/1 detail
! Shows PortFast status, BPDU Guard status

! Simulate BPDU Guard triggering (connect a switch to access port)
! Port should go err-disabled immediately
SW2# show interfaces Fa0/1 status
! Expected: err-disabled
```

## STP Port States Reference
```
802.1D:  Blocking → Listening (15s) → Learning (15s) → Forwarding
802.1w:  Discarding → Learning → Forwarding (much faster, ~1-2s)
```

## Questions to Answer After Lab
1. What was the default root bridge before manual configuration?
2. What port on SW3 became the Root Port?
3. What port became Alternate (Blocking) after root election?
4. How much faster does RSTP converge vs 802.1D?
5. What happens to a port when BPDU Guard triggers?
