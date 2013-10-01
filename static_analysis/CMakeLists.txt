
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

else()
	message(STATUS "oclint executable not found, static analysis not available.")
endif()

