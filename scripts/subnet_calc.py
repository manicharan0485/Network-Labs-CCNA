#!/usr/bin/env python3
"""
subnet_calc.py
─────────────────────────────────────────────────────────────────────────────
IPv4 Subnet Calculator — CCNA study tool.

Given an IP address and prefix length (or subnet mask), calculates:
  - Network address
  - Broadcast address
  - First and last usable host
  - Number of usable hosts
  - Subnet mask and wildcard mask
  - Binary representation

Also supports VLSM (Variable Length Subnet Mask) planning.

Usage:
    python subnet_calc.py 192.168.1.0/24
    python subnet_calc.py 10.0.0.0/8
    python subnet_calc.py 172.16.50.128/26
    python subnet_calc.py --vlsm 192.168.1.0/24 50 30 14 6 2

Author:  Manicharan Ravi
Version: 1.1.0 (CCNA study tool)
"""

import argparse
import ipaddress


def subnet_info(cidr: str) -> dict:
    """Calculate all subnet information for a given CIDR."""
    network  = ipaddress.IPv4Network(cidr, strict=False)
    hosts    = list(network.hosts())
    mask     = network.netmask
    wildcard = network.hostmask

    return {
        "network":       str(network.network_address),
        "broadcast":     str(network.broadcast_address),
        "mask":          str(mask),
        "wildcard":      str(wildcard),
        "prefix":        network.prefixlen,
        "first_host":    str(hosts[0]) if hosts else "N/A",
        "last_host":     str(hosts[-1]) if hosts else "N/A",
        "usable_hosts":  len(hosts),
        "total_ips":     network.num_addresses,
        "cidr":          str(network),
        "network_bin":   format(int(network.network_address), '032b'),
        "mask_bin":      format(int(mask), '032b'),
    }


def print_subnet_info(info: dict, ip: str = "") -> None:
    """Pretty-print subnet details."""
    print(f"\n{'='*54}")
    print(f"  Subnet: {info['cidr']}")
    if ip:
        print(f"  Host IP: {ip}")
    print(f"{'='*54}")
    print(f"  Network Address  : {info['network']}")
    print(f"  Subnet Mask      : {info['mask']}  (/{info['prefix']})")
    print(f"  Wildcard Mask    : {info['wildcard']}")
    print(f"  Broadcast        : {info['broadcast']}")
    print(f"  First Usable     : {info['first_host']}")
    print(f"  Last Usable      : {info['last_host']}")
    print(f"  Usable Hosts     : {info['usable_hosts']:,}")
    print(f"  Total IPs        : {info['total_ips']:,}")
    print(f"\n  Binary:")
    nb = info['network_bin']
    mb = info['mask_bin']
    prefix = info['prefix']
    # Display with dots every 8 bits and highlight network/host portions
    net_part  = nb[:prefix].replace('', ' ')[1:-1]
    host_part = nb[prefix:].replace('', ' ')[1:-1]
    print(f"  Network: [{net_part}] [{host_part}]")
    mask_disp = '.'.join(mb[i:i+8] for i in range(0, 32, 8))
    net_disp  = '.'.join(nb[i:i+8] for i in range(0, 32, 8))
    print(f"  IP Bin : {net_disp}")
    print(f"  Mask   : {mask_disp}")
    print(f"{'='*54}\n")


