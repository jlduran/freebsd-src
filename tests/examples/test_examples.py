import pytest
from atf_python.utils import BaseTest
from atf_python.sys.net.tools import ToolsHelper
from atf_python.sys.net.vnet import SingleVnetTestTemplate
from atf_python.sys.net.vnet import VnetTestTemplate
from atf_python.sys.net.vnet import VnetInstance

import errno
import socket
import subprocess
import json

from typing import List


# Test classes should be inherited
# from the BaseTest


class TestExampleSimple(BaseTest):
    @pytest.mark.require_user("root")
    def test_root(self):
        assert subprocess.getoutput("id -un") == "root"

    @pytest.mark.require_user("unprivileged")
    def test_unprivileged(self):
        assert subprocess.getoutput("id -un") != "root"

    @pytest.mark.parametrize(
        "user_tuple",
        [
            pytest.param(
                ["id -un", "root"],
                marks=pytest.mark.require_user("root"),
                id="root",
            ),
            pytest.param(
                ["id -un", "tests"],
                marks=pytest.mark.require_user("unprivileged"),
                id="unprivileged",
            ),
        ],
    )
    def test_parametrize_require_user(self, user_tuple):
        command, output = user_tuple
        assert output in subprocess.getoutput(command)


class TestSingleVnetTestTemplate(SingleVnetTestTemplate):
    @pytest.mark.require_user("root")
    def test_root(self):
        assert subprocess.getoutput("id -un") == "root"

    @pytest.mark.require_user("unprivileged")
    def test_unprivileged(self):
        assert subprocess.getoutput("id -un") != "root"

    @pytest.mark.parametrize(
        "user_tuple",
        [
            pytest.param(
                ["id -un", "root"],
                marks=pytest.mark.require_user("root"),
                id="root",
            ),
            pytest.param(
                ["id -un", "tests"],
                marks=pytest.mark.require_user("unprivileged"),
                id="unprivileged",
            ),
        ],
    )
    def test_parametrize_require_user(self, user_tuple):
        command, output = user_tuple
        assert output in subprocess.getoutput(command)


class TestVnetTestTemplate(VnetTestTemplate):
    TOPOLOGY = {
        "vnet1": {"ifaces": ["if1", "if2"]},
        "vnet2": {"ifaces": ["if1", "if2"]},
        "if1": {"prefixes6": [("2001:db8:a::1/64", "2001:db8:a::2/64")]},
        "if2": {"prefixes6": [("2001:db8:b::1/64", "2001:db8:b::2/64")]},
    }

    def _get_iface_stat(self, os_ifname: str):
        out = ToolsHelper.get_output(
            "{} -I {} --libxo json".format(ToolsHelper.NETSTAT_PATH, os_ifname)
        )
        js = json.loads(out)
        return js["statistics"]["interface"][0]

    def vnet2_handler(self, vnet: VnetInstance):
        """
        Test handler that runs in the vnet2 as a separate process.

        This handler receives an interface name, fetches received/sent packets
         and returns this data back to the parent process.
        """
        while True:
            # receives 'ifX' with an infinite timeout
            iface_alias = self.wait_object(vnet.pipe, None)
            # Translates topology interface name to the actual OS-assigned name
            os_ifname = vnet.iface_alias_map[iface_alias].name
            self.send_object(vnet.pipe, self._get_iface_stat(os_ifname))

    @pytest.mark.require_user("root")
    def test_root(self):
        assert subprocess.getoutput("id -un") == "root"

    @pytest.mark.require_user("unprivileged")
    def test_unprivileged(self):
        assert subprocess.getoutput("id -un") != "root"

    @pytest.mark.parametrize(
        "user_tuple",
        [
            pytest.param(
                ["id -un", "root"],
                marks=pytest.mark.require_user("root"),
                id="root",
            ),
            pytest.param(
                ["id -un", "tests"],
                marks=pytest.mark.require_user("unprivileged"),
                id="unprivileged",
            ),
        ],
    )
    def test_parametrize_require_user(self, user_tuple):
        command, output = user_tuple
        assert output in subprocess.getoutput(command)
