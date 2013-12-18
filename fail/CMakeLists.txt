# FAIL* options
set(FAIL_TOOLS_DIR "/proj/i4danceos/coredos/cored-tester" CACHE PATH "Directory containing FAIL* tester binaries")
if(NOT FAIL_TOOLS_DIR)
	message(WARNING "[${PROJECT_NAME}] FAIL_TOOLS_DIR not set! FAIL* testing will not work!")
endif()

set(FAIL_VARIANT "${PROJECT_NAME}" CACHE STRING "FAIL* variant name")
set(FAIL_PRUNER "basic" CACHE STRING "FAIL* pruner")
set(FAIL_NICE "19" CACHE STRING "Nice value for FAIL* clients")
set(FAIL_DBNAME "" CACHE STRING "FAIL* database name (taken from ~/my.cnf when empty)")
set(FAIL_HOSTNAME "" CACHE STRING "FAIL* MySQL server (taken from ~/my.cnf when empty)")
set(FAIL_USERNAME "" CACHE STRING "FAIL* MySQL username (taken from ~/my.cnf or username when empty)")
site_name(HOSTNAME)
set(FAIL_SERVERNAME ${HOSTNAME} CACHE STRING "FAIL* server hostname")

# find tools
find_program(FAIL_TRACE "fail-x86-tracing" ${FAIL_TOOLS_DIR})
find_program(FAIL_IMPORT "import-trace" ${FAIL_TOOLS_DIR})
find_program(FAIL_PRUNE "prune-trace" ${FAIL_TOOLS_DIR})
find_program(FAIL_SERVER "cored-tester-server" ${FAIL_TOOLS_DIR})
find_program(FAIL_CLIENT "cored-tester-client" ${FAIL_TOOLS_DIR})
find_program(OBJDUMP "objdump")
find_program(NICE "nice")

# DB options
set(FAIL_DBOPTS "")
if(FAIL_DBNAME)
	set(FAIL_DBOPTS ${FAIL_DBOPTS} -d ${FAIL_DBNAME})
endif()
if(FAIL_HOSTNAME)
	set(FAIL_DBOPTS ${FAIL_DBOPTS} --hostname ${FAIL_HOSTNAME})
endif()
if(FAIL_USERNAME)
	set(FAIL_DBOPTS ${FAIL_DBOPTS} -u ${FAIL_USERNAME})
endif()

# parallel options
find_program(PARALLEL "parallel")
if(PARALLEL)
	set(PARALLEL_SSHFILE "" CACHE FILEPATH "SSH login file to distribute FAIL* clients using parallel")
	if(PARALLEL_SSHFILE)
		message(STATUS "[${PROJECT_NAME}] Running FAIL* on all hosts specified in ${PARALLEL_SSHFILE}")
	endif()
else()
	message(WARNING "[${PROJECT_NAME}] GNU parallel not found, can only run FAIL* locally")
endif()

# targets to run all FAIL* tests
foreach(BENCHMARK "mem" "regs" "ip" "jump")
	add_custom_target(fail-all-${BENCHMARK})
endforeach()

