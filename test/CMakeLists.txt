# Build all test cases and run ctest -V
# mainly for manual use on commandline
#

set(SRCS
  test.cc
)

add_library(libtest ${SRCS})


# The traditional 'make test' has no dependency on any
# test case. Here, we add all test cases as dependency
add_custom_target(tests)


add_custom_target(build_and_test
    ${CMAKE_CTEST_COMMAND} -V
    DEPENDS tests
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
    DEPENDS tests
    OUTPUT ${XUNITOUTPUT}
)
