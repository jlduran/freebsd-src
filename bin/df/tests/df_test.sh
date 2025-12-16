#
# Copyright (c) 2026 Jose Luis Duran <jlduran@FreeBSD.org>
#
# SPDX-License-Identifier: BSD-2-Clause
#

atf_test_case Pflag
Pflag_head()
{
	atf_set "descr" "Tests the output of df when using the -P flag"
}
Pflag_body()
{
	cat >expout <<EOF
Filesystem   512-blocks        Used   Available Capacity  Mounted on
filer:/      2405433344      270336  2405163008     1%    /filer
EOF
	atf_check -s exit:0 -o file:expout -e empty \
	    -x "$(atf_get_srcdir)/h_df -P | head -2"
}

atf_test_case kPflags
kPflags_head()
{
	atf_set "descr" "Tests the output of df when using the -k and -P flags"
}
kPflags_body()
{
	cat >expout <<EOF
Filesystem  1024-blocks        Used   Available Capacity  Mounted on
filer:/      1202716672      135168  1202581504     1%    /filer
EOF
	atf_check -s exit:0 -o file:expout -e empty \
	    -x "$(atf_get_srcdir)/h_df -k -P | head -2"
}

atf_init_test_cases()
{
	atf_add_test_case Pflag
	atf_add_test_case kPflags
}
