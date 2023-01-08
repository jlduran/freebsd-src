import pytest

import re
import subprocess

from atf_python.sys.net.vnet import SingleVnetTestTemplate
from typing import List

# Command argument fixtures
#
# Naming convention: Replace spaces, dashes, colons with underscores.
#      Always start with an underscore.  Fixtures should be named after
#      the arguments used.
# Return: to match `getstatusoutput`, return the status
#     and the expected output.  I prefer atf-sh's separation of
#     stdout and stderr.  See if we can replicate it here, while
#     keeping it simple.  subprocess.getstatusoutput() is considered
#     a "legacy" function.
#     As a last resort, structure it as a CompletedProcess, and
#     use subprocess.run() instead.
# Description: Optionally add a brief description.
# Marks: Slow (time-out) tests should be marked as slow.
#        Scapy for (future) scapy-based tests.
#
# Not sure if these should be in a separate file?
@pytest.fixture(scope="function")
def _4_c1_s56_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    return (
        0,
        """\
PING localhost: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def _6_c1_s8_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    return (
        0,
        """\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
def _A_c1_192_0_2_1():
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
# @pytest.mark.slow # XXX evidently this won't work.
def _A_c1_192_0_2_2():
    return (
        2,
        """\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _A_c1_2001_db8__1():
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
# @pytest.mark.slow
def _A_c1_2001_db8__2():
    return (
        2,
        """\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _A_c3_192_0_2_1():
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
# @pytest.mark.slow
def _A_c3_192_0_2_2():
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
def _A_c3_2001_db8__1():
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
# @pytest.mark.slow
def _A_c3_2001_db8__2():
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
def _c1_192_0_2_1():
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
# @pytest.mark.slow
def _c1_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _c1_2001_db8__1():
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
# @pytest.mark.slow
def _c1_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _c3_192_0_2_1():
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
def _c1_S127_0_0_1_s56_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    return (
        0,
        """\
PING localhost from: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
def _c1_S__1_s8_t1_localhost():
    """Check that ping -S ::1 localhost succeeds"""
    return (
        0,
        """\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _c3_192_0_2_2():
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
def _c3_2001_db8__1():
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
# @pytest.mark.slow
def _c3_2001_db8__2():
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
def _q_c1_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c1_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _q_c1_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c1_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _q_c3_192_0_2_1():
    return (
        0,
        """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms""",
    )


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c3_192_0_2_2():
    return (
        2,
        """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


@pytest.fixture(scope="function")
def _q_c3_2001_db8__1():
    return (
        0,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms""",
    )


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c3_2001_db8__2():
    return (
        2,
        """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss""",
    )


class CheckPingStatistics(str):
    # The objective is to keep in line with ping_test.sh's
    # check_ping_statistics(), so that the redacted output
    # can be used interchangeably.
    # NB: I may update ping_test.sh as well, to account for
    #     future tests.  Also, I'm not sure if this is the best
    #     way to redact ping's output with pytest.
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
    # XXX ping_test.sh had require_ipv4/require_ipv6 methods.
    # These checks, in my opinion, should be done by the pytest framework,
    # as we should focus only on writing tests.
    IPV6_PREFIXES: List[str] = ["2001:db8::1/64"]
    IPV4_PREFIXES: List[str] = ["192.0.2.1/24"]

    # The idea is to streamline the creation of commands vs. expected output.
    # fmt: off
    tests = [
        ("-4 -c1 -s56 -t1 localhost", "_4_c1_s56_t1_localhost"),
        ("-6 -c1 -s8 -t1 localhost", "_6_c1_s8_t1_localhost"),
        ("-A -c1 192.0.2.1", "_A_c1_192_0_2_1"),
        ("-A -c1 192.0.2.2", "_A_c1_192_0_2_2"),
        ("-A -c1 2001:db8::1", "_A_c1_2001_db8__1"),
        ("-A -c1 2001:db8::2", "_A_c1_2001_db8__2"),
        ("-A -c3 192.0.2.1", "_A_c3_192_0_2_1"),
        ("-A -c3 192.0.2.2", "_A_c3_192_0_2_2"),
        ("-A -c3 2001:db8::1", "_A_c3_2001_db8__1"),
        ("-A -c3 2001:db8::2", "_A_c3_2001_db8__2"),
        ("-c1 192.0.2.1", "_c1_192_0_2_1"),
        ("-c1 192.0.2.2", "_c1_192_0_2_2"),
        ("-c1 2001:db8::1", "_c1_2001_db8__1"),
        ("-c1 2001:db8::2", "_c1_2001_db8__2"),
        ("-c1 -S127.0.0.1 -s56 -t1 localhost", "_c1_S127_0_0_1_s56_t1_localhost"),
        ("-c1 -S::1 -s8 -t1 localhost", "_c1_S__1_s8_t1_localhost"),
        ("-c3 192.0.2.1", "_c3_192_0_2_1"),
        ("-c3 192.0.2.2", "_c3_192_0_2_2"),
        ("-c3 2001:db8::1", "_c3_2001_db8__1"),
        ("-c3 2001:db8::2", "_c3_2001_db8__2"),
        ("-q -c1 192.0.2.1", "_q_c1_192_0_2_1"),
        ("-q -c1 192.0.2.2", "_q_c1_192_0_2_2"),
        ("-q -c1 2001:db8::1", "_q_c1_2001_db8__1"),
        ("-q -c1 2001:db8::2", "_q_c1_2001_db8__2"),
        ("-q -c3 192.0.2.1", "_q_c3_192_0_2_1"),
        ("-q -c3 192.0.2.2", "_q_c3_192_0_2_2"),
        ("-q -c3 2001:db8::1", "_q_c3_2001_db8__1"),
        ("-q -c3 2001:db8::2", "_q_c3_2001_db8__2"),
    ]
    test_ids = [test[1] for test in tests]

    @pytest.mark.parametrize("args, expected_fixture", tests, ids=test_ids)
    def test_ping(self, args, expected_fixture, request):
        # XXX can we parametrize the test's description
        #     without doing something too complex
        """Test ping"""
        status, output = subprocess.getstatusoutput(f"ping {args}")
        expected = request.getfixturevalue(expected_fixture)
        assert status == expected[0]
        assert CheckPingStatistics(output).redacted() == expected[1]
