#!/usr/libexec/flua

local n = require("nuage")

local cmd = '/bin/cat; echo "$CATS"'
os.execute("echo " .. n.quote(cmd))
