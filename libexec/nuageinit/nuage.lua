-- SPDX-License-Identifier: BSD-2-Clause
--
-- Copyright(c) 2022 Baptiste Daroussin <bapt@FreeBSD.org>

local pu = require("posix.unistd")
local lfs = require("lfs")

local function warnmsg(str, prepend)
	local pre = ""
	if prepend ~= false then
		pre = "nuageinit: "
	end
	io.stderr:write(pre .. str .. "\n")
end

local function errmsg(str, prepend)
	local pre = ""
	if prepend ~= false then
		pre = "nuageinit: "
	end
	io.stderr:write(pre .. str .. "\n")
	os.exit(1)
end

--- Serialize a string
local function serialize(str)
	return ("%q"):format(str)
end

-- Remove outer double quotation marks from a string
local function unquote(str)
	return ((str:gsub('"(.*)"', "%1")))
end

--- Sanitize a string
local function sanitize(str)
	return unquote(serialize(str))
end

local function dirname(oldpath)
	if not oldpath then
		return nil
	end
	local path = oldpath:gsub("[^/]+/*$", "")
	if path == "" then
		return nil
	end
	return path
end

local function mkdir_p(path)
	if lfs.attributes(path, "mode") ~= nil then
		return true
	end
	local r, err = mkdir_p(dirname(path))
	if not r then
		return nil, err .. " (creating " .. path .. ")"
	end
	return lfs.mkdir(path)
end

-- Check if a file exists
local function file_exists(file)
	local f = io.open(file, "rb")
	if f then
		f:close()
	end
	return f ~= nil
end

