#-
# Copyright (c) 2022 Baptiste Daroussin <bapt@FreeBSD.org>
#
# SPDX-License-Identifier: BSD-2-Clause
#

atf_test_case warn
atf_test_case err
atf_test_case quote
atf_test_case dirname
atf_test_case mkdir_p

warn_body()
{
	atf_check -e "inline:nuageinit: plop\n" -s exit:0 /usr/libexec/flua $(atf_get_srcdir)/warn.lua
}

err_body()
{
	atf_check -e "inline:nuageinit: plop\n" -s exit:1 /usr/libexec/flua $(atf_get_srcdir)/err.lua
}

quote_body()
{
	export CATS="ALL YOUR CLOUD ARE BELONG TO US."
	atf_check -o "inline:/bin/cat; echo \"\$CATS\"\n" -s exit:0 /usr/libexec/flua $(atf_get_srcdir)/quote.lua
}

dirname_body()
{
	cat > stderr <<- EOF
	nuageinit: dirname: argument should be a path
	nuageinit: dirname: no path found
	EOF
	cat > stdout <<- EOF
	nuageinit: dirname: /my/path/
	EOF
	atf_check -e file:stderr -o file:stdout /usr/libexec/flua $(atf_get_srcdir)/dirname.lua
}

mkdir_p_body()
{
	export NUAGE_FAKE_ROOTDIR="$PWD"
	mkdir -p "${PWD}/my/existing_path"

	cat > stderr <<- EOF
	nuageinit: mkdir_p: argument should be a path
	EOF
	cat > stdout <<- EOF
	nuageinit: mkdir_p: path1
	nuageinit: mkdir_p: /my/existing_path
	nuageinit: mkdir_p: /my/quoted path/path1
	nuageinit: mkdir_p: /my/path/path1
	EOF
	atf_check -e file:stderr -o file:stdout /usr/libexec/flua $(atf_get_srcdir)/mkdir_p.lua
	test -d "${PWD}path1" || atf_fail "'path1' not created"
	test -d "${PWD}/my/quoted path/path1" || atf_fail "'/my/quoted path/path1' not created"
	test -d "${PWD}"/my/path/path1 || atf_fail "'/my/path/path1' not created"
}

atf_init_test_cases()
{
	atf_add_test_case warn
	atf_add_test_case err
	atf_add_test_case quote
	atf_add_test_case dirname
	atf_add_test_case mkdir_p
}
