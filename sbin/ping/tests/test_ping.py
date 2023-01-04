import pytest

import re
import subprocess

from atf_python.sys.net.vnet import SingleVnetTestTemplate
from typing import List


@pytest.fixture(scope="function")
def Ac1_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def Ac1_192_0_2_2():
    return (
        2,
        """\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def Ac1_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def Ac1_2001_db8__2():
    return (
        2,
        """\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def Ac3_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def Ac3_192_0_2_2():
    return (
        2,
        """\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
\x07Request timeout for icmp_seq 1
\x07Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def Ac3_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def Ac3_2001_db8__2():
    return (
        2,
        """\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
\x07Request timeout for icmp_seq=1
\x07Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def c1_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def c1_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def c1_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def c1_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def c3_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def c3_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def c3_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def c3_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
Request timeout for icmp_seq=1
Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def qc1_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def qc1_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def qc1_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def qc1_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def qc3_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def qc3_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def qc3_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def qc3_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


class CheckPingStatistics(str):
    def redacted(self):
        patterns_tuple = [
            ("localhost \([0-9]{1,3}(\.[0-9]{1,3}){3}\)", "localhost"),
            ("from [0-9]{1,3}(\.[0-9]{1,3}){3}", "from"),
            ("hlim=[0-9]*", "hlim="),
            ("ttl=[0-9]*", "ttl="),
            ("time=[0-9.-]*", "time="),
            ("[0-9\.]+/[0-9.]+", "/"),
        ]
        for pattern, repl in patterns_tuple:
            self = re.sub(pattern, repl, self)
        return self


class TestPing(SingleVnetTestTemplate):
    IPV6_PREFIXES: List[str] = ["2001:db8::1/64"]
    IPV4_PREFIXES: List[str] = ["192.0.2.1/24"]

    tests = [
        ("-Ac1 192.0.2.1", "Ac1_192_0_2_1"),
        ("-Ac1 192.0.2.2", "Ac1_192_0_2_2"),
        ("-Ac1 2001:db8::1", "Ac1_2001_db8__1"),
        ("-Ac1 2001:db8::2", "Ac1_2001_db8__2"),
        ("-Ac3 192.0.2.1", "Ac3_192_0_2_1"),
        ("-Ac3 192.0.2.2", "Ac3_192_0_2_2"),
        ("-Ac3 2001:db8::1", "Ac3_2001_db8__1"),
        ("-Ac3 2001:db8::2", "Ac3_2001_db8__2"),
        ("-c1 192.0.2.1", "c1_192_0_2_1"),
        ("-c1 192.0.2.2", "c1_192_0_2_2"),
        ("-c1 2001:db8::1", "c1_2001_db8__1"),
        ("-c1 2001:db8::2", "c1_2001_db8__2"),
        ("-c3 192.0.2.1", "c3_192_0_2_1"),
        ("-c3 192.0.2.2", "c3_192_0_2_2"),
        ("-c3 2001:db8::1", "c3_2001_db8__1"),
        ("-c3 2001:db8::2", "c3_2001_db8__2"),
        ("-qc1 192.0.2.1", "qc1_192_0_2_1"),
        ("-qc1 192.0.2.2", "qc1_192_0_2_2"),
        ("-qc1 2001:db8::1", "qc1_2001_db8__1"),
        ("-qc1 2001:db8::2", "qc1_2001_db8__2"),
        ("-qc3 192.0.2.1", "qc3_192_0_2_1"),
        ("-qc3 192.0.2.2", "qc3_192_0_2_2"),
        ("-qc3 2001:db8::1", "qc3_2001_db8__1"),
        ("-qc3 2001:db8::2", "qc3_2001_db8__2"),
    ]
    test_ids = [test[1] for test in tests]

    @pytest.mark.parametrize("args, expected_fixture", tests, ids=test_ids)
    def test_ping(self, args, expected_fixture, request):
        """Test ping"""
        status, output = subprocess.getstatusoutput(f"ping {args}")
        expected = request.getfixturevalue(expected_fixture)
        assert status == expected[0]
        assert CheckPingStatistics(output).redacted() == expected[1]