def vlsm_plan(base_network: str, requirements: list[int]) -> None:
    """
    VLSM subnet planning.
    Given a base network and list of host requirements (descending order),
    allocate the smallest possible subnet for each requirement.
    """
    # Sort requirements descending (allocate largest first)
    requirements_sorted = sorted(requirements, reverse=True)

    print(f"\n{'='*70}")
    print(f"  VLSM Plan for: {base_network}")
    print(f"  Requirements : {requirements_sorted} hosts")
    print(f"{'='*70}")
    print(f"  {'Subnet':<20} {'Hosts Needed':>12} {'Usable':>8} {'Prefix':>8} {'Network':>18} {'Broadcast':>16}")
    print(f"  {'-'*18} {'-'*12} {'-'*8} {'-'*8} {'-'*18} {'-'*16}")

    base        = ipaddress.IPv4Network(base_network, strict=True)
    subnets     = base.subnets(new_prefix=base.prefixlen)
    allocated   = []
    next_network = base

    for req in requirements_sorted:
        # Find smallest prefix that fits this requirement
        # 2^(32-prefix) - 2 >= req
        needed_prefix = 32
        while needed_prefix > 0:
            if (2 ** (32 - needed_prefix) - 2) >= req:
                break
            needed_prefix -= 1

        # Find next available subnet of this size
        candidate = ipaddress.IPv4Network(f"{next_network.network_address}/{needed_prefix}", strict=False)
        # Make sure it doesn't overlap with allocated
        while any(candidate.overlaps(a) for a in allocated):
            next_addr = int(candidate.broadcast_address) + 1
            candidate = ipaddress.IPv4Network(f"{ipaddress.IPv4Address(next_addr)}/{needed_prefix}", strict=False)

        allocated.append(candidate)
        hosts_list = list(candidate.hosts())
        usable = len(hosts_list)
        first  = str(hosts_list[0]) if hosts_list else "N/A"
        last   = str(hosts_list[-1]) if hosts_list else "N/A"

        print(f"  {str(candidate):<20} {req:>12} {usable:>8} {needed_prefix:>7}  "
              f"{str(candidate.network_address):>18} {str(candidate.broadcast_address):>16}")

        # Update next available network
        next_addr = int(candidate.broadcast_address) + 1
        next_network = ipaddress.IPv4Network(
            f"{ipaddress.IPv4Address(next_addr)}/{base.prefixlen}", strict=False
        )

    print(f"\n  Total address space used: {sum(n.num_addresses for n in allocated)} IPs")
    print(f"  Remaining in {base_network}: {base.num_addresses - sum(n.num_addresses for n in allocated)} IPs")
    print(f"{'='*70}\n")


def subnet_table(base: str) -> None:
    """Print a subnetting table for common prefix lengths."""
    network = ipaddress.IPv4Network(base, strict=False)
    base_prefix = network.prefixlen

    print(f"\nSubnet table for {base}:")
    print(f"{'Prefix':<8} {'Subnet Mask':<18} {'Hosts':<10} {'Subnets from /{base_prefix}'}")
    print("-" * 60)

    for prefix in range(max(base_prefix, 24), 33):
        mask   = ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask
        hosts  = 2 ** (32 - prefix) - 2
        subnets = 2 ** (prefix - base_prefix)
        if hosts < 0:
            hosts = 0
        print(f"/{prefix:<7} {str(mask):<18} {hosts:<10} {subnets}")


def main():
    parser = argparse.ArgumentParser(
        description="IPv4 Subnet Calculator — CCNA study tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("cidr", nargs="?", help="IP/prefix, e.g. 192.168.1.0/24")
    parser.add_argument("--vlsm", metavar="NETWORK", help="Base network for VLSM planning")
    parser.add_argument("requirements", nargs="*", type=int, help="Host requirements for VLSM")
    parser.add_argument("--table", action="store_true", help="Show subnet table")
    args = parser.parse_args()

    if args.vlsm and args.requirements:
        vlsm_plan(args.vlsm, args.requirements)
        return

    if args.cidr:
        try:
            # Handle both "192.168.1.10/24" and "192.168.1.0/24"
            parts  = args.cidr.split("/")
            ip     = parts[0]
            prefix = parts[1] if len(parts) > 1 else "24"
            cidr   = f"{ip}/{prefix}"

            info = subnet_info(cidr)
            print_subnet_info(info, ip)

            if args.table:
                subnet_table(f"{info['network']}/{prefix}")

        except ValueError as e:
            print(f"Error: {e}")
            print("Example: python subnet_calc.py 192.168.1.0/24")
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python subnet_calc.py 192.168.1.0/24")
        print("  python subnet_calc.py 172.16.50.128/26")
        print("  python subnet_calc.py --vlsm 192.168.1.0/24 50 30 14 6 2")


if __name__ == "__main__":
    main()
