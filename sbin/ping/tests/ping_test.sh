#
# SPDX-License-Identifier: BSD-2-Clause-FreeBSD
#
# Copyright (C) 2019 Jan Sucan <jansucan@FreeBSD.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# $FreeBSD$

require_ipv4()
{
	if ! getaddrinfo -f inet localhost 1>/dev/null 2>&1; then
		atf_skip "IPv4 is not configured"
	fi
}
require_ipv6()
{
	if ! getaddrinfo -f inet6 localhost 1>/dev/null 2>&1; then
		atf_skip "IPv6 is not configured"
	fi
}

atf_test_case ping_c1_s56_t1
ping_c1_s56_t1_head()
{
	atf_set "descr" "Stop after receiving 1 ECHO_RESPONSE packet"
}
ping_c1_s56_t1_body()
{
	require_ipv4
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -4 -c 1 -s 56 -t 1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_c1_s56_t1.out
}

atf_test_case ping_c1_s56_t1_S127_0_0_1
ping_c1_s56_t1_S127_0_0_1_head()
{
	atf_set "descr" "Check that ping -S 127.0.0.1 localhost succeeds"
}
ping_c1_s56_t1_S127_0_0_1_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -c 1 -s 56 -t 1 -S 127.0.0.1 localhost
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_c1_s56_t1_S127_0_0_1.out
}

atf_test_case ping_6_c1_s8_t1
ping_6_c1_s8_t1_head()
{
	atf_set "descr" "Stop after receiving 1 ECHO_RESPONSE packet"
}
ping_6_c1_s8_t1_body()
{
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -6 -c 1 -s 8 -t 1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_6_c1_s8_t1.out
}

atf_test_case ping_c1_s8_t1_S__1
ping_c1_s8_t1_S__1_head()
{
	atf_set "descr" "Check that ping -S ::1 localhost succeeds"
}
ping_c1_s8_t1_S__1_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -c 1 -s 8 -t 1 -S ::1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_c1_s8_t1_S__1.out
}

atf_test_case ping6_c1_s8_t1
ping6_c1_s8_t1_head()
{
	atf_set "descr" "Use IPv6 when invoked as ping6"
}
ping6_c1_s8_t1_body()
{
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping6 -c 1 -s 8 -t 1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_6_c1_s8_t1.out
}

ping_c1_t6_head()
{
	atf_set "descr" "-t6 is not interpreted as -t -6 by ping"
}
ping_c1_t6_body()
{
	require_ipv4
	atf_check -s exit:0 -o ignore -e empty ping -c1 -t6 127.0.0.1
}

ping6_c1_t4_head()
{
	atf_set "descr" "-t4 is not interpreted as -t -4 by ping6"
}
ping6_c1_t4_body()
{
	require_ipv6
	atf_check -s exit:0 -o ignore -e empty ping6 -c1 -t4 ::1
}

ping_4_6_head()
{
	atf_set "descr" "-4 and -6 cannot be used simultaneously"
}
ping_4_6_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:1 \
	    -e match:"-4 and -6 cannot be used simultaneously" \
	    ping -4 -6 localhost
}

ping6_4_6_head()
{
	atf_set "descr" "-4 and -6 cannot be used simultaneously"
}
ping6_4_6_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:1 \
	    -e match:"-4 and -6 cannot be used simultaneously" \
	    ping6 -4 -6 localhost
}

ping_4__1_head()
{
	atf_set "descr" "-4 cannot ping an IPv6 address"
	require_ipv4
	require_ipv6
}
ping_4__1_body()
{
	atf_check -s exit:1 \
	    -e match:"IPv4 requested but IPv6 target address provided" \
	    ping -4 ::1
}

ping_6_127_0_0_1_head()
{
	atf_set "descr" "-6 cannot ping an IPv4 address"
	require_ipv4
	require_ipv6
}
ping_6_127_0_0_1_body()
{
	atf_check -s exit:1 \
	    -e match:"IPv6 requested but IPv4 target address provided" \
	    ping -6 127.0.0.1
}

ping_unknown_head()
{
	atf_set "descr" "Unknown host"
	require_ipv4
}
ping_unknown_body()
{
	atf_check -s exit:1 \
	    -e match:"Unknown host" \
	    ping unknown
}

ping6_unknown_head()
{
	atf_set "descr" "Unknown host"
	require_ipv6
}
ping6_unknown_body()
{
	atf_skip "WIP make an unknown host"
	atf_check -s exit:1 \
	    -e match:"Unknown host" \
	    ping6 unknown
}

ping_A_c2_t2_192_0_2_0_head()
{
	atf_set "descr" "Audible character when no packet is received"
	require_ipv4
}
ping_A_c2_t2_192_0_2_0_body()
{
	atf_check -s exit:2 \
	    -o save:std.out \
	    ping -A -c 2 -t 2 192.0.2.0
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_A_c2_t2_192_0_2_0.out
}

ping_a_c1_t1_localhost_head()
{
	atf_set "descr" "Audible character when a packet is received"
	require_ipv4
}
ping_a_c1_t1_localhost_body()
{
	atf_check -s exit:0 \
	    -o save:std.out \
	    ping -a -c 1 -t 1 localhost
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_a_c1_t1_localhost.out
}

ping_c1_f_t1_localhost_head()
{
	atf_set "descr" "Flood ping"
	atf_set require.user root
	require_ipv4
}
ping_c1_f_t1_localhost_body()
{
	atf_check -s exit:0 \
	    -o save:std.out \
	    ping -c 1 -f -t 1 localhost
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_c1_f_t1_localhost.out
}

ping_c1_H_t1_127_0_0_1_head()
{
	atf_set "descr" "Hostname output"
	require_ipv4
}
ping_c1_H_t1_127_0_0_1_body()
{
	atf_check -s exit:0 \
	    -o save:std.out \
	    ping -c 1 -H -t 1 127.0.0.1
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_c1_H_t1_127_0_0_1.out
}

atf_init_test_cases()
{
	atf_add_test_case ping_c1_s56_t1
	atf_add_test_case ping_c1_s56_t1_S127_0_0_1
	atf_add_test_case ping_6_c1_s8_t1
	atf_add_test_case ping_c1_s8_t1_S__1
	atf_add_test_case ping6_c1_s8_t1
	atf_add_test_case ping_c1_t6
	atf_add_test_case ping6_c1_t4
	atf_add_test_case ping_4_6
	atf_add_test_case ping6_4_6
	atf_add_test_case ping_4__1
	atf_add_test_case ping_6_127_0_0_1
	atf_add_test_case ping_unknown
	atf_add_test_case ping6_unknown
	atf_add_test_case ping_A_c2_t2_192_0_2_0
	atf_add_test_case ping_a_c1_t1_localhost
	atf_add_test_case ping_c1_f_t1_localhost
	atf_add_test_case ping_c1_H_t1_127_0_0_1
}

check_ping_statistics()
{
	sed -e 's/0.[0-9]\{3\}//g' \
	    -e 's/[1-9][0-9]*.[0-9]\{3\}//g' \
	    -e 's/localhost ([0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{1,3\})/localhost/' \
	    -e 's/from [0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{1,3\}/from/' \
	    -e 's/ttl=[0-9][0-9]*/ttl=/' \
	    -e 's/hlim=[0-9][0-9]*/hlim=/' \
	    "$1" >"$1".filtered
	atf_check -s exit:0 diff -u "$1".filtered "$2"
}
