set(SRCS
    counter.cc
    helper.cc
)

add_library(os ${SRCS})

add_subdirectory(scheduler)
