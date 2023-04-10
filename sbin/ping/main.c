/*-
 * SPDX-License-Identifier: BSD-2-Clause-FreeBSD
 *
 * Copyright (C) 2019 Jan Sucan <jansucan@FreeBSD.org>
 * All rights reserved.
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
__FBSDID("$FreeBSD$");

#include <sys/types.h>
#include <sys/socket.h>

#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>

#include <err.h>
#include <math.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "main.h"
#ifdef INET
#include "ping.h"
#endif
#ifdef INET6
#include "ping6.h"
#endif

#if defined(INET) && defined(INET6)
#define	OPTSTR PING6OPTS PING4OPTS
#elif defined(INET)
#define	OPTSTR PING4OPTS
#elif defined(INET6)
#define	OPTSTR PING6OPTS
#else
#error At least one of INET and INET6 is required
#endif

/* various options */
u_int options;

char *hostname;

/* counters */
long nreceived;		/* # of packets we got back */
long nrepeats;		/* number of duplicates */
long ntransmitted;	/* sequence # for outbound packets = #sent */
long nrcvtimeout = 0;	/* # of packets we got back after waittime */

/* nonzero if we've been told to finish up */
volatile sig_atomic_t seenint;
volatile sig_atomic_t seeninfo;

/* timing */
int timing;		/* flag to do timing */
double tmin = 999999999.0;	/* minimum round trip time */
double tmax = 0.0;	/* maximum round trip time */
double tsum = 0.0;	/* sum of all times, for doing average */
double tsumsq = 0.0;	/* sum of all times squared, for std. dev. */

int
main(int argc, char *argv[])
{
#if defined(INET) && defined(INET6)
	struct in_addr a;
	struct in6_addr a6;
#endif
#if defined(INET) || defined(INET6)
	struct addrinfo hints;
#endif
	int ch;
#ifdef INET
	bool ipv4 = false;
#endif
#ifdef INET6
	bool ipv6 = false;

	if (strcmp(getprogname(), "ping6") == 0)
		ipv6 = true;
#endif

	while ((ch = getopt(argc, argv, ":" OPTSTR)) != -1) {
		switch(ch) {
#ifdef INET
		case '4':
			ipv4 = true;
			break;
#endif
#ifdef INET6
		case '6':
			ipv6 = true;
			break;
#endif
#if defined(INET) && defined(INET6)
		case 'S':
			/*
			 * If -S is given with a numeric parameter,
			 * force use of the corresponding version.
			 */
			if (inet_pton(AF_INET, optarg, &a) == 1)
				ipv4 = true;
			else if (inet_pton(AF_INET6, optarg, &a) == 1)
				ipv6 = true;
			break;
#endif
		default:
			break;
		}
	}

	if (optind >= argc)
		usage();

	optreset = 1;
	optind = 1;
#if defined(INET) && defined(INET6)
	if (ipv4 && ipv6)
		errx(1, "-4 and -6 cannot be used simultaneously");
#endif

#if defined(INET) && defined(INET6)
	if (inet_pton(AF_INET, argv[argc - 1], &a) == 1) {
		if (ipv6)
			errx(1, "IPv6 requested but IPv4 target address "
			    "provided");
		hints.ai_family = AF_INET;
	}
	else if (inet_pton(AF_INET6, argv[argc - 1], &a6) == 1) {
		if (ipv4)
			errx(1, "IPv4 requested but IPv6 target address "
			    "provided");
		hints.ai_family = AF_INET6;
	} else if (ipv6)
		hints.ai_family = AF_INET6;
	else if (ipv4)
		hints.ai_family = AF_INET;
	else {
		if (!feature_present("inet6"))
			hints.ai_family = AF_INET;
		else if (!feature_present("inet"))
			hints.ai_family = AF_INET6;
		else {
			struct addrinfo *res;

			memset(&hints, 0, sizeof(hints));
			hints.ai_socktype = SOCK_RAW;
			hints.ai_family = AF_UNSPEC;
			getaddrinfo(argv[argc - 1], NULL, &hints, &res);
			if (res != NULL) {
				hints.ai_family = res[0].ai_family;
				freeaddrinfo(res);
			}
		}
	}
#elif defined(INET)
	hints.ai_family = AF_INET;
#elif defined(INET6)
	hints.ai_family = AF_INET6;
#endif

#ifdef INET
	if (hints.ai_family == AF_INET)
		return ping(argc, argv);
#endif /* INET */
#ifdef INET6
	if (hints.ai_family == AF_INET6)
		return ping6(argc, argv);
#endif /* INET6 */
	errx(1, "Unknown host");
}

