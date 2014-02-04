# Build all test cases and run ctest -V
# mainly for manual use on commandline
#

set(SRCS
  test.cc
)

add_library(libtest ${SRCS})


# The traditional 'make test' has no dependency on any
# test case. Here, we add all test cases as dependency
# (in the coredos_test macro)
add_custom_target(build_and_test
    ${CMAKE_CTEST_COMMAND} -V
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    COMMENT "[${PROJECT_NAME}] Building testcases (only) and running CTest"
)


# Convert ctest output to xUnit format for jenkins
set(CONVERTPY ${PROJECT_SOURCE_DIR}/toolchain/ctest2jenkins/convert.py)
set(CONVXSL   ${PROJECT_SOURCE_DIR}/toolchain/ctest2jenkins/conv.xsl)
set(XUNITOUTPUT ${PROJECT_BINARY_DIR}/BaseTest.xml)


# Custom target generating xUnit output (see below)
add_custom_target( ctest2jenkins
    DEPENDS ${XUNITOUTPUT}
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    COMMENT "[${PROJECT_NAME}] Generating xUnit output of CTest results"
)

# Generate ExperimentalTest results and convert to xUnit xml output
add_custom_command(
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    COMMAND ctest -V  -D ExperimentalTest || true
    COMMAND python ${CONVERTPY} ${PROJECT_BINARY_DIR} ${CONVXSL} > BaseTest.xml
    OUTPUT ${XUNITOUTPUT}
)

# Helper to define test cases
# Usage: coredos_test(<testcasefilename>)
# (without .cc ending)
macro(coredos_test TEST)
    set(TESTELF "test-${TEST}.elf")

    # build test executable
    coredos_executable(${TESTELF} LIBS libtest SOURCES ${TEST}.cc ${ARGN})
    configure_file("${PROJECT_SOURCE_DIR}/os/test/linker.ld" "${CMAKE_CURRENT_BINARY_DIR}/test-${TEST}_linker.ld" COPYONLY)

    # add test to CTest
    coredos_test_iso_image(${TESTELF} test-${TEST} "${PROJECT_BINARY_DIR}/${TESTELF}.iso")
endmacro()


macro(coredos_test_iso_image TESTNAME NAME IMAGE)
    # add test to CTest
    add_test(${TESTNAME} qemu-system-i386 -no-reboot -nographic -cdrom ${IMAGE})
    set_tests_properties(${TESTNAME} PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS.+ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 10)
    add_dependencies( build_and_test iso-${NAME} )
    add_dependencies( ctest2jenkins iso-${NAME} )
endmacro()

