set(SRCS
    counter.cc
    helper.cc
    isr.cc
)

add_library(os ${SRCS})

add_subdirectory(scheduler)
