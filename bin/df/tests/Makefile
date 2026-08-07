PACKAGE=	tests

ATF_TESTS_SH=	df_test

PROGS+=		h_df
BINDIR.h_df=	${TESTSDIR}

.PATH:		${SRCTOP}/bin/df
SRCS=		df.c getmntinfo.c

LIBADD=	xo util

.include <bsd.test.mk>
