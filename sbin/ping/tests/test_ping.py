import pytest

import logging
import re
import types
import subprocess

logging.getLogger("scapy").setLevel(logging.CRITICAL)
import scapy.all as sc

from atf_python.sys.net.vnet import SingleVnetTestTemplate
from typing import List


def redact(output):
    """Redact some elements of ping's output."""
    patterns_tuple = [
        ("localhost \([0-9]{1,3}(\.[0-9]{1,3}){3}\)", "localhost"),
        ("from [0-9]{1,3}(\.[0-9]{1,3}){3}", "from"),
        ("hlim=[0-9]*", "hlim="),
        ("ttl=[0-9]*", "ttl="),
        ("time=[0-9.-]*", "time="),
        ("[0-9\.]+/[0-9.]+", "/"),
    ]
    for pattern, repl in patterns_tuple:
        output = re.sub(pattern, repl, output)
    return output


def create_tun_iface(src, dst):
    completed_process = subprocess.run(
        "ifconfig tun create",
        capture_output=True,
        shell=True,
        check=True,
        text=True,
    )
    tun_iface = completed_process.stdout.strip()
    subprocess.run(f"ifconfig {tun_iface} up", shell=True, check=True)
    subprocess.run(f"ifconfig {tun_iface} {src} {dst}", shell=True, check=True)
    return tun_iface


def construct_response_packet(echo, ip, icmp, special):
    icmp_id_seq_types = [0, 8, 13, 14, 15, 16, 17, 18, 37, 38]
    oip = echo[sc.IP]
    oicmp = echo[sc.ICMP]
    load = echo[sc.ICMP].payload
    oip[sc.IP].remove_payload()
    oicmp[sc.ICMP].remove_payload()
    oicmp.type = 8

    # As if the original IP packet had these set
    oip.ihl = None
    oip.len = None
    oip.id = 1
    oip.flags = ip.flags
    oip.chksum = None
    oip.options = ip.options

    # Special options
    if special == "tcp":
        oip.proto = "tcp"
        tcp = sc.TCP(sport=1234, dport=5678)
        return ip / icmp / oip / tcp
    if special == "udp":
        oip.proto = "udp"
        udp = sc.UDP(sport=1234, dport=5678)
        return ip / icmp / oip / udp
    if special == "warp":
        # Build a package with a timestamp of INT_MAX
        # (time-warped package)
        payload_no_timestamp = sc.bytes_hex(load)[16:]
        load = (b"\xff" * 8) + sc.hex_bytes(payload_no_timestamp)
    if special == "wrong":
        # Build a package with a wrong last byte
        payload_no_last_byte = sc.bytes_hex(load)[:-2]
        load = (sc.hex_bytes(payload_no_last_byte)) + b"\x00"

    if icmp.type in icmp_id_seq_types:
        pkt = ip / icmp / load
    else:
        ip.options = ""
        pkt = ip / icmp / oip / oicmp / load
    return pkt


def generate_ip_options(opts):
    routers = [
        "192.0.2.10",
        "192.0.2.20",
        "192.0.2.30",
        "192.0.2.40",
        "192.0.2.50",
        "192.0.2.60",
        "192.0.2.70",
        "192.0.2.80",
        "192.0.2.90",
    ]
    routers_zero = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    if opts == "EOL":
        options = sc.IPOption(b"\x00")
    elif opts == "NOP":
        options = sc.IPOption(b"\x01")
    elif opts == "NOP-40":
        options = sc.IPOption(b"\x01" * 40)
    elif opts == "RR":
        options = sc.IPOption_RR(pointer=40, routers=routers)
    elif opts == "RR-same":
        options = sc.IPOption_RR(pointer=3, routers=routers_zero)
    elif opts == "RR-trunc":
        options = sc.IPOption_RR(length=7, routers=routers_zero)
    elif opts == "LSRR":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption_LSRR(routers=routers)
    elif opts == "LSRR-trunc":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption_LSRR(length=3, routers=routers_zero)
    elif opts == "SSRR":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption_SSRR(routers=routers)
    elif opts == "SSRR-trunc":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption_SSRR(length=3, routers=routers_zero)
    elif opts == "unk":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption(b"\x9f")
    elif opts == "unk-40":
        subprocess.run(["sysctl", "net.inet.ip.process_options=0"], check=True)
        options = sc.IPOption(b"\x9f" * 40)
    else:
        options = ""
    return options


