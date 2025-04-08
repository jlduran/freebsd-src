/*
 * Copyright (c) [year] [your name]
 *
 * SPDX-License-Identifier: BSD-2-Clause
 */

#ifndef	MAIN_H
#define MAIN_H 1

#ifdef IPSEC
#include <netipsec/ipsec.h>
#endif /*IPSEC*/

#define TRACEROUTEOPTS "4aA:eEdDFInrSvxf:g:i:M:m:P:p:q:s:t:w:z:"
#define TRACEROUTE6OPTS "6aA:dEf:g:Ilm:nNp:q:rs:St:TUvw:"

void	usage(void) __dead2;

#endif /* !MAIN_H */
