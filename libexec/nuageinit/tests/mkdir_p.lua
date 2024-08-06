#!/usr/libexec/flua

local n = require("nuage")

local root = os.getenv("NUAGE_FAKE_ROOTDIR")
local tests = {
	{path = false, addroot = false},
	{path = "path1", addroot = true},
	{path = "/my/existing_path", addroot = true},
	{path = "/my/quoted path/path1", addroot = true},
	{path = "/my/path/path1", addroot = true}
}

for _, test in pairs(tests) do
	local path
	if test.addroot then
		path = root .. test.path
	else
		path = test.path
	end
	local ret, err = n.mkdir_p(path)
	if ret then
		print("nuageinit: mkdir_p: " .. test.path)
	else
		n.warn("mkdir_p: " .. err)
	end
end
