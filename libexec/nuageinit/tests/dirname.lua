#!/usr/libexec/flua

local n = require("nuage")

print(n.dirname("/my/path/path1"))

if n.dirname("path") then
	n.err("expecting nil for n.dirname(\"path\")")
end

if n.dirname() then
	n.err("expecting nil for n.dirname()")
end
