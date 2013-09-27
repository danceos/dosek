
OPTION(X86_TARGET_FAIL "FailBochs" ON)

if(X86_TARGET_FAIL)
	message(STATUS "Target i386 fail")
	set(ADDITIONAL_TARGETS "${CMAKE_CURRENT_SOURCE_DIR}/failbochs" CACHE INTERNAL STRING)
endif()


# setup x86-32 specific sources
set(SRCS
		startup.cc
		startup.s
		cga.cc
)

add_library(arch ${SRCS})
target_link_libraries(arch generic)

set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)
