#!/usr/libexec/flua

local n = require("nuage")

local tests = {
	false,
	"path",
	"/my/path/path1"
}

for _, test in pairs(tests) do
	local name, err = n.dirname(test)
	if name then
		print("nuageinit: dirname: " .. name)
	else
		n.warn("dirname: " .. err)
	end
end
