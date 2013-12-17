
set(SRCS
	tasklist.cc
	scheduler.cc
)

add_library(scheduler ${SRCS})

add_subdirectory(test)
