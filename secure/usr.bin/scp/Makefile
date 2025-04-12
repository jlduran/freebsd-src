.include <src.opts.mk>
.include "${SRCTOP}/secure/ssh.mk"

PROG=	scp
SFTP_CLIENT_SRCS=sftp-common.c sftp-client.c sftp-glob.c
SRCS=	scp.c progressmeter.c $(SFTP_CLIENT_SRCS)
PACKAGE=	ssh

LIBADD=	ssh

.include <bsd.prog.mk>

.PATH:	${SSHDIR}