# create FAIL* targets
# TNAME: test name
# ELF: test .elf path
# TEST: which FAIL* test to run (mem/regs/ip/jump)
macro(fail_targets TNAME ELF TEST)
	set(BENCHMARK "${TNAME}-${TEST}")

	# scripts
	set(CLIENT_CMD ${PYTHON} ${PROJECT_SOURCE_DIR}/fail/fail-runner.py)

	# common options
	set(FAIL_OPTS ${FAIL_DBOPTS} -v ${FAIL_VARIANT} -b ${BENCHMARK})

	# common targets (create only once for all tests)
	if(NOT FAIL_SETUP_${TNAME})
		set(FAIL_SETUP_${TNAME} true CACHE INTERNAL "Common FAIL* targets alredy setup")

		# TODO: make architecture independent
		set(BOCHSRC "${PROJECT_BINARY_DIR}/startup_scripts/bochsrc-fail-${TNAME}-nogui")

		# tracing
		set(TRACEFILE "${FAIL_DIR}/trace.pb")
		set(STATEDIR "${FAIL_DIR}/state")
		add_custom_command(
			DEPENDS ${ELF} iso-fail-${TNAME}
			COMMAND ${CMAKE_COMMAND} -E remove_directory ${STATEDIR}
			COMMAND ${FAIL_TRACE} -f ${BOCHSRC} -q
				-Wf,--start-symbol=_trace_start_marker
				-Wf,--save-symbol=_trace_start_marker
				-Wf,--end-symbol=_trace_end_marker
				-Wf,--trace-file=trace.pb
				-Wf,--elf-file=${ELF}
			COMMENT "Tracing ${ELF} for ${FAIL_VARIANT}/${BENCHMARK}"
			WORKING_DIRECTORY ${FAIL_DIR}
			OUTPUT ${TRACEFILE} ${STATEDIR} ${FAIL_DIR}/bochsout.txt ${FAIL_DIR}/serial.out
		)
		add_custom_target(fail-trace-${TNAME} DEPENDS ${TRACEFILE})

		# extract {data, text, stack}_map
		set(FAIL_MAPPER "${PROJECT_SOURCE_DIR}/fail/mapper.py")
		add_custom_command(
			DEPENDS ${ELF}
			COMMAND ${PYTHON} ${FAIL_MAPPER} -e ${ELF} -o ${OBJDUMP}
			COMMENT "Extracting memory maps from ${ELF} for ${FAIL_VARIANT}/${BENCHMARK}"
			WORKING_DIRECTORY ${FAIL_DIR}
			OUTPUT ${FAIL_DIR}/text_map ${FAIL_DIR}/data_map ${FAIL_DIR}/stack_map
		)
		add_custom_target(fail-map-${TNAME}
			DEPENDS ${FAIL_DIR}/text_map ${FAIL_DIR}/data_map ${FAIL_DIR}/stack_map
		)

		# test client
		if(PARALLEL AND PARALLEL_SSHFILE)
			set(PARALLEL_CMD ${PARALLEL} --gnu -q
				-u --wd . --nonall -j0 -S : --slf ${PARALLEL_SSHFILE}
			)
		endif()
		if(NICE)
			set(PARALLEL_CMD ${PARALLEL_CMD} ${NICE} -n ${FAIL_NICE})
		endif()
		add_custom_target(fail-client-${TNAME}
			COMMAND ${PARALLEL_CMD} ${CLIENT_CMD}
				-e ${ELF} -f ${FAIL_CLIENT} -S ${FAIL_SERVERNAME}
			COMMENT "Starting FAIL* test clients..."
			WORKING_DIRECTORY ${FAIL_DIR}
			DEPENDS ${ELF} ${STATEDIR}
		)
		add_custom_target(fail-client-oneshot-${TNAME}
			COMMAND ${CLIENT_CMD} -e ${ELF} -f ${FAIL_CLIENT} -1 -S ${FAIL_SERVERNAME}
			COMMENT "Starting one FAIL* test client..."
			WORKING_DIRECTORY ${FAIL_DIR}
			DEPENDS ${ELF} ${STATEDIR}
		)
	endif()

	# import objdump
	set(OBJDUMPED_FILE ${FAIL_DIR}/.objdumped.${TEST})
	add_custom_command(
		COMMAND ${FAIL_IMPORT} ${FAIL_OPTS} -t ${TRACEFILE} -i ObjdumpImporter
			-e ${ELF} --objdump ${OBJDUMP}
		COMMAND ${CMAKE_COMMAND} -E touch ${OBJDUMPED_FILE}
		COMMENT "Importing ${ELF} into database for ${FAIL_VARIANT}/${BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		DEPENDS ${TRACEFILE}
		OUTPUT ${OBJDUMPED_FILE}
	)
	add_custom_target(fail-objdump-${BENCHMARK} DEPENDS ${OBJDUMPED_FILE})

	# importer
	if(${TEST} STREQUAL "mem")
		set(IMPORTER "MemoryImporter")
		set(IMPORTER_ARGS -m ${FAIL_DIR}/data_map -m ${FAIL_DIR}/stack_map)
		set(IMPORTER_DEPEND ${FAIL_DIR}/data_map ${FAIL_DIR}/stack_map)
	elseif(${TEST} STREQUAL "regs")
		set(IMPORTER "RegisterImporter")
		set(IMPORTER_ARGS --flags)
		set(IMPORTER_DEPEND "")
	elseif(${TEST} STREQUAL "ip")
		set(IMPORTER "RegisterImporter")
		set(IMPORTER_ARGS --no-gp --ip)
		set(IMPORTER_DEPEND "")
	elseif(${TEST} STREQUAL "jump")
		set(IMPORTER "RandomJumpImporter")
		set(IMPORTER_ARGS --jump-from ${FAIL_DIR}/text_map --jump-to ${FAIL_DIR}/text_map)
		set(IMPORTER_DEPEND ${FAIL_DIR}/text_map)
	else()
		message(ERROR "[${PROJECT_NAME}] Unknown FAIL* importer type!")
	endif()

	set(IMPORTED_FILE ${FAIL_DIR}/.imported.${TEST})
	add_custom_command(
		DEPENDS ${TRACEFILE} ${ELF} ${IMPORTER_DEPEND} ${OBJDUMPED_FILE}
		COMMAND ${FAIL_IMPORT} -t ${TRACEFILE} -i ${IMPORTER}
			-e ${ELF} ${FAIL_OPTS} ${IMPORTER_ARGS}
		COMMAND ${CMAKE_COMMAND} -E touch ${IMPORTED_FILE}
		COMMENT "Importing ${ELF} into database for ${FAIL_VARIANT}/${BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		OUTPUT ${IMPORTED_FILE}
	)
	add_custom_target(fail-import-${BENCHMARK} DEPENDS ${IMPORTED_FILE})

	# pruner
	set(PRUNED_FILE ${FAIL_DIR}/.pruned.${TEST})
	add_custom_command(
		DEPENDS ${IMPORTED_FILE}
		COMMAND ${FAIL_PRUNE} ${FAIL_OPTS} -p ${FAIL_PRUNER}
		COMMAND ${CMAKE_COMMAND} -E touch ${PRUNED_FILE}
		COMMENT "Pruning ${FAIL_VARIANT}/${BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		OUTPUT ${PRUNED_FILE}
	)
	add_custom_target(fail-prune-${BENCHMARK} DEPENDS ${PRUNED_FILE})

	# start test server
	add_custom_target(fail-server-${BENCHMARK}
		COMMAND ${FAIL_SERVER} ${FAIL_OPTS} -p ${FAIL_PRUNER}
		DEPENDS ${PRUNED_FILE}
		COMMENT "Starting FAIL* test server..."
		WORKING_DIRECTORY ${FAIL_DIR}
	)

	# start test server and clients
	# will start server only on FAIL_SERVERNAME when run distributed
	add_custom_target(fail-${BENCHMARK}
		COMMAND ${PARALLEL_CMD} ${CLIENT_CMD} -e ${ELF} -f ${FAIL_CLIENT}
			-S ${FAIL_SERVERNAME} -s \"${FAIL_SERVER} ${FAIL_OPTS} -p ${FAIL_PRUNER}\"
		DEPENDS ${PRUNED_FILE} ${ELF} ${STATEDIR}
		COMMENT "Starting FAIL* test server (on ${FAIL_SERVERNAME}) and clients..."
		WORKING_DIRECTORY ${FAIL_DIR}
	)
	# add to fail-all- target
	add_dependencies(fail-all-${TEST} fail-${BENCHMARK})
