BLOCKLIST_DIR=${SRCTOP}/contrib/blocklist
.PATH: ${BLOCKLIST_DIR}/bin ${BLOCKLIST_DIR}/port

PACKAGE=	blocklist

CONFS=	blocklistd.conf # XXXJL use the new blocklistd.conf
PROG=	blacklistd
SRCS=	blocklistd.c conf.c run.c state.c support.c internal.c \
	sockaddr_snprintf.c pidfile.c strtoi.c popenve.c
MAN=	blocklistd.8 blocklistd.conf.5
MLINKS+=	blocklistd.8 blacklistd.8
MLINKS+=	blocklistd.conf.5 blacklistd.conf.5

LDFLAGS+=-L${LIBBLACKLISTDIR}
LIBADD+= blacklist util

CFLAGS+=-I${BLOCKLIST_DIR}/include -I${BLOCKLIST_DIR}/port \
	-D_PATH_BLCONTROL=\"/usr/libexec/blocklistd-helper\" \
	-DHAVE_CONFIG_H -DHAVE_DB_H -DHAVE_LIBUTIL_H \
	-DHAVE_CLOCK_GETTIME -DHAVE_FGETLN -DHAVE_FPARSELN \
	-DHAVE_GETPROGNAME -DHAVE_STRLCAT -DHAVE_STRLCPY \
	-DHAVE_STRUCT_SOCKADDR_SA_LEN
# CFLAGS+= -D_REENTRANT

.include <bsd.prog.mk>
