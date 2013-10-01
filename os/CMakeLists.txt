
set(SRCS
		main.cc
)

add_library(os ${SRCS})

add_subdirectory(scheduler)
target_link_libraries(os scheduler)

add_subdirectory(test)
