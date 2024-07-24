#!/usr/libexec/flua

local n = require("nuage")

print(n.serialize('/bin/cat ; echo "ALL YOUR CLOUD ARE BELONG TO US."'))
