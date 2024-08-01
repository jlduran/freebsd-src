---
-- SPDX-License-Identifier: BSD-2-Clause
--
-- Copyright(c) 2022 Baptiste Daroussin <bapt@FreeBSD.org>

local unistd = require("posix.unistd")
local sys_stat = require("posix.sys.stat")
local lfs = require("lfs")

local function warnmsg(str, prepend)
	if not str then
		return
	end
	local tag = ""
	if prepend ~= false then
		tag = "nuageinit: "
	end
	io.stderr:write(tag .. str .. "\n")
end

local function errmsg(str, prepend)
	warnmsg(str, prepend)
	os.exit(1)
end

-- Determine if a string is shell-safe
local function safe(str)
	return str:find("[^%w_@%%%+=:,%./%-]") == nil
end

-- Return a shell-escaped version of a string
local function quote(str)
	if not str then
		return "''"
	end
	if safe(str) then
		return str
	end

	-- Enclose with single quotes, and
	-- single quotes with double quotes
	return "'" .. ((str:gsub("'", "'\"'\"'"))) .. "'"
end

-- Return the directory portion of a path
local function dirname(path)
	if not path then
		return nil, "argument should be a path"
	end
	path = path:gsub("[^/]+/*$", "")
	if path == "" then
		return nil, "no path found"
	end
	return path
end

-- Create a directory (mkdir -p path)
local function mkdir_p(path)
	if not path or path == "" then
		return nil, "argument should be a path"
	end
	return os.execute("mkdir -p " .. quote(path))
end

-- XXX JL this is slow!
-- -q does not work as expected.
-- -R does not work, because it chroots and expects a sh inside.
-- Its only real value would be without -f, but then we won't
-- be able to mock the tests.
-- Run sysrc [-f file] name=[value]
local function sysrc_f(name, value, file)
	if not name or not safe(name) or name == "" then
		return
	end
	if not value then
		return
	end
	if not file or file == "" then
		file = ""
	else
		file = "-f " .. quote(file) .. " "
	end

	os.execute(
		"sysrc -q " .. file .. name .. "=" ..
		quote(value) .. " 1> /dev/null"
	)
end

local function sethostname(hostname)
	if hostname == nil then
		return
	end
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	if not root then
		root = ""
	end
	local hostnamepath = root .. "/etc/rc.conf.d/hostname"

	mkdir_p(dirname(hostnamepath))
	local f, err = io.open(hostnamepath, "w")
	if not f then
		warnmsg("Impossible to open " .. hostnamepath .. ":" .. err)
		return
	end
	f:write('hostname="' .. hostname .. '"\n')
	f:close()
end

