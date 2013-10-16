# Build all test cases and run ctest -V
# mainly for manual use on commandline
#
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

    # Executable for debugging tests
    coredos_executable("debug${TESTELF}" "${TEST}.cc")
    set_target_properties("debug${TESTELF}" PROPERTIES COMPILE_DEFINITIONS "DEBUG=1")
    set_target_properties("debug${TESTELF}" PROPERTIES EXCLUDE_FROM_ALL true)

    # Executable for FAIL* testing
    coredos_executable("fail${TESTELF}" "${TEST}.cc")
    set_target_properties("fail${TESTELF}" PROPERTIES COMPILE_DEFINITIONS "FAIL=1")
    set_target_properties("fail${TESTELF}" PROPERTIES EXCLUDE_FROM_ALL true)

    # The normal (CTest) test
    coredos_executable(${TESTELF} "${TEST}.cc")
    add_test(${TESTELF} qemu-system-i386 -no-reboot -nographic -kernel "${PROJECT_BINARY_DIR}/${TESTELF}")
    set_tests_properties(${TESTELF} PROPERTIES PASS_REGULAR_EXPRESSION "ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 10)
    add_dependencies( build_and_test ${TESTELF} )
    add_dependencies( ctest2jenkins ${TESTELF} )
endmacro()
