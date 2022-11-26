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
. $(atf_get_srcdir)/icmp_control_messages.subr
. $(atf_get_srcdir)/vnet.subr

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

ping_A_c2_t2_head()
{
	atf_set descr "Audible character when no packet is received"
}
ping_A_c2_t2_body()
{
	require_ipv4
	atf_check -s exit:2 \
	    -o save:std.out \
	    ping -A -c 2 -t 2 192.0.2.0
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_A_c2_t2.out
}

ping_a_c1_t1_head()
{
	atf_set descr "Audible character when a packet is received"
}
ping_a_c1_t1_body()
{
	require_ipv4
	atf_check -s exit:0 \
	    -o save:std.out \
	    ping -a -c 1 -t 1 localhost
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/ping_a_c1_t1.out
}

ping_Cx_head()
{
	atf_set descr "invalid PCP"
}
ping_Cx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid PCP" \
	    ping -Cx localhost
}

ping_cx_head()
{
	atf_set descr "invalid count of packets to transmit"
}
ping_cx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid count of packets to transmit" \
	    ping -cx localhost
}

ping_f_uid_head()
{
	atf_set descr "-f flag"
}
ping_f_uid_body()
{
	atf_check -s exit:66 \
	    -e match:"-f flag" \
	    ping -f localhost
}

# IPv4 only options
ping_Gx_head()
{
	atf_set descr "invalid packet size"
}
ping_Gx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid packet size" \
	    ping -Gx localhost
}

ping_G57_head()
{
	atf_set descr "packet size too large"
}
ping_G57_body()
{
	#sweepmax_1=$((DEFDATALEN + 1))
	sweepmax_1=57

	atf_check -s exit:66 \
	    -e match:"packet size too large" \
	    ping -G${sweepmax_1} localhost
}

ping_gx_head()
{
	atf_set descr "invalid packet size"
}
ping_gx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid packet size" \
	    ping -gx localhost
}

ping_g57_head()
{
	atf_set descr "packet size too large"
}
ping_g57_body()
{
	#sweepmin_1=$((DEFDATALEN + 1))
	sweepmin_1=57

	atf_check -s exit:66 \
	    -e match:"packet size too large" \
	    ping -g${sweepmin_1} localhost
}

ping_hx_head()
{
	atf_set descr "sweepincr invalid packet size"
}
ping_hx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid packet size" \
	    ping -hx localhost
}

ping_h57_head()
{
	atf_set descr "sweepincr packet size too large"
}
ping_h57_body()
{
	#sweepmin_1=$((DEFDATALEN + 1))
	sweepmin_1=57

	atf_check -s exit:66 \
	    -e match:"packet size too large" \
	    ping -h${sweepmin_1} localhost
}

ping_Iunknown_head()
{
	atf_set descr "invalid multicast interface"
}
ping_Iunknown_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid multicast interface" \
	    ping -Iunknown localhost
}

ping_lx_head()
{
	atf_set descr "invalid preload value"
}
ping_lx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid preload value" \
	    ping -hx localhost
}

ping_l100_head()
{
	atf_set descr "-l flag"
}
ping_l100_body()
{
	atf_check -s exit:66 \
	    -e match:"-l flag" \
	    ping -l100 localhost
}

ping_Mx_head()
{
	atf_set descr "invalid message"
}
ping_Mx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid message" \
	    ping -Mx localhost
}

ping_Mm_Mt_head()
{
	atf_set descr "ICMP_TSTAMP and ICMP_MASKREQ are exclusive"
}
ping_Mm_Mt_body()
{
	require_ipv4
	atf_check -s exit:64 \
	    -e match:"ICMP_TSTAMP and ICMP_MASKREQ are exclusive." \
	    ping -Mm -Mt localhost
}

ping_mx_head()
{
	atf_set descr "invalid TTL"
}
ping_mx_body()
{
	atf_check -s exit:64 \
	    -e match:"invalid TTL" \
	    ping -Mx localhost
}

ping_Px_head()
{
	atf_set descr "invalid security policy"
}
ping_Px_body()
{
	require_ipsec
	atf_check -s exit:64 \
	    -e match:"invalid security policy" \
	    ping -Px localhost
}

