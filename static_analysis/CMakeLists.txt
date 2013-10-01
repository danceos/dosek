
# Static C++ code analysis
find_program(CPPCHECK cppcheck
			PATHS /proj/i4danceos/tools/cppcheck/bin
)

if(CPPCHECK)
	add_custom_target( cppcheck
			COMMAND ${CPPCHECK} --enable=all ${PROJECT_SOURCE_DIR}
	)
else()
		message(STATUS "cppcheck executable not found, code quality not checked.")
endif()

# CCCC Code metrics
find_program(CCCC cccc)
if(CCCC)
	add_custom_target( cccc COMMAND ${CCCC}  ${CCCC_SOURCES})
else()
	message(STATUS "cccc executable not found, no code metrics available.")
endif()


# OClint static code analysis
find_program(OCLINT_JSON oclint-json-compilation-database
		PATHS /proj/i4danceos/tools/oclint/bin)

if(OCLINT_JSON)
	set(OCLINT_OUTPUT "${PROJECT_BINARY_DIR}/oclint.html")
	set(OCLINT_OUTPUT_PMD "${PROJECT_BINARY_DIR}/oclint.xml")

	add_custom_target( oclint
			COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type html -o ${OCLINT_OUTPUT}
			DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
			WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
	)

	add_custom_target( oclint-jenkins
		COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type pmd -o ${OCLINT_OUTPUT_PMD}
			DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
			WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
	)

	add_custom_target( oclint-static-analyzer
			COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type html -o ${OCLINT_OUTPUT} -enable-clang-static-analyzer
			DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
			WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
	)

	add_custom_target( oclint-jenkins-static-analyzer
		COMMAND ${OCLINT_JSON} -- -p ${PROJECT_BINARY_DIR} -report-type pmd -o ${OCLINT_OUTPUT_PMD} -enable-clang-static-analyzer
			DEPENDS "${PROJECT_BINARY_DIR}/compile_commands.json"
			WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
	)

else()
	message(STATUS "oclint executable not found, static analysis not available.")
endif()

