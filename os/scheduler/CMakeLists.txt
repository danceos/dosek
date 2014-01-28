set(SRCS
)

add_library(scheduler ${SRCS})
set_target_properties(scheduler PROPERTIES LINKER_LANGUAGE CXX)

add_subdirectory(test)