local function splitlist(list)
	local ret = {}
	if type(list) == "string" then
		for str in list:gmatch("([^, ]+)") do
			ret[#ret + 1] = str
		end
	elseif type(list) == "table" then
		ret = list
	else
		warnmsg("Invalid type " .. type(list) .. ", expecting table or string")
	end
	return ret
end

local function adduser(pwd)
	if (type(pwd) ~= "table") then
		warnmsg("Argument should be a table")
		return nil
	end
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	local cmd = "pw "
	if root then
		cmd = cmd .. "-R " .. root .. " "
	end
	local f = io.popen(cmd .. " usershow " .. pwd.name .. " -7 2> /dev/null")
	local pwdstr = f:read("*a")
	f:close()
	if pwdstr:len() ~= 0 then
		return pwdstr:match("%a+:.+:%d+:%d+:.*:(.*):.*")
	end
	if not pwd.gecos then
		pwd.gecos = pwd.name .. " User"
	end
	if not pwd.homedir then
		pwd.homedir = "/home/" .. pwd.name
	end
	local extraargs = ""
	if pwd.groups then
		local list = splitlist(pwd.groups)
		extraargs = " -G " .. table.concat(list, ",")
	end
	-- pw will automatically create a group named after the username
	-- do not add a -g option in this case
	if pwd.primary_group and pwd.primary_group ~= pwd.name then
		extraargs = extraargs .. " -g " .. pwd.primary_group
	end
	if not pwd.no_create_home then
		extraargs = extraargs .. " -m "
	end
	if not pwd.shell then
		pwd.shell = "/bin/sh"
	end
	local precmd = ""
	local postcmd = ""
	if pwd.passwd then
		precmd = "echo '" .. pwd.passwd .. "' | "
		postcmd = " -H 0"
	elseif pwd.plain_text_passwd then
		precmd = "echo '" .. pwd.plain_text_passwd .. "' | "
		postcmd = " -h 0"
	end
	cmd = precmd .. "pw "
	if root then
		cmd = cmd .. "-R " .. root .. " "
	end
	cmd = cmd .. "useradd -n " .. pwd.name .. " -M 0755 -w none "
	cmd = cmd .. extraargs .. " -c '" .. pwd.gecos
	cmd = cmd .. "' -d '" .. pwd.homedir .. "' -s " .. pwd.shell .. postcmd

	local r = os.execute(cmd)
	if not r then
		warnmsg("fail to add user " .. pwd.name)
		warnmsg(cmd)
		return nil
	end
	if pwd.locked then
		cmd = "pw "
		if root then
			cmd = cmd .. "-R " .. root .. " "
		end
		cmd = cmd .. "lock " .. pwd.name
		os.execute(cmd)
	end
	return pwd.homedir
end

local function addgroup(grp)
	if (type(grp) ~= "table") then
		warnmsg("Argument should be a table")
		return false
	end
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	local cmd = "pw "
	if root then
		cmd = cmd .. "-R " .. root .. " "
	end
	local f = io.popen(cmd .. " groupshow " .. grp.name .. " 2> /dev/null")
	local grpstr = f:read("*a")
	f:close()
	if grpstr:len() ~= 0 then
		return true
	end
	local extraargs = ""
	if grp.members then
		local list = splitlist(grp.members)
		extraargs = " -M " .. table.concat(list, ",")
	end
	cmd = "pw "
	if root then
		cmd = cmd .. "-R " .. root .. " "
	end
	cmd = cmd .. "groupadd -n " .. grp.name .. extraargs
	local r = os.execute(cmd)
	if not r then
		warnmsg("fail to add group " .. grp.name)
		warnmsg(cmd)
		return false
	end
	return true
end

local function addsshkey(homedir, key)
	local chownak = false
	local chowndotssh = false
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	if root then
		homedir = root .. "/" .. homedir
	end
	local ak_path = homedir .. "/.ssh/authorized_keys"
	local dotssh_path = homedir .. "/.ssh"
	local dirattrs = lfs.attributes(ak_path)
	if dirattrs == nil then
		chownak = true
		dirattrs = lfs.attributes(dotssh_path)
		if dirattrs == nil then
			assert(lfs.mkdir(dotssh_path))
			chowndotssh = true
			dirattrs = lfs.attributes(homedir)
		end
	end

	local f = io.open(ak_path, "a")
	if not f then
		warnmsg("impossible to open " .. ak_path)
		return
	end
	f:write(key .. "\n")
	f:close()
	if chownak then
		sys_stat.chmod(ak_path, 384)
		unistd.chown(ak_path, dirattrs.uid, dirattrs.gid)
	end
	if chowndotssh then
		sys_stat.chmod(dotssh_path, 448)
		unistd.chown(dotssh_path, dirattrs.uid, dirattrs.gid)
	end
end

local n = {
	warn = warnmsg,
	err = errmsg,
	safe = safe,
	quote = quote,
	dirname = dirname,
	mkdir_p = mkdir_p,
	sysrc_f = sysrc_f,
	sethostname = sethostname,
	adduser = adduser,
	addgroup = addgroup,
	addsshkey = addsshkey
}

return n
