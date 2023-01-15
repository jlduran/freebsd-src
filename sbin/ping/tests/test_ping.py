import pytest

import re
import types
import subprocess

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


class ExpectedProcess(object):
    """An expected ping output that matches `subprocess.CompletedProcess()`.

    Attributes:
      returncode: The exit code of the process, negative for signals.
      stdout: The standard output ('' if none).
      stderr: The standard error ('' if none).
    """

    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        args = ["returncode={!r}".format(self.returncode)]
        if self.stdout is not None:
            args.append("stdout={!r}".format(self.stdout))
        if self.stderr is not None:
            args.append("stderr={!r}".format(self.stderr))
        return "{}({})".format(type(self).__name__, ", ".join(args))

    __class_getitem__ = classmethod(types.GenericAlias)


class TestPing(SingleVnetTestTemplate):
    IPV6_PREFIXES: List[str] = ["2001:db8::1/64"]
    IPV4_PREFIXES: List[str] = ["192.0.2.1/24"]

    # Each test in testdata is a tuple (args, ExpectedProcess())
    testdata = [
        pytest.param(
            "-4 -c1 -s56 -t1 localhost",
            ExpectedProcess(
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
            "-6 -c1 -s8 -t1 localhost",
            ExpectedProcess(
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
            "-A -c1 192.0.2.1",
            ExpectedProcess(
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
            "-A -c1 192.0.2.2",
            ExpectedProcess(
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
            "-A -c1 2001:db8::1",
            ExpectedProcess(
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
            "-A -c1 2001:db8::2",
            ExpectedProcess(
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
            "-A -c3 192.0.2.1",
            ExpectedProcess(
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
            "-A -c3 192.0.2.2",
            ExpectedProcess(
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
            "-A -c3 2001:db8::1",
            ExpectedProcess(
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
            "-A -c3 2001:db8::2",
            ExpectedProcess(
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
            "-c1 192.0.2.1",
            ExpectedProcess(
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
            "-c1 192.0.2.2",
            ExpectedProcess(
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
            "-c1 2001:db8::1",
            ExpectedProcess(
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
            "-c1 2001:db8::2",
            ExpectedProcess(
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
            "-c1 -S127.0.0.1 -s56 -t1 localhost",
            ExpectedProcess(
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
            "-c1 -S::1 -s8 -t1 localhost",
            ExpectedProcess(
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
            "-c3 192.0.2.1",
            ExpectedProcess(
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
            "-c3 192.0.2.2",
            ExpectedProcess(
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
            "-c3 2001:db8::1",
            ExpectedProcess(
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
            "-c3 2001:db8::2",
            ExpectedProcess(
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
            "-q -c1 192.0.2.1",
            ExpectedProcess(
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
            "-q -c1 192.0.2.2",
            ExpectedProcess(
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
            "-q -c1 2001:db8::1",
            ExpectedProcess(
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
            "-q -c1 2001:db8::2",
            ExpectedProcess(
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
            "-q -c3 192.0.2.1",
            ExpectedProcess(
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
            "-q -c3 192.0.2.2",
            ExpectedProcess(
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
            "-q -c3 2001:db8::1",
            ExpectedProcess(
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
            "-q -c3 2001:db8::2",
            ExpectedProcess(
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
            "-Wx localhost",
            ExpectedProcess(64, stderr="ping: invalid timing interval: `x'\n"),
            marks=pytest.mark.skip("Not yet implemented"),
            id="_Wx_localhost",
        ),
    ]

    @pytest.mark.parametrize("args, expected", testdata)
    def test_ping(self, args, expected):
        """Test ping"""
        ping = subprocess.run(
            f"ping {args}".split(), capture_output=True, timeout=15, text=True
        )
        assert ping.returncode == expected.returncode
        assert redact(ping.stdout) == expected.stdout
        assert ping.stderr == expected.stderr
