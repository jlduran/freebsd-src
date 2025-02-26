#!/bin/sh

##########################################
# This file should eventually dissappear #
##########################################

#
# Rename blocklist to blacklist
#

# Change within files blocklist -> blacklist
files="$(find . -type f)"
for file in $files; do
	sed -i "" -e 's/blocklist/blacklist/g' "$file"
	sed -i "" -e 's/Blocklist/Blacklist/g' "$file"
	sed -i "" -e 's/BLOCKLIST/BLACKLIST/g' "$file"
done

# Rename blocklist -> blacklist
mv bin/blocklistctl.8 bin/blacklistctl.8
mv bin/blocklistctl.c bin/blacklistctl.c
mv bin/blocklistd.8 bin/blacklistd.8
mv bin/blocklistd.c bin/blacklistd.c
mv bin/blocklistd.conf.5 bin/blacklistd.conf.5
mv etc/blocklistd.conf etc/blacklistd.conf
mv etc/rc.d/blocklistd etc/rc.d/blacklistd
mv include/blocklist.h include/blacklist.h
mv lib/blocklist.c lib/blacklist.c
mv lib/libblocklist.3 lib/libblacklist.3
mv libexec/blocklistd-helper libexec/blacklistd-helper
