#!/bin/sh
set -e

start_time=$(date +%s)
mkdir -p /usr/local/etc/pkg/repos
echo 'FreeBSD: {url: "pkg+https://pkg.FreeBSD.org/${ABI}/latest"}' > /usr/local/etc/pkg/repos/FreeBSD.conf
pkg upgrade -y
pkg install -y "$@" && exit 0

cat <<EOF
pkg install failed after $(($(date +%s) - $start_time))s

dmesg tail:
$(dmesg | tail)

trying again
EOF

start_time=$(date +%s)
pkg install -y "$@" && exit 0

cat <<EOF
second pkg install failed after $(($(date +%s) - $start_time))s
EOF
exit 1
