.include <src.opts.mk>
.include "${SRCTOP}/secure/ssh.mk"

PROG=	sftp
SFTP_CLIENT_SRCS=sftp-common.c sftp-client.c sftp-glob.c
SRCS=	sftp.c sftp-usergroup.c progressmeter.c $(SFTP_CLIENT_SRCS)
PACKAGE=	ssh

LIBADD=	ssh edit

.include <bsd.prog.mk>

.PATH:	${SSHDIR}
