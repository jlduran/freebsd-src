#!/usr/libexec/flua

local n = require("nuage")
local nkeys = 1

if #arg == 1 then
	nkeys = arg[1]
end

for nkey = 1, nkeys do
	n.addsshkey(".", "mykey" .. nkey)
end