/*
 * onsignal --
 *	Set the global bit that causes the main loop to quit.
 */
void
onsignal(int sig)
{
	switch (sig) {
	case SIGALRM:
	case SIGINT:
		/*
		 * When doing reverse DNS lookups, the seenint flag might not
		 * be noticed for a while.  Just exit if we get a second SIGINT.
		 */
		if (!(options & F_HOSTNAME) && seenint != 0)
			_exit(nreceived ? 0 : 2);
		seenint++;
		break;
	case SIGINFO:
		seeninfo++;
		break;
	}
}

/*
 * pr_summary --
 *	Print out summary statistics to the given output stream.
 */
void
pr_summary(FILE * restrict stream)
{
	fprintf(stream, "\n--- %s ping statistics ---\n", hostname);
	fprintf(stream, "%ld packets transmitted, ", ntransmitted);
	fprintf(stream, "%ld packets received, ", nreceived);
	if (nrepeats)
		fprintf(stream, "+%ld duplicates, ", nrepeats);
	if (ntransmitted) {
		if (nreceived > ntransmitted)
			fprintf(stream, "-- somebody's duplicating packets!");
		else
			fprintf(stream, "%.1f%% packet loss",
			    ((((double)ntransmitted - nreceived) * 100.0) /
			    ntransmitted));
	}
	if (nrcvtimeout)
		fprintf(stream, ", %ld packets out of wait time", nrcvtimeout);
	fputc('\n', stream);
	if (nreceived && timing) {
		/* Only display average to microseconds */
		double num = nreceived + nrepeats;
		double avg = tsum / num;
		double dev = sqrt(fmax(0, tsumsq / num - avg * avg));
		fprintf(stream,
		    "round-trip min/avg/max/stddev = %.3f/%.3f/%.3f/%.3f ms\n",
		    tmin, avg, tmax, dev);
	}
	fflush(stream);
}

void
usage(void)
{
	(void)fprintf(stderr,
	    "usage:\n"
#ifdef INET
	    "\tping [-4AaDdfHnoQqRrv] [-C pcp] [-c count] "
	    "[-G sweepmaxsize]\n"
	    "\t    [-g sweepminsize] [-h sweepincrsize] [-i wait] "
	    "[-l preload]\n"
	    "\t    [-M mask | time] [-m ttl] "
#ifdef IPSEC
	    "[-P policy] "
#endif
	    "[-p pattern] [-S src_addr] \n"
	    "\t    [-s packetsize] [-t timeout] [-W waittime] [-z tos] "
	    "IPv4-host\n"
	    "\tping [-4AaDdfHLnoQqRrv] [-C pcp] [-c count] [-I iface] "
	    "[-i wait]\n"
	    "\t    [-l preload] [-M mask | time] [-m ttl] "
#ifdef IPSEC
	    "[-P policy] "
#endif
	    "[-p pattern]\n"
	    "\t    [-S src_addr] [-s packetsize] [-T ttl] [-t timeout] [-W waittime]\n"
	    "\t    [-z tos] IPv4-mcast-group\n"
#endif /* INET */
#ifdef INET6
	    "\tping [-6AaDd"
#if defined(IPSEC) && !defined(IPSEC_POLICY_IPSEC)
	    "E"
#endif
	    "fHnNoOq"
#ifdef IPV6_USE_MIN_MTU
	    "u"
#endif
	    "vyY"
#if defined(IPSEC) && !defined(IPSEC_POLICY_IPSEC)
	    "Z"
#endif
	    "] "
	    "[-b bufsiz] [-c count] [-e gateway]\n"
	    "\t    [-I interface] [-i wait] [-k addrtype] [-l preload] "
	    "[-m hoplimit]\n"
	    "\t    [-p pattern]"
#if defined(IPSEC) && defined(IPSEC_POLICY_IPSEC)
	    " [-P policy]"
#endif
	    " [-S sourceaddr] [-s packetsize] [-t timeout]\n"
	    "\t    [-W waittime] [-z tclass] [IPv6-hops ...] IPv6-host\n"
#endif	/* INET6 */
	    );

	exit(1);
}
