PROG=	iovctl
SRCS=	iovctl.c parse.c validate.c
LIBADD=	nv ucl m

CFLAGS+=-I${SRCTOP}/contrib/libucl/include

MAN=	\
	iovctl.8 \
	iovctl.conf.5 \

.include <bsd.own.mk>
.include <bsd.prog.mk>

