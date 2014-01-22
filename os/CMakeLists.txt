set(SRCS
	counter.cc
    helper.cc
)

# TODO: add message to ignore non-suppressable warning
add_library(os ${SRCS})

add_subdirectory(scheduler)
#Currently we have no scheduler library!
#target_link_libraries(os scheduler)

add_subdirectory(test)
