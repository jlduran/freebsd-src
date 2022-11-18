#!/usr/bin/env atf-sh
#
# SPDX-License-Identifier: BSD-2-Clause
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

. $(atf_get_srcdir)/common.subr

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

atf_test_case ping_c1_s56_t1_S127
ping_c1_s56_t1_S127_head()
{
	atf_set "descr" "Check that ping -S 127.0.0.1 localhost succeeds"
}
ping_c1_s56_t1_S127_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -c 1 -s 56 -t 1 -S 127.0.0.1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_c1_s56_t1_S127.out
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

atf_test_case ping_c1_s8_t1_S1
ping_c1_s8_t1_S1_head()
{
	atf_set "descr" "Check that ping -S ::1 localhost succeeds"
}
ping_c1_s8_t1_S1_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:0 -o save:std.out -e empty \
	    ping -c 1 -s 8 -t 1 -S ::1 localhost
	check_ping_statistics std.out $(atf_get_srcdir)/ping_c1_s8_t1_S1.out
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

ping_c1t6_head()
{
	atf_set "descr" "-t6 is not interpreted as -t -6 by ping"
}
ping_c1t6_body()
{
	require_ipv4
	atf_check -s exit:0 -o ignore -e empty ping -c1 -t6 127.0.0.1
}

ping6_c1t4_head()
{
	atf_set "descr" "-t4 is not interpreted as -t -4 by ping6"
}
ping6_c1t4_body()
{
	require_ipv6
	atf_check -s exit:0 -o ignore -e empty ping6 -c1 -t4 ::1
}

ping_46_head()
{
	atf_set "descr" "-4 and -6 cannot be used simultaneously"
}
ping_46_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:1 \
	    -e match:"-4 and -6 cannot be used simultaneously" \
	    ping -4 -6 localhost
}

ping6_46_head()
{
	atf_set "descr" "-4 and -6 cannot be used simultaneously"
}
ping6_46_body()
{
	require_ipv4
	require_ipv6
	atf_check -s exit:1 \
	    -e match:"-4 and -6 cannot be used simultaneously" \
	    ping6 -4 -6 localhost
}

atf_init_test_cases()
{
	atf_add_test_case ping_c1_s56_t1
	atf_add_test_case ping_c1_s56_t1_S127
	atf_add_test_case ping_6_c1_s8_t1
	atf_add_test_case ping_c1_s8_t1_S1
	atf_add_test_case ping6_c1_s8_t1
	atf_add_test_case ping_c1t6
	atf_add_test_case ping6_c1t4
	atf_add_test_case ping_46
	atf_add_test_case ping6_46
}

check_ping_statistics()
{
	sed -e 's/localhost ([0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\})/localhost/' \
	    -e 's/from [0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}/from/' \
	    -e 's/hlim=[0-9]*/hlim=/' \
	    -e 's/ttl=[0-9]*/ttl=/' \
	    -e 's/time=[0-9.-]*/time=/g' \
	    -e '/round-trip/s/[0-9.]//g' \
	    "$1" >"$1".filtered
	atf_check -s exit:0 diff -u "$1".filtered "$2"
}
