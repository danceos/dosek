# FAIL* options
set(FAIL_TOOLS_DIR "/proj/i4danceos/tools/fail" CACHE PATH "Directory containing FAIL* tester binaries")
if(NOT FAIL_TOOLS_DIR)
	message(WARNING "[${PROJECT_NAME}] FAIL_TOOLS_DIR not set! FAIL* testing will not work!")
endif()

set(FAIL_PRUNER "basic" CACHE STRING "FAIL* pruner")
set(FAIL_DBNAME "" CACHE STRING "FAIL* database name (taken from ~/my.cnf when empty)")
set(FAIL_HOSTNAME "" CACHE STRING "FAIL* MySQL server (taken from ~/my.cnf when empty)")
set(FAIL_USERNAME "" CACHE STRING "FAIL* MySQL username (taken from ~/my.cnf or username when empty)")
site_name(HOSTNAME)
set(FAIL_SERVERNAME ${HOSTNAME} CACHE STRING "FAIL* server hostname")

# find tools
find_program(FAIL_TRACE "cored-tracing" ${FAIL_TOOLS_DIR})
find_program(FAIL_IMPORT "import-trace" ${FAIL_TOOLS_DIR})
find_program(FAIL_PRUNE "prune-trace" ${FAIL_TOOLS_DIR})
find_program(FAIL_SERVER "cored-tester-server" ${FAIL_TOOLS_DIR})
find_program(FAIL_CLIENT "cored-tester-client" ${FAIL_TOOLS_DIR})
find_program(OBJDUMP "objdump")
find_program(GIT "git")
find_program(PROTOC "protoc")

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

