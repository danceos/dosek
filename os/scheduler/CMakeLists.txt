set(SRCS
	tasklist.cc
)

add_library(scheduler ${SRCS})

add_subdirectory(test)