ping_px_head()
{
	atf_set descr "patterns must be specified as hex digits"
}
ping_px_body()
{
	atf_check -s exit:64 \
	    -e match:"patterns must be specified as hex digits" \
	    ping -px localhost
}

atf_test_case pinger_reply cleanup
pinger_reply_head()
{
	atf_set descr "Echo Reply packet using pinger.py"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 \
	    -o match:"1 packets transmitted, 1 packets received" \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0
}
pinger_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_reply_dup cleanup
pinger_reply_dup_head()
{
	atf_set descr "Echo Reply DUP! packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_reply_dup_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0 \
	    --count 2 \
	    --dup
	check_ping_statistics std.out $(atf_get_srcdir)/pinger_reply_dup.out
}
pinger_reply_dup_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_reply_opts cleanup
pinger_reply_opts_head()
{
	atf_set descr "Echo Reply packet with IP options"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_reply_opts_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0 \
	    --opts NOP
	check_ping_statistics std.out $(atf_get_srcdir)/pinger_reply_opts.out
}
pinger_reply_opts_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_reply_unk_opts cleanup
pinger_reply_unk_opts_head()
{
	atf_set descr "Echo Reply packet with unknown IP options"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_reply_unk_opts_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0 \
	    --opts unk
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/pinger_reply_unk_opts.out
}
pinger_reply_unk_opts_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_mask_reply cleanup
pinger_mask_reply_head()
{
	atf_set descr "Mask Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_mask_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 18 \
	    --icmp_code 0 \
	    --icmp_mask 255.255.0.0 \
	    --request mask
	check_ping_statistics std.out $(atf_get_srcdir)/pinger_mask_reply.out
}
pinger_mask_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_redirect_reply cleanup
pinger_redirect_reply_head()
{
	atf_set descr "Redirect Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_redirect_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 5 \
	    --icmp_code 0 \
	    --icmp_gwaddr 192.0.2.10
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_redirect_reply.out

	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 5 \
	    --icmp_code 0
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_redirect_reply_nogwaddr.out
}
pinger_redirect_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_paramprob_reply cleanup
pinger_paramprob_reply_head()
{
	atf_set descr "Parameter Problem Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_paramprob_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 12 \
	    --icmp_code 0 \
	    --icmp_pptr 20
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_paramprob_reply.out
}
pinger_paramprob_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_timestamp_reply cleanup
pinger_timestamp_reply_head()
{
	atf_set descr "Timestamp Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_timestamp_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 14 \
	    --icmp_code 0 \
	    --icmp_otime 1000 \
	    --icmp_rtime 2000 \
	    --icmp_ttime 3000 \
	    --request timestamp
	check_ping_statistics std.out \
	    $(atf_get_srcdir)/pinger_timestamp_reply.out
}
pinger_timestamp_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_warp_reply cleanup
pinger_warp_reply_head()
{
	atf_set descr "Time-warped Echo Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_warp_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out \
	    -e match:"time of day goes back" \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0 \
	    --special warp
	check_ping_statistics std.out $(atf_get_srcdir)/pinger_warp_reply.out
}
pinger_warp_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_wrong_reply cleanup
pinger_wrong_reply_head()
{
	atf_set descr "Malformed Echo Reply packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_wrong_reply_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:0 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 0 \
	    --icmp_code 0 \
	    --special wrong
	check_ping_statistics std.out $(atf_get_srcdir)/pinger_wrong_reply.out
}
pinger_wrong_reply_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_unreach_df cleanup
pinger_unreach_df_head()
{
	atf_set descr "Fragmentation Needed and DF Set"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_unreach_df_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 3 \
	    --icmp_code 4 \
	    --flags DF
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_unreach_df.out
}
pinger_unreach_df_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_unreach_nextmtu cleanup
pinger_unreach_nextmtu_head()
{
	atf_set descr "Fragmentation Needed and DF Set (MTU 1000)"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_unreach_nextmtu_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 3 \
	    --icmp_code 4 \
	    --flags DF \
	    --icmp_nextmtu 1000
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_unreach_nextmtu.out
}
pinger_unreach_nextmtu_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_unreach_opts cleanup
pinger_unreach_opts_head()
{
	atf_set descr \
	    "Host Unreachable packet with IP options"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_unreach_opts_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 3 \
	    --icmp_code 1 \
	    --opts NOP
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_unreach_opts.out
}
pinger_unreach_opts_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_unreach_tcp cleanup
pinger_unreach_tcp_head()
{
	atf_set descr \
	    "Host Unreachable with a TCP packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_unreach_tcp_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 3 \
	    --icmp_code 1 \
	    --special tcp
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_unreach_tcp.out
}
pinger_unreach_tcp_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_unreach_udp cleanup
pinger_unreach_udp_head()
{
	atf_set descr \
	    "Host Unreachable with a UDP packet"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_unreach_udp_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	atf_check -s exit:2 -o save:std.out -e empty \
	    jexec BRL $(atf_get_srcdir)/pinger.py \
	    --iface $tun \
	    --src 192.0.2.1 \
	    --dst 192.0.2.2 \
	    --icmp_type 3 \
	    --icmp_code 1 \
	    --special udp
	atf_check -s exit:0 \
	    diff -u std.out $(atf_get_srcdir)/pinger_unreach_udp.out
}
pinger_unreach_udp_cleanup()
{
	pinger_cleanup
}