# TracePlugin python version
SET(FAIL_TRACE_PLUGIN_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/TracePlugin.proto")
SET(FAIL_TRACE_PLUGIN_PYTHON "${CMAKE_CURRENT_BINARY_DIR}/TracePlugin_pb2.py" CACHE INTERNAL "TracePlugin_pb2.py")
add_custom_target(fail-trace-plugin-python
  DEPENDS ${FAIL_TRACE_PLUGIN_SOURCE}
  COMMAND ${PROTOC} 
		  -I${CMAKE_CURRENT_SOURCE_DIR} ${FAIL_TRACE_PLUGIN_SOURCE} 
		  --python_out=${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Compiling fail TracePlugin.proto"
  OUTPUT  ${FAIL_TRACE_PLUGIN_PYTHON}
)

# target to trace everything traceable
add_custom_target(fail-trace-all)

# targets to run all FAIL* tests
foreach(BENCHMARK "mem" "regs" "ip" "jump")
	add_custom_target(fail-all-${BENCHMARK})
  endforeach()

  
# Get the current Git Revision
set(GIT_REV_FILE ${PROJECT_BINARY_DIR}/.gitrev)
set(CHECK_WORKSPACE ${PROJECT_SOURCE_DIR}/fail/check-workspace.py CACHE INTERNAL "")
if(NOT EXISTS ${GIT_REV_FILE})
  execute_process(COMMAND ${PYTHON} ${CHECK_WORKSPACE} -w ${PROJECT_SOURCE_DIR} -o ${GIT_REV_FILE} -g ${GIT} -f)
endif()
file(READ ${GIT_REV_FILE} GIT_REV)
string(STRIP ${GIT_REV} GIT_REV)
set(GIT_REV "${GIT_REV}" CACHE INTERNAL "")

# re-run cmake if GIT_REV_FILE changes
configure_file(${GIT_REV_FILE} ${GIT_REV_FILE}.tmp COPYONLY)
file(REMOVE ${GIT_REV_FILE}.tmp) # discard dummy output file

macro(fail_get_variant TNAME TEST)
  set(FAIL_VARIANT "${PROJECT_NAME}-${GIT_REV}/")
  set(FAIL_BENCHMARK "${TNAME}-${TEST}")

  if(CONFIG_ARCH_MPU)
	set(FAIL_VARIANT "${FAIL_VARIANT}+mpu")
  endif()
  if(CONFIG_ARCH_PRIVILEGE_ISOLATION)
	set(FAIL_VARIANT "${FAIL_VARIANT}+priv")
  endif()
  if(CONFIG_OS_SPECIALIZE)
	set(FAIL_VARIANT "${FAIL_VARIANT}+opt")
  endif()
  if(CONFIG_DEPENDABILITY_ENCODED)
	set(FAIL_VARIANT "${FAIL_VARIANT}+encoded")
  endif()
  if(CONFIG_DEPENDABILITY_STATE_ASSERTS)
	set(FAIL_VARIANT "${FAIL_VARIANT}+ass")
  endif()
  if(CONFIG_DEPENDABILITY_CFG_REGIONS)
	set(FAIL_VARIANT "${FAIL_VARIANT}+cfg")
  endif()

endmacro()

# create FAIL* targets
# TNAME: test name
# ELF: test .elf path
# TEST: which FAIL* test to run (mem/regs/ip/jump)
macro(fail_targets TNAME ELF TEST)
    fail_get_variant(${TNAME} ${TEST})
	set(FAIL_OPTS ${FAIL_DBOPTS} -v ${FAIL_VARIANT} -b ${FAIL_BENCHMARK})

	# import objdump
	set(OBJDUMPED_FILE ${FAIL_DIR}/.objdumped.${TEST})
	add_custom_command(
		COMMAND ${FAIL_IMPORT} ${FAIL_OPTS} -t ${TRACEFILE} -i ElfImporter
		         -e ${ELF} --objdump ${OBJDUMP} --sources
        COMMAND ${FAIL_IMPORT} -t ${TRACEFILE} -i FullTraceImporter ${FAIL_OPTS}
		COMMAND ${CMAKE_COMMAND} -E touch ${OBJDUMPED_FILE}
		COMMENT "Importing ${ELF} into database for ${FAIL_VARIANT}/${FAIL_BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		DEPENDS ${TRACEFILE}
		OUTPUT ${OBJDUMPED_FILE}
	)
	add_custom_target(fail-objdump-${FAIL_BENCHMARK} DEPENDS ${OBJDUMPED_FILE})

	# importer
	if(${TEST} STREQUAL "mem")
		set(IMPORTER "MemoryImporter")
		set(IMPORTER_ARGS "") #-m ${FAIL_DIR}/data_map -m ${FAIL_DIR}/stack_map)
		set(IMPORTER_DEPEND "") #${FAIL_DIR}/data_map ${FAIL_DIR}/stack_map)
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
		DEPENDS ${TRACEFILE} ${ELF} ${IMPORTER_DEPEND}
		COMMAND ${FAIL_IMPORT} -t ${TRACEFILE} --elf-file ${ELF} -i ${IMPORTER} ${FAIL_OPTS} ${IMPORTER_ARGS}
		COMMAND ${CMAKE_COMMAND} -E touch ${IMPORTED_FILE}
		COMMENT "Importing ${ELF} into database for ${FAIL_VARIANT}/${FAIL_BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		OUTPUT ${IMPORTED_FILE}
	)
  add_custom_target(fail-import-${FAIL_BENCHMARK} DEPENDS ${IMPORTED_FILE})
  add_dependencies(fail-import-${TNAME} fail-import-${FAIL_BENCHMARK})

	# pruner
	set(PRUNED_FILE ${FAIL_DIR}/.pruned.${TEST})
	add_custom_command(
		DEPENDS ${IMPORTED_FILE}
		COMMAND ${FAIL_PRUNE} ${FAIL_OPTS} -p ${FAIL_PRUNER}
		COMMAND ${CMAKE_COMMAND} -E touch ${PRUNED_FILE}
		COMMENT "Pruning ${FAIL_VARIANT}/${FAIL_BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		OUTPUT ${PRUNED_FILE}
	)
    add_custom_target(fail-prune-${FAIL_BENCHMARK} DEPENDS ${PRUNED_FILE})
    add_dependencies(fail-prune-${TNAME} fail-prune-${FAIL_BENCHMARK})
    add_dependencies(fail-server-${TNAME} fail-prune-${FAIL_BENCHMARK})

	# start test server
	add_custom_target(fail-server-${FAIL_BENCHMARK}
		COMMAND ${FAIL_SERVER} ${FAIL_OPTS} -p ${FAIL_PRUNER}
		DEPENDS ${PRUNED_FILE}
		COMMENT "Starting FAIL* test server..."
		WORKING_DIRECTORY ${FAIL_DIR}
    )

endmacro()

macro(fail_test TEST TESTELF)
	# directory for FAIL* test
	set(FAIL_DIR "${PROJECT_BINARY_DIR}/fail-${TEST}")
	file(MAKE_DIRECTORY ${FAIL_DIR})

	set_target_properties("${TESTELF}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${FAIL_DIR})
	set_target_properties("${TESTELF}" PROPERTIES EXCLUDE_FROM_ALL true)

    fail_get_variant(${TEST} "%")
	# generate FAIL* targets
	message(STATUS "[${PROJECT_NAME}] Adding FAIL* targets for ${TESTELF} in ${FAIL_DIR}")

    # Add general tagers
    add_custom_target(fail-import-${TEST})
    add_custom_target(fail-prune-${TEST} DEPENDS fail-import-${TEST})

    # TODO: make architecture independent
	set(BOCHSRC "${PROJECT_BINARY_DIR}/startup_scripts/bochsrc-fail-${TEST}-nogui")
    

	# Tracing
	set(TRACEFILE "${FAIL_DIR}/trace.pb")
	set(CHECKPOINTFILE "${FAIL_DIR}/checkpoint.trace")
	set(STATEDIR "${FAIL_DIR}/state")
    set(ELF ${FAIL_DIR}/${TESTELF})
	set(STATS_BINARY ${DOSEK_GENERATOR_DIR}/stats_binary.py)
	set(STATS_TRACE ${PROJECT_SOURCE_DIR}/fail/trace-analyze.py)
	set(STATS_DICT ${DOSEK_OUTPUT_DIR}/stats.dict.py)
    find_program(GIT "git")
	add_custom_command(
	  DEPENDS ${ELF} iso-fail-${TEST} ${GIT_REV_FILE} fail-trace-plugin-python ${STATS_BINARY} ${STATS_TRACE}
	  COMMAND ${PYTHON} ${CHECK_WORKSPACE} -w ${PROJECT_SOURCE_DIR} -o ${PROJECT_BINARY_DIR}/.gitrev -g ${GIT}
	  COMMAND ${CMAKE_COMMAND} -E remove_directory ${STATEDIR}
	  COMMAND ${FAIL_TRACE} -f ${BOCHSRC} -q
			-Wf,--start-symbol=test
			-Wf,--save-symbol=test
			-Wf,--end-symbol=test_finish
			-Wf,--trace-file=trace.pb
			-Wf,--elf-file=${ELF}
		COMMAND ${PYTHON} ${STATS_BINARY}
			--stats-dict ${STATS_DICT}
			--elf ${ELF}
		COMMAND PYTHONPATH=${PROJECT_SOURCE_DIR} ${STATS_TRACE}
			--stats-dict ${STATS_DICT}
			--elf ${ELF}
            --nm ${CROSS_NM}
			--trace ${TRACEFILE}
			--trace-plugin ${FAIL_TRACE_PLUGIN_PYTHON}
		COMMENT "Tracing ${ELF} for ${FAIL_VARIANT}/${BENCHMARK}"
		WORKING_DIRECTORY ${FAIL_DIR}
		OUTPUT ${TRACEFILE} ${CHECKPOINTFILE} ${STATEDIR} ${STATS_DICT}
	)
	add_custom_target(fail-trace-${TEST} DEPENDS ${TRACEFILE})
	add_dependencies(fail-trace-all fail-trace-${TEST})

    # scripts
	set(CLIENT_CMD ${PYTHON} ${PROJECT_SOURCE_DIR}/fail/fail-runner.py)
	add_custom_target(fail-client-${TEST}
		COMMAND ${PARALLEL_CMD} ${CLIENT_CMD}
			-e ${ELF} -f ${FAIL_CLIENT} -S ${FAIL_SERVERNAME}
		COMMENT "Starting FAIL* test clients..."
		WORKING_DIRECTORY ${FAIL_DIR}
		DEPENDS ${ELF} ${STATEDIR} ${CHECKPOINTFILE}
	)
	add_custom_target(fail-client-oneshot-${TEST}
		COMMAND ${CLIENT_CMD} -e ${ELF} -f ${FAIL_CLIENT} -1 -S ${FAIL_SERVERNAME}
		COMMENT "Starting one FAIL* test client..."
		WORKING_DIRECTORY ${FAIL_DIR}
		DEPENDS ${ELF} ${STATEDIR} ${CHECKPOINTFILE}
	)

    # Server for all benchmarks
	add_custom_target(fail-server-${TEST}
		COMMAND ${FAIL_SERVER} -v ${FAIL_VARIANT} -b ${FAIL_BENCHMARK} -p ${FAIL_PRUNER}
		DEPENDS fail-prune-${TEST}
		COMMENT "Starting FAIL* test server..."
		WORKING_DIRECTORY ${FAIL_DIR}
    )

	foreach(BENCHMARK "mem" "regs" "ip")
		fail_targets(${TEST} ${ELF} ${BENCHMARK})
	endforeach()


endmacro()