-- Read all the lines from a file
-- Return an empty table if the file does not exist
local function lines_from(file)
	local lines = {}
	if file_exists(file) then
		for line in io.lines(file) do
			lines[#lines + 1] = line
		end
	end
	return lines
end

-- Check if an element is in a table
-- Return the index if found or nil if not present
local function find_in(a_table, element)
	local found = nil
	for i in pairs(a_table) do
		if a_table[i] == element then
			found = i
			break
		end
	end
	return found
end

local function sethostname(hostname)
	if hostname == nil then
		return
	end
	hostname = sanitize(hostname)
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	if not root then
		root = ""
	end
	local hostnamepath = sanitize(root .. "/etc/rc.conf.d/hostname")

	mkdir_p(dirname(hostnamepath))
	local f, err = io.open(hostnamepath, "w")
	if not f then
		warnmsg("impossible to write " .. hostnamepath .. ": " .. err)
		return
	end
	f:close()
	os.execute("sysrc -f " .. hostnamepath .. " hostname=" .. hostname .. " 1>/dev/null")
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
		warnmsg("invalid type ".. type(list) ..", expecting table or string")
	end
	return ret
end

local function adduser(pwd)
	if (type(pwd) ~= "table") then
		warnmsg("argument should be a table")
		return nil
	end
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	local gecos
	local homedir
	local shell = sanitize(pwd.shell)
	local name = sanitize(pwd.name)
	local cmd = "pw "
	local extraargs=""
	if root then
		cmd = sanitize(cmd .. "-R " .. root .. " ")
	end
	local f = io.popen(cmd .. " usershow " .. name .. " -7 2>/dev/null")
	local pwdstr = f:read("*a")
	f:close()
	if pwdstr:len() ~= 0 then
		return pwdstr:match("%a+:.+:%d+:%d+:.*:(.*):.*")
	end
	if not pwd.gecos then
		gecos = name .. " User"
	else
		gecos = sanitize(pwd.gecos)
	end
	if not pwd.homedir then
		homedir = "/home/" .. name
	else
		homedir = sanitize(pwd.homedir)
	end
	if pwd.groups then
		local list = splitlist(pwd.groups)
		extraargs = " -G " .. table.concat(list, ',')
	end
	-- pw will automatically create a group named after the username
	-- do not add a -g option in this case
	if pwd.primary_group and pwd.primary_group ~= name then
		extraargs = extraargs .. " -g " .. pwd.primary_group
	end
	if not pwd.no_create_home then
		extraargs = extraargs .. " -m "
	end
	if not pwd.shell then
		shell = "/bin/sh"
	end
	local precmd = ""
	local postcmd = ""
	if pwd.passwd then
		precmd = "echo " .. sanitize(pwd.passwd) .. " | "
		postcmd = " -H 0 "
	elseif pwd.plain_text_passwd then
		precmd = "echo " .. sanitize(pwd.plain_text_passwd) .. " | "
		postcmd = " -h 0 "
	end
	cmd = precmd .. "pw "
	if root then
		cmd = cmd .. "-R " .. root .. " "
	end
	cmd = cmd .. "useradd -n ".. name .. " -M 0755 -w none "
	cmd = cmd .. extraargs .. " -c '".. gecos
	cmd = cmd .. "' -d " .. homedir .. " -s ".. shell .. postcmd

	local r = os.execute(cmd)
	if not r then
		warnmsg("fail to add user " .. name);
		warnmsg(cmd)
		return nil
	end
	if pwd.locked then
		cmd = "pw "
		if root then
			cmd = cmd .. "-R " .. root .. " "
		end
		cmd = cmd .. "lock " .. name
		os.execute(cmd)
	end
	return homedir
end

local function addgroup(grp)
	if (type(grp) ~= "table") then
		warnmsg("argument should be a table")
		return false
	end
	local name = sanitize(grp.name)
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	local cmd = "pw "
	if root then
		cmd = sanitize(cmd .. "-R " .. root .. " ")
	end
	local f = io.popen(cmd .. " groupshow " .. name .. " 2>/dev/null")
	local grpstr = f:read("*a")
	f:close()
	if grpstr:len() ~= 0 then
		return true
	end
	local extraargs = ""
	if grp.members then
		local list = splitlist(grp.members)
		extraargs = " -M " .. table.concat(list, ',')
	end
	cmd = "pw "
	if root then
		cmd = sanitize(cmd .. "-R " .. root .. " ")
	end
	cmd = cmd .. "groupadd -n " .. name .. extraargs
	local r = os.execute(cmd)
	if not r then
		warnmsg("fail to add group " .. grp.name);
		warnmsg(cmd)
		return false
	end
	return true
end

local function addsshkey(homedir, key)
	homedir = sanitize(homedir)
	key = sanitize(key)
	local chownak = false
	local chowndotssh = false
	local authorized_keys
	local root = os.getenv("NUAGE_FAKE_ROOTDIR")
	if root then
		homedir = sanitize(root .. "/" .. homedir)
	end
	local ak_path = homedir .. "/.ssh/authorized_keys"
	local dotssh_path = homedir .. "/.ssh"
	local dirattrs = lfs.attributes(ak_path)
	if dirattrs == nil then
		chownak = true
		dirattrs = lfs.attributes(dotssh_path)
		if dirattrs == nil then
			if not lfs.mkdir(dotssh_path) then
				warnmsg("impossible to create " .. dotssh_path)
				return
			end
			chowndotssh = true
			dirattrs = lfs.attributes(homedir)
		end
	end
	authorized_keys = lines_from(ak_path)
	if find_in(authorized_keys, key) then
		return
	end
	local f = io.open(ak_path, "a")
	if not f then
		warnmsg("impossible to append " .. ak_path)
		return
	end
	f:write(key .. "\n")
	f:close()
	if chownak then
		os.execute("chmod 0600 " .. ak_path)
		pu.chown(ak_path, dirattrs.uid, dirattrs.gid)
	end
	if chowndotssh then
		os.execute("chmod 0700 " .. dotssh_path)
		pu.chown(dotssh_path, dirattrs.uid, dirattrs.gid)
	end
end

local n = {
	warn = warnmsg,
	err = errmsg,
	serialize = serialize,
	sanitize = sanitize,
	dirname = dirname,
	mkdir_p = mkdir_p,
	sethostname = sethostname,
	adduser = adduser,
	addgroup = addgroup,
	addsshkey = addsshkey,
}

return n
