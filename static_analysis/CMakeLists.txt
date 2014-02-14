# Determine browser to open HTML results
find_program(BROWSER sensible-browser)
if(BROWSER)
	set(BROWSER_OPEN on CACHE BOOL "Open browser after generating HTML reports")
else()
	set(BROWSER_OPEN off CACHE BOOL "Open browser after generating HTML reports")
endif()

# Static C++ code analysis
find_program(CPPCHECK cppcheck
   PATHS /proj/i4danceos/tools/cppcheck/bin
)

if(CPPCHECK)
    set(CPPINCLUDES ${CMAKE_CURRENT_BINARY_DIR}/cppcheck_includes.txt)
    foreach(dir ${INCLUDEDIRS})
        file(APPEND ${CPPINCLUDES} "${dir}\n")
    endforeach()
#    if(BUILD_posix)
        file(APPEND ${CPPINCLUDES} "/usr/include\n")
        file(APPEND ${CPPINCLUDES} "/usr/include/linux\n")
#    endif()


    add_custom_target( cppcheck
        COMMAND ${CPPCHECK} --check-config --enable=all -q --enable=all --xml --std=c++11 ${PROJECT_SOURCE_DIR} --includes-file=${CPPINCLUDES} -i ${PROJECT_BINARY_DIR} 2> ${PROJECT_BINARY_DIR}/cppcheck-result.xml
        )
else()
  message(STATUS "[${PROJECT_NAME}] cppcheck executable not found, code quality not checked.")
endif()

# CCCC Code metrics
find_program(CCCC cccc)
if(CCCC)

    add_custom_target( cccc
        COMMAND ${CCCC} --outdir=${PROJECT_BINARY_DIR}/cccc ${CCCC_SOURCES}
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND ${CMAKE_COMMAND} -E echo CCCC results: ${PROJECT_BINARY_DIR}/cccc/cccc.html
    )
    if(BROWSER_OPEN)
        add_custom_command( TARGET cccc
            POST_BUILD
            COMMAND ${BROWSER} ${PROJECT_BINARY_DIR}/cccc/cccc.html
        )
    endif()
else()
    message(STATUS "cccc executable not found, no code metrics available.")
endif()


# OClint static code analysis
find_program(OCLINT_JSON oclint-json-compilation-database
        PATHS /proj/i4danceos/tools/oclint/bin)

if(OCLINT_JSON)

    set(OCLINT_OUTPUT "${PROJECT_BINARY_DIR}/oclint.html")
    set(OCLINT_OUTPUT_PMD "${PROJECT_BINARY_DIR}/oclint.xml")
    set(SHORT_VARIABLE_THRS "-rc SHORT_VARIABLE_NAME=2")

    add_custom_target( oclint
        COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type html -o ${OCLINT_OUTPUT} ${SHORT_VARIABLE_THRS}
            DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    )

    add_custom_target( oclint-jenkins
        COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type pmd -o ${OCLINT_OUTPUT_PMD} ${SHORT_VARIABLE_THRS}
            DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    )

    add_custom_target( oclint-static-analyzer
            COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type html -o ${OCLINT_OUTPUT} ${SHORT_VARIABLE_THRS} -enable-clang-static-analyzer
            DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    )

    add_custom_target( oclint-jenkins-static-analyzer
        COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type pmd -o ${OCLINT_OUTPUT_PMD} ${SHORT_VARIABLE_THRS} -enable-clang-static-analyzer
            DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
    )

    if(BROWSER_OPEN)
        add_custom_command( TARGET oclint POST_BUILD
            COMMAND ${BROWSER} ${OCLINT_OUTPUT}
        )
        add_custom_command( TARGET oclint-static-analyzer POST_BUILD
            COMMAND ${BROWSER} ${OCLINT_OUTPUT}
        )

    endif()

else()
  message(STATUS "[${PROJECT_NAME}] oclint executable not found")
endif()

find_program(PYLINT pylint)
if(PYLINT)
  add_custom_command(
	  COMMAND find ./ -iname \"*.py\" | PYTHONPATH=${PROJECT_SOURCE_DIR} xargs ${PYLINT} 
	  	--output-format=parseable 
		--rcfile=${PROJECT_SOURCE_DIR}/static_analysis/pylint.rc
		   > ${PROJECT_BINARY_DIR}/pylint.txt
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/generator
    OUTPUT ${PROJECT_BINARY_DIR}/pylint.txt
  )

  add_custom_target(pylint
    DEPENDS ${PROJECT_BINARY_DIR}/pylint.txt
  )

else()
  message(STATUS "[${PROJECT_NAME}] pylint executable not found")

endif()

