# Get gem5 binary
set(GEM5_DIR "/proj/i4danceos/tools/fail/gem5" CACHE PATH "Directory containing gem5 binary")
find_program(GEM5 "gem5.debug" ${GEM5_DIR})
if(NOT GEM5)
	message(WARNING "[${PROJECT_NAME} No gem5 found, not generating gem5 targets!")
	return()
endif()

set(DEBUGGER "/srv/scratch/siflluka/gdb/gdb-7.7.1/gdb/gdb")

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	set(ELF_ABS ${PROJECT_BINARY_DIR}/${ELF})

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

	# GDB init file
	set(GDB_FEATURES_XML ${CMAKE_CURRENT_SOURCE_DIR}/arm-with-neon.xml)
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${SUFFIX}.gem5.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})

	# Common arguments
	set(GEM5_CONFIG ${PROJECT_SOURCE_DIR}/arch/arm/gem5/gem5panda.py)
	set(BOOTLOADER ${GEM5_DIR}/boot.arm)
	set(GEM5_ARGS ${GEM5_CONFIG} --kernel ${ELF_ABS} --bootloader ${BOOTLOADER}) #  --mem-size=${RAM_SIZE}MB

	# Start gem5
	add_custom_target(run-gem5-${ELF}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in gem5"
		COMMAND ${GEM5} ${GEM5_ARGS}
		COMMAND cat m5out/system.terminal
	)

	# Start gem5 for tests (only serial console)
	add_custom_target(test-gem5-${ELF}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in gem5 serial mode."
		COMMAND ${GEM5} ${GEM5_ARGS} &
		COMMAND sleep 1
		COMMAND telnet localhost 3456
	)

	# Start gem5 and attach debugger
	add_custom_target(debug-gem5-${ELF}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in gem5 debug mode. "
		COMMAND ${GEM5} ${GEM5_ARGS} &
        COMMAND sleep 1
		COMMAND ${DEBUGGER} -n -x ${GDBINITFILE} $<TARGET_FILE:${ELF}>
	)

	# Start debugger attach to gem5
	add_custom_target(debugger-gem5-${ELF}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Starting debugger for ${ELF}."
		WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
		COMMAND ${DEBUGGER} -n -x ${GDBINITFILE} $<TARGET_FILE:${ELF}>
	)
endforeach()
