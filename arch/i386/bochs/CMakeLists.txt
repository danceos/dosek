# Get bochs binary
find_program(BOCHS "bochs")
if(NOT BOCHS)
	message(WARNING "[${PROJECT_NAME}] No bochs found, not generating bochs targets!")
	return()
endif()

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	# Do not suffix targets for main executable
	if(${ELF} STREQUAL ${ELFFILE})
		set(SUFFIX "")
		set(DSUFFIX "")
	else()
		GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)
		set(DSUFFIX "-${SUFFIX}")
	endif()

	get_target_property(ELF_ABS ${ELF} LOCATION)
	set(ISOFILE "${ELF_ABS}.iso")

	# Bochs
	set(BOCHS_BIOS "${CMAKE_CURRENT_SOURCE_DIR}/BIOS-bochs-latest")
	set(BOCHS_GUEST_RAM ${RAM_SIZE})
	set(BOCHS_HOST_RAM ${RAM_SIZE})
	set(BOCHS_VGA_IMAGE "${CMAKE_CURRENT_SOURCE_DIR}/vgabios.bin")
	set(BOCHS_ISO_IMAGE "${ISOFILE}")

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

	set(BOCHSRC "${STARTUP_SCRIPTS}/bochsrc${DSUFFIX}")
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc.in" ${BOCHSRC} )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-gdb.in" "${BOCHSRC}-gdb" )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-term.in" "${BOCHSRC}-term" )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-nogui.in" "${BOCHSRC}-nogui" )

	# GDB init file
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${SUFFIX}.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})

	# Start bochs
	add_custom_target(run${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in Bochs."
		COMMAND ${BOCHS} -f ${BOCHSRC}
	)

	# Start bochs in terminal (for ssh)
	add_custom_target(runterm${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in Bochs term mode"
		COMMAND ${BOCHS} -f ${BOCHSRC}-term
	)

	# Start bochs with GDB stub for debugging
	add_custom_target(debug${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in Bochs with gdb"
		COMMAND ${BOCHS} -f ${BOCHSRC}-gdb
	)

	# Start debugger attach to bochs
	add_custom_target(debugger${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "Starting debugger for ${ISOFILE}..."
		WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
		COMMAND ${DEBUGGER} -n -x ${GDBINITFILE} $<TARGET_FILE:${ELF}>
	)
endforeach()
