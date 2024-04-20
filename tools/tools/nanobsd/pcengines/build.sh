#!/bin/sh

if [ -z "${1}" ] || ! [ -f "${1}" ]; then
	echo "Usage: $0 cfg_file [-bhiknw]"
	echo "-h : print this help summary page"
	echo "-i : skip image build"
	echo "-w : skip buildworld step"
	echo "-k : skip buildkernel step"
	echo "-b : skip buildworld and buildkernel step"
	echo "-n : add -DNO_CLEAN to buildworld, buildkernel, etc"
	exit
fi

CFG="${1}"
shift;

sh ../nanobsd.sh "$@" -c "${CFG}"
