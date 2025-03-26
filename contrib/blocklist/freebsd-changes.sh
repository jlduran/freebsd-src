#!/bin/sh

#
# FreeBSD-specific changes from upstream
#

# Remove Debian port
rm -fr port/debian

# /libexec -> /usr/libexec
sed -i "" -e 's|/libexec|/usr/libexec|g' bin/blocklistd.8

# NetBSD: RT_ROUNDUP -> FreeBSD: SA_SIZE (from net/route.h)
sed -i "" -e 's/RT_ROUNDUP/SA_SIZE/g' bin/conf.c

# npfctl(8) -> ipf(8), ipfw(8), pfctl(8)
sed -i "" -e 's/npfctl 8 ,/ipf 8 ,\nipfw 8 ,\npfctl 8 ,/g' bin/blocklistd.8

# TODO: etc/rc.d/blocklistd: should we change it to:
# REQUIRE: ipfw pf ipfilter