endmacro()

# Helper to define FAIL* test cases
# Usage: fail_test(<testcasefilename>)
# (without .cc ending)
macro(fail_test TEST)
	# directory for this FAIL* target
	set(FAIL_DIR "${PROJECT_BINARY_DIR}/fail-${TEST}")
	file(MAKE_DIRECTORY ${FAIL_DIR})

	# executable for FAIL*
	set(TESTELF "fail-${TEST}.elf")
	coredos_executable("${TESTELF}" EXCLUDE_FROM_ALL ${TEST}.cc)
	set_target_properties("${TESTELF}" PROPERTIES COMPILE_DEFINITIONS "FAIL=1")
	set_target_properties("${TESTELF}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${FAIL_DIR})
	set_target_properties("${TESTELF}" PROPERTIES EXCLUDE_FROM_ALL true)

	# generate FAIL* targets
	message(STATUS "[${PROJECT_NAME}] Adding FAIL* targets for ${TESTELF} in ${FAIL_DIR}")
	set(FAIL_SETUP_${TEST} false CACHE INTERNAL "Common FAIL* targets already setup")
	foreach(BENCHMARK "mem" "regs" "ip" "jump")
		fail_targets(${TEST} ${FAIL_DIR}/${TESTELF} ${BENCHMARK})
	endforeach()
endmacro()

# Convenience macro for combined CoRed and FAIL* tests
macro(coredos_fail_test TEST)
	coredos_test(${TEST})
	fail_test(${TEST})
endmacro()
