# Notes: Network Security (CCNA Phase 3)

## Port Security

Restricts which MAC addresses can connect to a switch port.
Prevents MAC flooding attacks and unauthorized device connections.

### Port Security Violation Modes
| Mode | Action on Violation | Sends Syslog? | Sends SNMP Trap? | Port Disabled? |
|------|---------------------|--------------|-----------------|----------------|
| **Protect** | Drop frames, no alert | No | No | No |
| **Restrict** | Drop frames + increment counter | Yes | Yes | No |
| **Shutdown** (default) | Err-disable port | Yes | Yes | Yes |

```bash
# Basic port security
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security

# Limit to 2 MACs
Switch(config-if)# switchport port-security maximum 2

# Sticky MAC — learn dynamically and save to config
Switch(config-if)# switchport port-security mac-address sticky

# Manual MAC address
Switch(config-if)# switchport port-security mac-address aa:bb:cc:dd:ee:ff

# Set violation mode
Switch(config-if)# switchport port-security violation restrict

# Recover from err-disabled
Switch(config-if)# shutdown
Switch(config-if)# no shutdown
# OR auto-recovery:
Switch(config)# errdisable recovery cause psecure-violation
Switch(config)# errdisable recovery interval 300

# Verify
Switch# show port-security
Switch# show port-security interface Fa0/1
Switch# show port-security address
```

---

## DHCP Snooping

Prevents rogue DHCP servers. Builds a binding table (IP + MAC + port + VLAN).

```bash
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10,20,30

# Trust only the uplink to the real DHCP server
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# ip dhcp snooping trust

# Rate-limit DHCP on untrusted ports (packets/second)
Switch(config)# interface range Fa0/1-24
Switch(config-if-range)# ip dhcp snooping limit rate 15

# Verify
Switch# show ip dhcp snooping
Switch# show ip dhcp snooping binding
```

---

## Dynamic ARP Inspection (DAI)

Validates ARP packets using the DHCP snooping binding table.
Prevents ARP poisoning / Man-in-the-Middle attacks.

```bash
Switch(config)# ip arp inspection vlan 10,20,30

# Trust uplink (towards router/DHCP server)
Switch(config-if)# ip arp inspection trust

# Rate-limit ARP on untrusted ports
Switch(config-if)# ip arp inspection limit rate 100

# Verify
Switch# show ip arp inspection
Switch# show ip arp inspection vlan 10
Switch# show ip arp inspection statistics
```

---

## 802.1X Port Authentication

Prevents unauthorized devices from accessing the network.

```
Supplicant (PC) ←→ Authenticator (Switch) ←→ Authentication Server (RADIUS)
```

```bash
# Enable AAA
Switch(config)# aaa new-model
Switch(config)# aaa authentication dot1x default group radius

# Enable 802.1X globally
Switch(config)# dot1x system-auth-control

# Enable per interface
Switch(config-if)# authentication port-control auto
Switch(config-if)# dot1x pae authenticator

# Configure RADIUS server
Switch(config)# radius server CORP-RADIUS
Switch(config-radius-server)# address ipv4 192.168.1.100 auth-port 1812 acct-port 1813
Switch(config-radius-server)# key MySharedSecret123

# Verify
Switch# show dot1x all
Switch# show authentication sessions
```

---

## SSH Hardening

```bash
# Set domain name (required for key generation)
Switch(config)# ip domain-name corp.local

# Generate RSA key (2048 bits minimum)
Switch(config)# crypto key generate rsa modulus 2048

# Enable SSH v2 only
Switch(config)# ip ssh version 2
Switch(config)# ip ssh time-out 60
Switch(config)# ip ssh authentication-retries 3

# Create local user
Switch(config)# username admin privilege 15 secret SecurePass123!

# VTY lines — SSH only, no Telnet
Switch(config)# line vty 0 4
Switch(config-line)# transport input ssh
Switch(config-line)# login local
Switch(config-line)# exec-timeout 10 0    # 10 min timeout

# Disable Telnet on console
Switch(config)# line console 0
Switch(config-line)# exec-timeout 5 0
Switch(config-line)# login local

# Disable unused services
Switch(config)# no ip http server
Switch(config)# no ip http secure-server   # if not needed
Switch(config)# no cdp run                 # on untrusted interfaces
Switch(config)# no service finger
Switch(config)# no service tcp-small-servers
Switch(config)# no service udp-small-servers
```

---

## ACL Security Best Practices

```bash
# Block RFC 1918 private IPs on external interface (anti-spoofing)
Router(config)# ip access-list extended ANTI-SPOOFING-IN
Router(config-ext-nacl)# deny ip 10.0.0.0 0.255.255.255 any
Router(config-ext-nacl)# deny ip 172.16.0.0 0.15.255.255 any
Router(config-ext-nacl)# deny ip 192.168.0.0 0.0.255.255 any
Router(config-ext-nacl)# deny ip 127.0.0.0 0.255.255.255 any
Router(config-ext-nacl)# permit ip any any

Router(config)# interface GigabitEthernet0/0     # WAN/external interface
Router(config-if)# ip access-group ANTI-SPOOFING-IN in

# Block Telnet (port 23) — enforce SSH
Router(config)# ip access-list extended BLOCK-TELNET
Router(config-ext-nacl)# deny tcp any any eq 23
Router(config-ext-nacl)# permit ip any any
```

---

## NTP (Network Time Protocol)

Critical for log accuracy, certificates, and authentication.

```bash
# Configure NTP server
Router(config)# ntp server pool.ntp.org prefer
Router(config)# ntp server 1.de.pool.ntp.org

# Set timezone (Germany)
Router(config)# clock timezone CET 1
Router(config)# clock summer-time CEST recurring last Sun Mar 2:00 last Sun Oct 3:00

# Verify
Router# show ntp status
Router# show ntp associations
Router# show clock detail
```

---

## Common Exam Questions — Security

1. **Port security default violation mode?** → Shutdown (err-disable)
2. **What does 'sticky' do in port security?** → Dynamically learns and saves MACs to config
3. **DHCP snooping trusted ports?** → Uplinks to DHCP server/router only
4. **What protocol does 802.1X use to communicate with the RADIUS server?** → EAP over RADIUS
5. **How to re-enable an err-disabled port?** → `shutdown` then `no shutdown`
6. **Minimum SSH RSA key length for CCNA?** → 768 bits minimum, 2048 recommended
