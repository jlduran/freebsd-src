#
ACLOCAL_AMFLAGS = -I m4
lib_LTLIBRARIES = libblacklist.la
include_HEADERS = ../include/blacklist.h

exampledir = $(datarootdir)/examples/blacklistd
example_DATA = ../etc/blacklistd.conf ../etc/npf.conf

sbin_PROGRAMS = blacklistd blacklistctl
noinst_PROGRAMS = srvtest cltest
libexec_SCRIPTS = ../libexec/blacklistd-helper

man5_MANS = ../bin/blacklistd.conf.5
man8_MANS = ../bin/blacklistd.8 ../bin/blacklistctl.8

VPATH = ../bin:../lib:../test:../include

AM_CPPFLAGS = -I../include  -DDOT="."
AM_CPPFLAGS += -D_PATH_BLCONF=\"$(sysconfdir)/blacklistd.conf\"
AM_CPPFLAGS += -D_PATH_BLCONTROL=\"$(libexecdir)/blacklistd-helper\"
AM_CPPFLAGS += -D_PATH_BLSOCK=\"$(runstatedir)/blacklistd.sock\"
AM_CPPFLAGS += -D_PATH_BLSTATE=\"$(localstatedir)/db/blacklistd.db\"
AM_CPPFLAGS += -std=c99 -D_POSIX_C_SOURCE=200809L -D__EXTENSIONS__
AM_CPPFLAGS += -D__BSD_VISIBLE=1
AM_CFLAGS = @WARNINGS@

libblacklist_la_SOURCES = bl.c blacklist.c
libblacklist_la_LDFLAGS = -no-undefined -version-info 0:0:0
libblacklist_la_LIBADD = $(LTLIBOBJS)

SRCS = internal.c support.c run.c conf.c state.c
blacklistd_SOURCES = blacklistd.c ${SRCS}
blacklistd_LDADD = libblacklist.la
blacklistctl_SOURCES = blacklistctl.c ${SRCS}
blacklistctl_LDADD = libblacklist.la
srvtest_SOURCES = srvtest.c ${SRCS}
srvtest_LDADD = libblacklist.la
cltest_SOURCES = cltest.c ${SRCS}
cltest_LDADD = libblacklist.la