# XXX This will be converted to a class
def pinger(src, dst, icmp_type, icmp_code, opts):
    """P I N G E R

    Echo reply faker.

    Returns a CompletedProcess instance.

    Attributes:
      src: The source IP address.
      dst: The destination IP address.
      icmp_type: The ICMP type.
      icmp_code: The ICMP code.
    """
    iface = create_tun_iface(src, dst)
    tun = sc.TunTapInterface(iface)
    opts = generate_ip_options(opts)
    ip = sc.IP(src=dst, dst=src, options=opts)
    command = f"/sbin/ping -v -c1 -t1 {dst}"
    special = ""
    with subprocess.Popen(
        args=command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as ping:
        echo = tun.recv()
        icmp = sc.ICMP(
            type=icmp_type,
            code=icmp_code,
            id=echo[sc.ICMP].id,
            seq=echo[sc.ICMP].seq,
        )
        pkt = construct_response_packet(echo, ip, icmp, special)
        tun.send(pkt)
        stdout, stderr = ping.communicate()
    return subprocess.CompletedProcess(
        ping.args, ping.returncode, stdout, stderr
    )


class TestPing(SingleVnetTestTemplate):
    IPV6_PREFIXES: List[str] = ["2001:db8::1/64"]
    IPV4_PREFIXES: List[str] = ["192.0.2.1/24"]

    # Each test in testdata is an expected subprocess.CompletedProcess()
    testdata = [
        pytest.param(
            subprocess.CompletedProcess(
                "ping -4 -c1 -s56 -t1 localhost",
                0,
                stdout="""\
PING localhost: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_4_c1_s56_t1_localhost",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -6 -c1 -s8 -t1 localhost",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_6_c1_s8_t1_localhost",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c1 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_A_c1_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c1 192.0.2.2",
                2,
                stdout="""\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_A_c1_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c1 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_A_c1_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c1 2001:db8::2",
                2,
                stdout="""\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_A_c1_2001_db8__2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c3 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_A_3_192_0.2.1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c3 192.0.2.2",
                2,
                stdout="""\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
\x07Request timeout for icmp_seq 1
\x07Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_A_c3_192_0_2_2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c3 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_A_c3_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -A -c3 2001:db8::2",
                2,
                stdout="""\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
\x07Request timeout for icmp_seq=1
\x07Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_A_c3_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_c1_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 192.0.2.2",
                2,
                stdout="""\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_c1_192_0_2_2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_c1_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 2001:db8::2",
                2,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_c1_2001_db8__2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 -S127.0.0.1 -s56 -t1 localhost",
                0,
                stdout="""\
PING localhost from: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_c1_S127_0_0_1_s56_t1_localhost",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c1 -S::1 -s8 -t1 localhost",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_c1_S__1_s8_t1_localhost",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c3 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_c3_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c3 192.0.2.2",
                2,
                stdout="""\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_c3_192_0_2_2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c3 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_c3_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -c3 2001:db8::2",
                2,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
Request timeout for icmp_seq=1
Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_c3_2001_db8__2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c1 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_q_c1_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c1 192.0.2.2",
                2,
                stdout="""\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_q_c1_192_0_2_2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c1 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_q_c1_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c1 2001:db8::2",
                2,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_q_c1_2001_db8__2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c3 192.0.2.1",
                0,
                stdout="""\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
""",
            ),
            id="_q_c3_192_0_2_1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c3 192.0.2.2",
                2,
                stdout="""\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_q_c3_192_0_2_2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c3 2001:db8::1",
                0,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
""",
            ),
            id="_q_c3_2001_db8__1",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -q -c3 2001:db8::2",
                2,
                stdout="""\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
""",
            ),
            id="_q_c3_2001_db8__2",
        ),
        pytest.param(
            subprocess.CompletedProcess(
                "ping -Wx localhost",
                64,
                stderr="ping: invalid timing interval: `x'\n",
            ),
            marks=pytest.mark.skip("XXX currently failing"),
            id="_Wx_localhost",
        ),
    ]

    @pytest.mark.parametrize("expected", testdata)
    def test_ping(self, expected):
        """Test ping"""
        ping = subprocess.run(
            expected.args.split(), capture_output=True, timeout=15, text=True
        )
        assert ping.returncode == expected.returncode
        assert redact(ping.stdout) == str(expected.stdout or "")
        assert ping.stderr == str(expected.stderr or "")

    # XXX The following scapy based tests will probably be parameterized as well
    def test_pinger_0_0(self):
        """Test an echo reply"""
        ping = pinger("192.0.2.1", "192.0.2.2", 0, 0, "")
        expected_stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
        assert ping.returncode == 0
        assert redact(ping.stdout) == expected_stdout
        assert ping.stderr == ""

    def test_pinger_0_0_NOP_40(self):
        """Test an echo reply with 40 NOP IP options"""
        ping = pinger("192.0.2.1", "192.0.2.2", 0, 0, "NOP-40")
        expected_stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
wrong total length 124 instead of 84
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP
NOP

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
        assert ping.returncode == 0
        assert redact(ping.stdout) == expected_stdout
        assert ping.stderr == ""

    # @pytest.mark.skip("XXX currently failing")
    def test_pinger_3_1_NOP_40(self):
        """Test a destination host unreachable reply with 40 NOP IP options"""
        ping = pinger("192.0.2.1", "192.0.2.2", 3, 1, "NOP-40")
        expected_stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
132 bytes from 192.0.2.2: Destination Host Unreachable
Vr HL TOS  Len   ID Flg  off TTL Pro  cks      Src      Dst
 4  f  00 007c 0001   0 0000  40  01 d868 192.0.2.1  192.0.2.2 01010101010101010101010101010101010101010101010101010101010101010101010101010101

Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
        assert ping.returncode == 2
        assert ping.stdout == expected_stdout
        assert ping.stderr == ""
