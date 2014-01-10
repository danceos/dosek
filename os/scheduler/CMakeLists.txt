set(SRCS
	tasklist.cc
	thetasks.cc
	scheduler.cc
)

add_library(scheduler ${SRCS})

add_subdirectory(test)
