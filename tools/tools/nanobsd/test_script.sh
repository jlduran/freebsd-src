#!/bin/sh

TEST_USER=jlduran

# Save the mtree of the resulting image
save_w_mtree() {
	worlddir="$1"
	file="$2"
	unprivileged="$3"

	if [ -z "$unprivileged" ]; then
		cp /usr/obj/home/${TEST_USER}/nanobsd.full/_.metalog /tmp/METALOG.pre
	else
		mtree -c -p "$worlddir" | mtree -C -K uname,gname -R nlink,size,time > /tmp/METALOG.pre
		sed -i "" -e "s/ flags=schg,uarch/ flags=schg/g" -e "s/ flags=uarch$//g" /tmp/METALOG.pre
	fi
	sort /tmp/METALOG.pre > "/tmp/${file}.mtree"
	rm -f /tmp/METALOG.pre
}

# Common base configuration
setup_config() {
	unprivileged="$1"

	cat << EOF > /tmp/nano_test.conf
NANO_MEDIASIZE=8000000
NANO_RAM_TMPVARSIZE=81920
NANO_DRIVE=vtbd0

NANO_PACKAGE_DIR=/usr/local/poudriere/data/packages/nanobsd-latest/All
NANO_CUSTOMIZE="cust_comconsole cust_allow_ssh_root cust_install_files cust_pkgng"

NANO_CFGDIR=/home/${TEST_USER}/Developer/nanobsd/cfg
NANO_METALOG_CFG=/home/${TEST_USER}/Developer/nanobsd/cfg.mtree
EOF

	if [ -n "$unprivileged" ]; then
		echo 'NANO_SRC="/home/jlduran/Developer/freebsd-src"' >> /tmp/nano_test.conf
		echo 'NANO_OBJ="/usr/obj/home/jlduran/nanobsd.${NANO_NAME}${NANO_LAYOUT:+.${NANO_LAYOUT}}"' >> /tmp/nano_test.conf
	fi
	chmod 0777 /tmp/nano_test.conf
}

# Header Print
hprint() {
	echo
	printf "%80s\n" "" | tr " " "#"
	printf "# %-76s #\n" "$*"
	printf "%80s\n" "" | tr " " "#"
}

cd /usr/src/tools/tools/nanobsd || exit

# NOTE: Assume all caches are hot!

if [ "$(id -u)" -ne 0 ]; then
	echo "Must be root." >&2
	exit 1
fi

# Precompiled

## Privileged

### Distribution Sets

#### MBR (Legacy)

hprint "Precompiled - Privileged - Distribution Sets - MBR"
setup_config
cat << EOF >> /tmp/nano_test.conf
legacy
NANO_NOPKGBASE=yes
EOF
sh nanobsd.sh -nP -c /tmp/nano_test.conf
save_w_mtree /usr/obj/nanobsd.full/_.w precompiled_privileged_distset_mbr

#### GPT

hprint "Precompiled - Privileged - Distribution Sets - GPT"
setup_config
cat << EOF >> /tmp/nano_test.conf
gpt
NANO_NOPKGBASE=yes
EOF
sh nanobsd.sh -nP -c /tmp/nano_test.conf
save_w_mtree /usr/obj/nanobsd.full/_.w precompiled_privileged_distset_gpt

### Package Base

#### MBR (Legacy)

hprint "Precompiled - Privileged - Package Base - MBR"
setup_config
cat << EOF >> /tmp/nano_test.conf
legacy
EOF
sh nanobsd.sh -nP -c /tmp/nano_test.conf
save_w_mtree /usr/obj/nanobsd.full/_.w precompiled_privileged_pkgbase_mbr

#### GPT

hprint "Precompiled - Privileged - Package Base - GPT"
setup_config
cat << EOF >> /tmp/nano_test.conf
gpt
EOF
sh nanobsd.sh -nP -c /tmp/nano_test.conf
save_w_mtree /usr/obj/nanobsd.full/_.w precompiled_privileged_pkgbase_gpt

## Unprivileged

### Distribution Sets

#### MBR (Legacy)

hprint "Precompiled - Unprivileged - Distribution Sets - MBR"
setup_config "unprivileged"
cat << EOF >> /tmp/nano_test.conf
legacy
NANO_NOPKGBASE=yes
EOF
su "$TEST_USER" -c "cd /home/${TEST_USER}/Developer/freebsd-src/tools/tools/nanobsd && sh nanobsd.sh -nPU -c /tmp/nano_test.conf"
save_w_mtree /usr/obj/home/${TEST_USER}/nanobsd.full/_.w precompiled_unprivileged_distset_mbr

#### GPT

hprint "Precompiled - Unprivileged - Distribution Sets - GPT"
setup_config "unprivileged"
cat << EOF >> /tmp/nano_test.conf
gpt
NANO_NOPKGBASE=yes
EOF
su "$TEST_USER" -c "cd /home/${TEST_USER}/Developer/freebsd-src/tools/tools/nanobsd && sh nanobsd.sh -nPU -c /tmp/nano_test.conf"
save_w_mtree /usr/obj/home/${TEST_USER}/nanobsd.full/_.w precompiled_unprivileged_distset_gpt

### Package Base

#### MBR (Legacy)

hprint "Precompiled - Unprivileged - Package Base - MBR"
setup_config "unprivileged"
cat << EOF >> /tmp/nano_test.conf
legacy
EOF
su "$TEST_USER" -c "cd /home/${TEST_USER}/Developer/freebsd-src/tools/tools/nanobsd && sh nanobsd.sh -nPU -c /tmp/nano_test.conf"
save_w_mtree /usr/obj/home/${TEST_USER}/nanobsd.full/_.w precompiled_unprivileged_pkgbase_mbr

#### GPT

hprint "Precompiled - Unprivileged - Package Base - GPT"
setup_config "unprivileged"
cat << EOF >> /tmp/nano_test.conf
gpt
EOF
su "$TEST_USER" -c "cd /home/${TEST_USER}/Developer/freebsd-src/tools/tools/nanobsd && sh nanobsd.sh -nPU -c /tmp/nano_test.conf"
save_w_mtree /usr/obj/home/${TEST_USER}/nanobsd.full/_.w precompiled_unprivileged_pkgbase_gpt
