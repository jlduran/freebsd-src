#!/usr/bin/env python
#
# $FreeBSD$
#

import sys
import subprocess
import argparse
import logging
logging.getLogger("scapy").setLevel(logging.CRITICAL)

import scapy.all as sc

def parse_args():
    parser = argparse.ArgumentParser(prog="pinger.py",
                                     description="P I N G E R",
                                     epilog="This utility creates a tun "
                                     "interface, sends an echo request, and "
                                     "forges the reply.")
    # Required arguments
    # Avoid setting defaults on these arguments,
    # as we want to set them explicitly in the tests
    parser.add_argument("--iface", type=str, required=True,
                        help="Interface to send packet to")
    parser.add_argument("--src", type=str, required=True,
                        help="Source packet IP")
    parser.add_argument("--dst", type=str, required=True,
                        help="Destination packet IP")
    parser.add_argument("--icmp_type", type=int, required=True,
                        help="ICMP type")
    parser.add_argument("--icmp_code", type=int, required=True,
                        help="ICMP code")
    # IP arguments
    parser.add_argument("--flags", type=str, default="",
                        choices=["MF", "DF", "evil"],
                        help="IP flags")
    parser.add_argument("--opts", type=str, default="",
                        choices=["EOL", "NOP", "RR", "LSRR", "SSRR", "unk"],
                        help="Include IP options")
    parser.add_argument("--special", type=str, default="",
                        choices=["tcp", "udp", "wrong", "warp"],
                        help="Send a special packet")
    # ICMP arguments
    # Match names with <netinet/ip_icmp.h>
    parser.add_argument("--icmp_pptr", type=int, default=0,
                        help="ICMP pointer")
    parser.add_argument("--icmp_gwaddr", type=str, default="0.0.0.0",
                        help="ICMP gateway IP address")
    parser.add_argument("--icmp_nextmtu", type=int, default=0,
                        help="ICMP next MTU")
    parser.add_argument("--icmp_otime", type=int, default=0,
                        help="ICMP originate timestamp")
    parser.add_argument("--icmp_rtime", type=int, default=0,
                        help="ICMP receive timestamp")
    parser.add_argument("--icmp_ttime", type=int, default=0,
                        help="ICMP transmit timestamp")
    parser.add_argument("--icmp_mask", type=str, default="0.0.0.0",
                        help="ICMP address mask")
    parser.add_argument("--request", type=str, default="echo",
                        help="Request type (echo, mask, timestamp)")
    # Miscellaneous arguments
    parser.add_argument("--count", type=int, default=1,
                        help="Number of packets to send")
    parser.add_argument("--dup", action="store_true",
                        help="Duplicate packets")
    parser.add_argument("--version", action="version", version='%(prog)s 1.0')
    return parser.parse_args()

def construct_control_message(echo, ip, icmp):
    icmp.seq=echo.seq
    payload=echo.payload.payload
    oip=sc.IP(src=ip.dst, dst=ip.src, flags=ip.flags, options=ip.options)
    oicmp=sc.ICMP(type=0, code=0, id=echo.payload.id)

    if icmp.type == 0:
        icmp.id=echo.payload.id
        pkt=ip/icmp/payload
    elif icmp.type in (3, 4, 5, 11, 12):
        pkt=ip/icmp/oip/oicmp/payload
    elif icmp.type in (13, 14, 17, 18):
        icmp.id=echo.payload.id
        pkt=ip/icmp/payload
    else:
        icmp.id=echo.payload.id
        pkt=ip/icmp/oip/oicmp/payload
    return pkt

# fixme merge with previous function
def construct_special_package(echo, ip, icmp, special):
    icmp.id=echo.payload.id
    icmp.seq=echo.seq
    if special == "tcp":
        oip=sc.IP(src=ip.dst, dst=ip.src)
        oip.proto="tcp"
        tcp=sc.TCP(sport=1234, dport=5678)
        pkt=ip/icmp/oip/tcp
    elif special == "udp":
        oip=sc.IP(src=ip.dst, dst=ip.src)
        oip.proto="udp"
        udp=sc.UDP(sport=1234, dport=5678)
        pkt=ip/icmp/oip/udp
    elif special == "warp":
        # Build a package with a timestamp of INT_MAX
        # (time-warped package)
        payload_no_timestamp=sc.bytes_hex(echo.payload.payload)[16:]
        pkt=ip/icmp/((b"\xff" * 8) + sc.hex_bytes(payload_no_timestamp))
    elif special == "wrong":
        # Build a package with a wrong last byte
        payload_no_last_byte=sc.bytes_hex(echo.payload.payload)[:-2]
        pkt=ip/icmp/((sc.hex_bytes(payload_no_last_byte)) + b"\x00")
    else:
        pkt=ip/icmp
    return pkt

def generate_ip_options(opts):
    routers=["192.0.2.10", "192.0.2.20", "192.0.2.30", "192.0.2.40",
             "192.0.2.50", "192.0.2.60", "192.0.2.70", "192.0.2.80", 0]
    if opts == "EOL":
        options=sc.IPOption(b"\x00")
    elif opts == "NOP":
        options=sc.IPOption(b"\x01" * 40)
    elif opts == "RR":
        options=sc.IPOption(b"\x07")
        # options.pointer=3  # same route
        #options.length=7 # truncated route
        #options[0].routers=routers_t # truncated route
        options.pointer=40
        options[0].routers=routers
    elif opts == "LSRR":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options=sc.IPOption(b"\x83")
        options[0].routers=routers
    elif opts == "SSRR":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options=sc.IPOption(b"\x89")
        options[0].routers=routers
    elif opts == "unk":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options=sc.IPOption(b"\x99")
    else:
        options=""
    return options

def main():
    """P I N G E R"""
    args=parse_args()
    opts=generate_ip_options(args.opts)
    ip=sc.IP(flags=args.flags, src=args.dst, dst=args.src, options=opts)
    icmp=sc.ICMP(type=args.icmp_type, code=args.icmp_code,
                 ts_ori=args.icmp_otime, ts_rx=args.icmp_rtime,
                 ts_tx=args.icmp_ttime, gw=args.icmp_gwaddr,
                 ptr= args.icmp_pptr, addr_mask=args.icmp_mask,
                 nexthopmtu=args.icmp_nextmtu)
    tun=sc.TunTapInterface(args.iface)
    with open("created_interfaces.lst", "w", encoding="utf-8") as file:
        file.write(args.iface)
    subprocess.run(["ifconfig", tun.iface, "up"], check=True)
    subprocess.run(["ifconfig", tun.iface, args.src, args.dst], check=True)
    command=["/sbin/ping", "-c", str(args.count), "-t", str(args.count), "-v"]
    if args.request == "mask":
        command+=["-Mm"]
    if args.request == "timestamp":
        command+=["-Mt"]
    if args.special != "":
        command+=["-p1"]
    if args.opts in ("RR", "LSRR", "SSRR"):
        command+=["-R"]
    command+=[args.dst]
    with subprocess.Popen(
        args=command,
        text=True
    ) as ping:
        for dummy in range(args.count):
            echo=tun.recv()
            if args.special != "":
                pkt=construct_special_package(echo, ip, icmp, args.special)
            else:
                pkt=construct_control_message(echo, ip, icmp)
            tun.send(pkt)
            if args.dup is True:
                tun.send(pkt)
        ping.communicate()

    sys.exit(ping.returncode)

if __name__ == "__main__":
    main()
