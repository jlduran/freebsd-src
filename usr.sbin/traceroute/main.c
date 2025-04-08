/*
 * Copyright (c) [year] [your name]
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

#include <sys/types.h>
#include <sys/socket.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <unistd.h>
#include <err.h>
#include <sysexits.h>

#include <netinet/in.h>
#include <arpa/inet.h>

#include "main.h"
#ifdef INET
#include "traceroute.h"
#endif
#ifdef INET6
#include "traceroute6.h"
#endif

#if defined(INET) && defined(INET6)
#define	OPTSTR TRACEROUTE6OPTS TRACEROUTEOPTS
#elif defined(INET)
#define	OPTSTR TRACEROUTEOPTS
#elif defined(INET6)
#define	OPTSTR TRACEROUTE6OPTS
#else
#error At least one of INET or INET6 is required
#endif

#define Fprintf (void)fprintf

int
main(int argc, char **argv)
{
#if defined(INET)
	struct in_addr a;
#endif
#if defined(INET6)
	struct in6_addr a6;
#endif
#if defined(INET) && defined(INET6)
	struct addrinfo hints, *res, *ai;
	const char *target;
	int error;
#endif
	int opt;

#ifdef INET6
	if (strcmp(getprogname(), "traceroute6") == 0)
		return traceroute6(argc, argv);
#endif

	while ((opt = getopt(argc, argv, ":" OPTSTR)) != -1) {
		switch (opt) {
#ifdef INET
		case '4':
			goto traceroute;
			break;
#endif
#ifdef INET6
		case '6':
			goto traceroute6;
			break;
#endif
		case 's':
			/*
			 * If -s is given with a numeric parameter,
			 * force use of the corresponding version.
			 */
#ifdef INET
			if (inet_pton(AF_INET, optarg, &a) == 1)
				goto traceroute;
#endif
#ifdef INET6
			if (inet_pton(AF_INET6, optarg, &a6) == 1)
				goto traceroute6;
#endif
			break;
		default:
			break;
		}
	}

#if defined(INET) && defined(INET6)
	target = argv[argc - 1];
	memset(&hints, 0, sizeof(hints));
	hints.ai_socktype = SOCK_RAW;
	if (feature_present("inet") && !feature_present("inet6"))
		hints.ai_family = AF_INET;
	else if (feature_present("inet6") && !feature_present("inet"))
		hints.ai_family = AF_INET6;
	else
		hints.ai_family = AF_UNSPEC;
	error = getaddrinfo(target, NULL, &hints, &res);
	if (res == NULL)
		errx(EX_NOHOST, "cannot resolve %s: %s",
				target, gai_strerror(error));
	for (ai = res; ai != NULL; ai = ai->ai_next) {
		if (ai->ai_family == AF_INET) {
			freeaddrinfo(res);
			goto traceroute;
		}
		if (ai->ai_family == AF_INET6) {
			freeaddrinfo(res);
			goto traceroute6;
		}
	}
	freeaddrinfo(res);
	errx(EX_NOHOST, "cannot resolve %s", target);
#endif


#ifdef INET
traceroute:
	optreset = 1;
	optind = 1;
	return traceroute(argc, argv);
#endif

#ifdef INET6
traceroute6:
	optreset = 1;
	optind = 1;
	return traceroute6(argc, argv);
#endif

	errx(1, "%s: no suitable addresses", argv[0]);
}

void
usage(void)
{
	Fprintf(stderr, "Usage:\n"
#ifdef INET
	    "\ttraceroute [-4adDeEFInrSvx] [-A as_server] [-f first_ttl] [-g gateway]\n"
	    "\t    [-i iface] [-m max_ttl] [-M first_ttl] [-p port] [-P proto]\n"
	    "\t    [-q nprobes] [-s src_addr] [-t tos] [-w waittime]\n"
	    "\t    [-z pausemsecs] host [packetlen]\n"
#endif /* INET */
#ifdef INET6
	    "\ttraceroute [-6adEIlnNrSTUv] [-A as_server] [-f firsthop] [-g gateway]\n"
	    "\t    [-m hoplimit] [-p port] [-q probes] [-s src] [-t tclass]\n"
	    "\t    [-w waittime] target [datalen]\n"
	    "\ttraceroute6 [adEIlnNrSTUv] [-A as_server] [-f firsthop] [-g gateway]\n"
	    "\t    [-m hoplimit] [-p port] [-q probes] [-s src] [-t tclass]\n"
	    "\t    [-w waittime] target [datalen]\n"
#endif /* INET6 */
	    );

	exit(1);
}
