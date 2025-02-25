#!/bin/sh

NANO_MEDIASIZE=16000000
NANO_IMAGES=2
NANO_SECTS=63
NANO_HEADS=16
NANO_CODESIZE=0
NANO_CONFSIZE=2048
NANO_DATASIZE=0

	echo $NANO_MEDIASIZE $NANO_IMAGES \
		$NANO_SECTS $NANO_HEADS \
		$NANO_CODESIZE $NANO_CONFSIZE $NANO_DATASIZE |
	awk '
	{
		# size of cylinder in sectors
		cs = $3 * $4

		# number of full cylinders on media
		cyl = int ($1 / cs)

		if ($7 > 0) {
			# size of data partition in full cylinders
			dsl = int (($7 + cs - 1) / cs)
		} else {
			dsl = 0;
		}

		# size of config partition in full cylinders
		csl = int (($6 + cs - 1) / cs)

		# size of image partition(s) in full cylinders
		if ($5 == 0) {
			isl = int ((cyl - dsl - csl) / $2)
		} else {
			isl = int (($5 + cs - 1) / cs)
		}

		# First image partition start at second track
		print $3, isl * cs - $3, 1
		c = isl * cs;

		# Second image partition (if any) also starts offset one
		# track to keep them identical.
		if ($2 > 1) {
			print $3 + c, isl * cs - $3, 2
			c += isl * cs;
		}

		# Config partition starts at cylinder boundary.
		print c, csl * cs, 3
		c += csl * cs

		# Data partition (if any) starts at cylinder boundary.
		if ($7 > 0) {
			print c, dsl * cs, 4
		} else if ($7 < 0 && $1 > c) {
			print c, $1 - c, 4
		} else if ($1 < c) {
			print "Disk space overcommitted by", \
			    c - $1, "sectors" > "/dev/stderr"
			exit 2
		}
	}
	'

