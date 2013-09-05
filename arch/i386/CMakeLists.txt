
OPTION(X86_TARGET_FAIL "FailBochs" ON)

if(X86_TARGET_FAIL)
	message(STATUS "Target i386 fail")
	set(ADDITIONAL_TARGETS "${CMAKE_CURRENT_SOURCE_DIR}/failbochs" CACHE INTERNAL STRING)
endif()


# setup x86-32 specific sources
set(SRCS
		startup.cc
		startup.s
)


add_library(arch ${SRCS})
