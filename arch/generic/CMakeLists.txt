message(STATUS "Preparing generic startup code.")

set(SRCS
		startup.cc
		constructors.cc
		constructors.h
		ostream.cc
)

# Add to include directories
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Link startup code into library
add_library(generic ${SRCS})
