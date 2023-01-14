import pytest

import re
import types
import subprocess

from atf_python.sys.net.vnet import SingleVnetTestTemplate
from typing import List


# XXX Command argument fixtures
#
# Naming convention: Replace spaces, dashes, colons with underscores.
#      Fixtures should be named after the arguments used.
# Return: A subprocess.CompletedProcess-like ExpectedProcess (without args).
# Description: Optionally add a brief description.
# Marks: slow (time-out) tests should be marked as slow.
#             (not yet implemented/supported by kyua?).
#        scapy for (future) Scapy-based tests.
#
# Not sure if these should be in a separate file?
@pytest.fixture(scope="function")
def _4_c1_s56_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    returncode = 0
    stdout = """\
PING localhost: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _6_c1_s8_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _A_c1_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow # XXX evidently this won't work.
def _A_c1_192_0_2_2():
    returncode = 2
    stdout = """\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _A_c1_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _A_c1_2001_db8__2():
    returncode = 2
    stdout = """\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _A_c3_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _A_c3_192_0_2_2():
    returncode = 2
    stdout = """\
\x07PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
\x07Request timeout for icmp_seq 1
\x07Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _A_c3_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _A_c3_2001_db8__2():
    returncode = 2
    stdout = """\
\x07PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
\x07Request timeout for icmp_seq=1
\x07Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c1_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _c1_192_0_2_2():
    returncode = 2
    stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c1_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _c1_2001_db8__2():
    returncode = 2
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c3_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms
64 bytes from: icmp_seq=1 ttl= time= ms
64 bytes from: icmp_seq=2 ttl= time= ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c1_S127_0_0_1_s56_t1_localhost():
    """Stop after receiving 1 ECHO_RESPONSE packet"""
    returncode = 0
    stdout = """\
PING localhost from: 56 data bytes
64 bytes from: icmp_seq=0 ttl= time= ms

--- localhost ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c1_S__1_s8_t1_localhost():
    """Check that ping -S ::1 localhost succeeds"""
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) ::1 --> ::1
16 bytes from ::1, icmp_seq=0 hlim= time= ms

--- localhost ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _c3_192_0_2_2():
    returncode = 2
    stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _c3_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1
16 bytes from 2001:db8::1, icmp_seq=0 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=1 hlim= time= ms
16 bytes from 2001:db8::1, icmp_seq=2 hlim= time= ms

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _c3_2001_db8__2():
    returncode = 2
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2
Request timeout for icmp_seq=0
Request timeout for icmp_seq=1
Request timeout for icmp_seq=2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _q_c1_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c1_192_0_2_2():
    returncode = 2
    stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _q_c1_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c1_2001_db8__2():
    returncode = 2
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
1 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _q_c3_192_0_2_1():
    returncode = 0
    stdout = """\
PING 192.0.2.1 (192.0.2.1): 56 data bytes

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c3_192_0_2_2():
    returncode = 2
    stdout = """\
PING 192.0.2.2 (192.0.2.2): 56 data bytes

--- 192.0.2.2 ping statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _q_c3_2001_db8__1():
    returncode = 0
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::1

--- 2001:db8::1 ping6 statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/std-dev = /// ms
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
# @pytest.mark.slow
def _q_c3_2001_db8__2():
    returncode = 2
    stdout = """\
PING6(56=40+8+8 bytes) 2001:db8::1 --> 2001:db8::2

--- 2001:db8::2 ping6 statistics ---
3 packets transmitted, 0 packets received, 100.0% packet loss
"""
    return ExpectedProcess(returncode, stdout=stdout)


@pytest.fixture(scope="function")
def _Wx_localhost():
    returncode = 64
    stderr = "ping: invalid timing interval: `x'\n"
    return ExpectedProcess(returncode, stderr=stderr)


# XXX Choose a better name?
def methodize(args):
    if args[0] == "-":
        leading = "_"
    else:
        leading = ""
    return leading + ("_").join(
        args.replace("-", "").replace(".", "_").replace(":", "_").split()
    )


# The objective is to keep in line with ping_test.sh's
# check_ping_statistics(), so that the redacted output
# can be used interchangeably.
# NB: I may update ping_test.sh as well, to account for
#     future tests.  Also, I'm not sure if this is the best
#     way to redact ping's output with pytest.
def redact(output):
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


# XXX Better name?
# XXX Or add args and use subprocess.CompletedProcess instead?
class ExpectedProcess(object):
    """An expected ping output.

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
    # XXX ping_test.sh has require_ipv4/require_ipv6 methods.
    # These checks, in my opinion, should be done by atf-python,
    # as we should focus only on writing tests.
    IPV6_PREFIXES: List[str] = ["2001:db8::1/64"]
    IPV4_PREFIXES: List[str] = ["192.0.2.1/24"]

    # nota bene:
    # The main idea is to streamline the creation of a
    # command to be tested vs. expected output by leveraging
    # pytest's parametrization.  Any feedback is welcomed.
    # Achieving the same goal with atf-sh is not so simple and
    # very repetitive.
    #
    # fmt: off
    tests = [
        "-4 -c1 -s56 -t1 localhost",
        "-6 -c1 -s8 -t1 localhost",
        "-A -c1 192.0.2.1",
        "-A -c1 192.0.2.2",
        "-A -c1 2001:db8::1",
        "-A -c1 2001:db8::2",
        "-A -c3 192.0.2.1",
        "-A -c3 192.0.2.2",
        "-A -c3 2001:db8::1",
        "-A -c3 2001:db8::2",
        "-c1 192.0.2.1",
        "-c1 192.0.2.2",
        "-c1 2001:db8::1",
        "-c1 2001:db8::2",
        "-c1 -S127.0.0.1 -s56 -t1 localhost",
        "-c1 -S::1 -s8 -t1 localhost",
        "-c3 192.0.2.1",
        "-c3 192.0.2.2",
        "-c3 2001:db8::1",
        "-c3 2001:db8::2",
        "-q -c1 192.0.2.1",
        "-q -c1 192.0.2.2",
        "-q -c1 2001:db8::1",
        "-q -c1 2001:db8::2",
        "-q -c3 192.0.2.1",
        "-q -c3 192.0.2.2",
        "-q -c3 2001:db8::1",
        "-q -c3 2001:db8::2",
        "-Wx localhost",
    ]
    test_ids = [methodize(test) for test in tests]

    @pytest.mark.parametrize("args", tests, ids=test_ids)
    def test_ping(self, args, request):
        """Test ping"""
        ping = subprocess.run(f"ping {args}".split(), capture_output=True,
                              timeout=10, text=True)
        expected = request.getfixturevalue(methodize(args))
        assert ping.returncode == expected.returncode
        assert redact(ping.stdout) == expected.stdout
        assert ping.stderr == expected.stderr
