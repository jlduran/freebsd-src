.include <src.opts.mk>

.if exists(${.CURDIR}/${MACHINE_ARCH:S/powerpc64le/powerpc64/})
SUBDIR+= ${MACHINE_ARCH:S/powerpc64le/powerpc64/}
.else
MACHINE_CPUARCH=       ${TARGET_ARCH} # XXX Linux clean (x86_64 -> amd64, aarch64 -> arm64)
SUBDIR+= ${MACHINE_CPUARCH}
.endif

HAS_TESTS=
SUBDIR.${MK_TESTS}+= tests

.include <bsd.subdir.mk>
