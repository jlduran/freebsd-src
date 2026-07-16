/*-
 * Copyright (c) 2015 The NetBSD Foundation, Inc.
 * Copyright (c) 2016 The FreeBSD Foundation
 * All rights reserved.
 *
 * Portions of this software were developed by Kurt Lidl
 * under sponsorship from the FreeBSD Foundation.
 *
 * This code is derived from software contributed to The NetBSD Foundation
 * by Christos Zoulas.
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
 * THIS SOFTWARE IS PROVIDED BY THE NETBSD FOUNDATION, INC. AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 * TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include "includes.h"

#include <ctype.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <syslog.h>
#include <unistd.h>

#include "ssh.h"
#include "packet.h"
#include "log.h"
#include "misc.h"
#include "servconf.h"
#include <blocklist.h>
#include "blocklist_client.h"

static struct blocklist *blstate = NULL;

/* import */
extern ServerOptions options;

/* internal definition from bl.h */
struct blocklist *bl_create(bool, char *, void (*)(int, const char *, va_list));

/* impedence match vsyslog() to sshd's internal logging levels */
void
im_log(int priority, const char *message, va_list args)
{
	LogLevel imlevel;

	switch (priority) {
	case LOG_ERR:
		imlevel = SYSLOG_LEVEL_ERROR;
		break;
	case LOG_DEBUG:
		imlevel = SYSLOG_LEVEL_DEBUG1;
		break;
	case LOG_INFO:
		imlevel = SYSLOG_LEVEL_INFO;
		break;
	default:
		imlevel = SYSLOG_LEVEL_DEBUG2;
	}
	do_log2(imlevel, message, args);
}

void
blocklist_init(void)
{

	if (options.use_blocklist)
		blstate = bl_create(false, NULL, im_log);
}

void
blocklist_notify(struct ssh *ssh, int action, const char *msg)
{

	if (blstate != NULL && ssh_packet_connection_is_on_socket(ssh))
		(void)blocklist_r(blstate, action,
		ssh_packet_get_connection_in(ssh), msg);
}

void
blocklist_notify_safe(struct ssh *ssh, int action, const char *msg)
{
	int s;
	int fd;
	struct sockaddr_un addr;
	struct {
		int db_action;
		int db_fd;
		char db_msg[128];
	} bl_msg;

	if (ssh == NULL)
		return;

	/* Extract the file descriptor safely */
	fd = ssh_packet_get_connection_in(ssh);
	if (fd < 0)
		return;

	/* Open the local domain socket */
	s = socket(PF_LOCAL, SOCK_DGRAM | SOCK_CLOEXEC, 0);
	if (s == -1)
		return;

	/* Configure target socket path */
	memset(&addr, 0, sizeof(addr));
	addr.sun_family = AF_LOCAL;
	strlcpy(addr.sun_path, _PATH_BLSOCK, sizeof(addr.sun_path));

	/* Connect and send binary payload */
	if (connect(s, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
		memset(&bl_msg, 0, sizeof(bl_msg));
		bl_msg.db_action = action;
		bl_msg.db_fd = fd;
		strlcpy(bl_msg.db_msg, msg, sizeof(bl_msg.db_msg));

		(void)write(s, &bl_msg, sizeof(bl_msg));
	}

	(void)close(s);
}
