.include <src.opts.mk>

PACKAGE=	runtime
PROG=	traceroute
SRCS=	main.c
MAN=	traceroute.8
BINOWN=	root
BINMODE=4555

.if ${MK_INET_SUPPORT}!= "no"
CFLAGS+= -DINET
SRCS+=	as.c traceroute.c ifaddrlist.c findsaddr-udp.c
.endif

.if ${MK_INET6_SUPPORT}!= "no"
CFLAGS+= -DINET6
SRCS+=	traceroute6.c
LINKS=	${BINDIR}/traceroute ${BINDIR}/traceroute6
MLINKS=	traceroute.8 traceroute6.8
.endif

.if !defined(TRACEROUTE_NO_IPSEC)
CFLAGS+= -DIPSEC
LIBADD+=	ipsec
.endif

# RTT Jitter on the internet these days means printing 3 decimal places on
# > 1000ms times is plain useless.  Uncomment this to enable variable precision
# reporting, ie: print a variable precision from 0.001ms through 1000ms
# CFLAGS+= -DSANE_PRECISION

.if ${MK_CASPER} != "no"
LIBADD+=	casper
LIBADD+=	cap_dns
CFLAGS+=-DWITH_CASPER
.endif

WARNS?=	3

.include <bsd.prog.mk>
