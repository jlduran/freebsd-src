/*-
 * SPDX-License-Identifier: BSD-2-Clause-FreeBSD
 *
 * Copyright (c) 2023 Fidaullah Noonari-emumba
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#include <sys/cdefs.h>

#include <sys/errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <atf-c.h>

#define MULTICAST_IP "233.252.0.1"
#define SOURCE_IP "192.0.2.1"
#define LOCAL_PORT 4321
#define PORT 12345
#define TIMEOUT 5

static int sd;

static int
create_datagram_socket(struct group_source_req *grp, struct group_req *grp1)
{
	int reuse = 1;
	struct sockaddr_in local_sock;
	struct timeval tv;
	struct sockaddr_in *sockad_ptr;
	struct sockaddr_in *sockad_ptr1;

	/* Create a datagram socket on which to receive. */
	sd = socket(PF_INET, SOCK_DGRAM, 0);

	if (sd < 0)
		atf_tc_skip("Opening datagram socket error");

	/*
	 * Enable SO_REUSEADDR to allow multiple instances of this
	 * application to receive copies of the multicast datagrams.
	 */
	if (setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)))
		atf_tc_skip("Setting SO_REUSEADDR error");

	/*
	 * Bind to the proper port number with the IP address
	 * specified as INADDR_ANY.
	 */
	memset((char *)&local_sock, 0, sizeof(local_sock));

	local_sock.sin_len = sizeof(local_sock);
	local_sock.sin_family = AF_INET;
	local_sock.sin_port = htons(LOCAL_PORT);
	local_sock.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(sd, (struct sockaddr *)&local_sock, sizeof(local_sock)))
		atf_tc_skip("Binding datagram socket error");

	/* Set the timeout. */
	tv.tv_sec = TIMEOUT;
	tv.tv_usec = 0;

	if (setsockopt(sd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(struct timeval)))
		atf_tc_skip("Error setting timeout");

	/* Multicast block */
	memset((char *)&sockad_ptr, 0, sizeof(sockad_ptr));
	memset((char *)&sockad_ptr1, 0, sizeof(sockad_ptr1));

	grp->gsr_interface = 1;
	grp1->gr_interface = 1;

	sockad_ptr = (struct sockaddr_in *)&grp->gsr_group;
	sockad_ptr->sin_len = sizeof(struct sockaddr_in);
	sockad_ptr->sin_family = AF_INET;
	sockad_ptr->sin_port = htons(PORT);
	sockad_ptr->sin_addr.s_addr = inet_addr(MULTICAST_IP);

	sockad_ptr = (struct sockaddr_in *)&grp->gsr_source;
	sockad_ptr->sin_len = sizeof(struct sockaddr_in);
	sockad_ptr->sin_family = AF_INET;
	sockad_ptr->sin_port = htons(PORT);
	sockad_ptr->sin_addr.s_addr = inet_addr(SOURCE_IP);

	sockad_ptr1 = (struct sockaddr_in *)&grp1->gr_group;
	sockad_ptr1->sin_len = sizeof(struct sockaddr_in);
	sockad_ptr1->sin_family = AF_INET;
	sockad_ptr1->sin_port = htons(PORT);
	sockad_ptr1->sin_addr.s_addr = inet_addr(MULTICAST_IP);

	return (sd);
}

ATF_TC_WITH_CLEANUP(join_group);
ATF_TC_HEAD(join_group, tc)
{
	atf_tc_set_md_var(tc, "descr", "Test MCAST_JOIN_GROUP option");
}
ATF_TC_BODY(join_group, tc)
{
	struct group_source_req grp;
	struct group_req grp1;
	int ret;
	char databuf[1024];

	sd = create_datagram_socket(&grp, &grp1);

	ret = setsockopt(sd, IPPROTO_IP, MCAST_JOIN_GROUP, &grp1, sizeof(grp1));
	ATF_REQUIRE_EQ_MSG(0, ret, "Adding multicast group error %d", errno);

	ATF_REQUIRE_MSG(read(sd, databuf, sizeof(databuf) - 1), "Reading datagram message `%s', error %d", databuf, errno);
}
ATF_TC_CLEANUP(join_group, tc)
{
	close(sd);
}

ATF_TC_WITH_CLEANUP(block_source);
ATF_TC_HEAD(block_source, tc)
{
	atf_tc_set_md_var(tc, "descr", "Test MCAST_BLOCK_SOURCE option");
}
ATF_TC_BODY(block_source, tc)
{
	struct group_source_req grp;
	struct group_req grp1;
	int ret;
	char databuf[1024];

	sd = create_datagram_socket(&grp, &grp1);

	setsockopt(sd, IPPROTO_IP, MCAST_JOIN_GROUP, &grp1, sizeof(grp1));
	ret = setsockopt(sd, IPPROTO_IP, MCAST_BLOCK_SOURCE, &grp, sizeof(grp));
	ATF_REQUIRE_EQ_MSG(0, ret, "Adding multicast group error %d", errno);

	ATF_REQUIRE_MSG(read(sd, databuf, sizeof(databuf) - 1), "Reading datagram message `%s', error %d", databuf, errno);
}
ATF_TC_CLEANUP(block_source, tc)
{
	close(sd);
}

ATF_TC_WITH_CLEANUP(unblock_source);
ATF_TC_HEAD(unblock_source, tc)
{
	atf_tc_set_md_var(tc, "descr", "Test MCAST_UNBLOCK_SOURCE option");
}
ATF_TC_BODY(unblock_source, tc)
{
	struct group_source_req grp;
	struct group_req grp1;
	int ret;
	char databuf[1024];

	sd = create_datagram_socket(&grp, &grp1);

	setsockopt(sd, IPPROTO_IP, MCAST_JOIN_GROUP, &grp1, sizeof(grp1));
	setsockopt(sd, IPPROTO_IP, MCAST_BLOCK_SOURCE, &grp, sizeof(grp));
	ret = setsockopt(sd, 0, MCAST_UNBLOCK_SOURCE, &grp, sizeof(grp));
	ATF_REQUIRE_EQ_MSG(0, ret, "Adding multicast group error %d", errno);

	ATF_REQUIRE_MSG(read(sd, databuf, sizeof(databuf) - 1), "Reading datagram message `%s', error %d", databuf, errno);
}
ATF_TC_CLEANUP(unblock_source, tc)
{
	close(sd);
}

ATF_TC_WITH_CLEANUP(leave_group);
ATF_TC_HEAD(leave_group, tc)
{
	atf_tc_set_md_var(tc, "descr", "Test MCAST_LEAVE_GROUP option");
}
ATF_TC_BODY(leave_group, tc)
{
	struct group_source_req grp;
	struct group_req grp1;
	int ret;

	sd = create_datagram_socket(&grp, &grp1);

	setsockopt(sd, IPPROTO_IP, MCAST_JOIN_GROUP, &grp1, sizeof(grp1));
	ret = setsockopt(sd, 0, MCAST_LEAVE_GROUP, &grp1, sizeof(grp1));
	ATF_REQUIRE_EQ_MSG(0, ret, "Adding multicast group error %d", errno);
}
ATF_TC_CLEANUP(leave_group, tc)
{
	close(sd);
}

ATF_TP_ADD_TCS(tp)
{

	ATF_TP_ADD_TC(tp, join_group);
	ATF_TP_ADD_TC(tp, block_source);
	ATF_TP_ADD_TC(tp, unblock_source);
	ATF_TP_ADD_TC(tp, leave_group);

	return atf_no_error();
}