atf_test_case pinger_pr_icmph cleanup
pinger_pr_icmph_head()
{
	atf_set descr "ICMP header descriptive strings"
	atf_set require.user root
	atf_set require.progs scapy
}
pinger_pr_icmph_body()
{
	require_ipv4
	pinger_init

	tun=$(vnet_mktun)
	vnet_mkjail BRL $tun
	icmp_control_messages | while read -r type code description; do
		atf_check -s exit:2 \
		    -o match:"$description" \
		    jexec BRL $(atf_get_srcdir)/pinger.py \
		    --iface $tun \
		    --src 192.0.2.1 \
		    --dst 192.0.2.2 \
		    --icmp_type "$type" \
		    --icmp_code "$code"
	done
}
pinger_pr_icmph_cleanup()
{
	pinger_cleanup
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
	atf_add_test_case ping_A_c2_t2
	atf_add_test_case ping_a_c1_t1
	atf_add_test_case ping_Cx
	atf_add_test_case ping_cx
	atf_add_test_case ping_f_uid
	atf_add_test_case ping_Gx
	atf_add_test_case ping_G57
	atf_add_test_case ping_gx
	atf_add_test_case ping_g57
	atf_add_test_case ping_hx
	atf_add_test_case ping_h57
	atf_add_test_case ping_Iunknown
	atf_add_test_case ping_lx
	atf_add_test_case ping_l100
	atf_add_test_case ping_Mx
	atf_add_test_case ping_Mm_Mt
	atf_add_test_case ping_mx
	atf_add_test_case ping_Px
	atf_add_test_case ping_px
	atf_add_test_case pinger_reply
	atf_add_test_case pinger_reply_dup
	atf_add_test_case pinger_reply_opts
	atf_add_test_case pinger_reply_unk_opts
	atf_add_test_case pinger_mask_reply
	atf_add_test_case pinger_paramprob_reply
	atf_add_test_case pinger_timestamp_reply
	atf_add_test_case pinger_redirect_reply
	atf_add_test_case pinger_warp_reply
	atf_add_test_case pinger_wrong_reply
	atf_add_test_case pinger_unreach_df
	atf_add_test_case pinger_unreach_nextmtu
	atf_add_test_case pinger_unreach_opts
	atf_add_test_case pinger_unreach_tcp
	atf_add_test_case pinger_unreach_udp
	atf_add_test_case pinger_pr_icmph
}

check_ping_statistics()
{
	sed -e 's/localhost ([0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\})/localhost/' \
	    -e 's/from [0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}/from/' \
	    -e 's/hlim=[0-9]*/hlim=/' \
	    -e 's/ttl=[0-9]*/ttl=/' \
	    -e 's/time=[0-9.-]*/time=/g' \
	    -e 's/cp:.*$/cp:  x  x  x  x  x  x  x  x /g' \
	    -e 's/dp:.*$/dp:  x  x  x  x  x  x  x  x /g' \
	    -e '/round-trip/s/[0-9.]//g' \
	    "$1" >"$1".filtered
	atf_check -s exit:0 diff -u "$1".filtered "$2"
}

pinger_init()
{
	vnet_init
}

pinger_cleanup()
{
	vnet_cleanup

	rm -f std.out
	rm -f std.out.filtered
}
