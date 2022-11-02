# $FreeBSD$

ATF_TESTS_C+=	in_cksum_test
SRCS.in_cksum_test= in_cksum_test.c ../utils.c

PACKAGE= tests

ATF_TESTS_SH+=	ping_test

${PACKAGE}FILES+= common.subr
${PACKAGE}FILES+= icmp_control_messages.subr
${PACKAGE}FILES+= ping_6_c1_s8_t1.out
${PACKAGE}FILES+= ping_A_c2_t2.out
${PACKAGE}FILES+= ping_a_c1_t1.out
${PACKAGE}FILES+= ping_c1_s56_t1.out
${PACKAGE}FILES+= ping_c1_s56_t1_S127.out
${PACKAGE}FILES+= ping_c1_s8_t1_S1.out
${PACKAGE}FILES+= pinger.py
${PACKAGE}FILES+= pinger_reply_dup.out
${PACKAGE}FILES+= pinger_reply_opts.out
${PACKAGE}FILES+= pinger_unreach_opts.out

${PACKAGE}FILESMODE_pinger.py=	0555

.include <bsd.test.mk>
