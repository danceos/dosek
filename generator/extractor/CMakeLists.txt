# Get the directory of llvm by using llvm-config. also remove whitespaces.
execute_process(COMMAND ${LLVM_CONFIG_EXE} --includedir
                OUTPUT_VARIABLE LLVM_INCLUDE_DIRS
                OUTPUT_STRIP_TRAILING_WHITESPACE )
execute_process(COMMAND ${LLVM_CONFIG_EXE} --cxxflags
                OUTPUT_VARIABLE LLVM_CXX_FLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE )
 execute_process(COMMAND ${LLVM_CONFIG_EXE} --ldflags
                OUTPUT_VARIABLE LLVM_LD_FLAGS
                OUTPUT_STRIP_TRAILING_WHITESPACE )
execute_process(COMMAND ${LLVM_CONFIG_EXE} --libs all
                OUTPUT_VARIABLE LLVM_LIBS
                OUTPUT_STRIP_TRAILING_WHITESPACE )


include_directories(${LLVM_INCLUDE_DIRS})

set(CMAKE_CXX_FLAGS "-fno-rtti -std=c++11 ${LLVM_CXX_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${LLVM_LD_FLAGS}")

# Now build our tools
add_executable(llvm-extractor main.cc)

# Link against LLVM libraries
target_link_libraries(llvm-extractor ${LLVM_LIBS} dl pthread curses)

SET(LLVM_EXTRACTOR "$<TARGET_FILE:llvm-extractor>" CACHE INTERNAL "")
