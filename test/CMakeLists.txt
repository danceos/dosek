macro(coredos_test TEST)
	coredos_executable("test-${TEST}.elf" "${TEST}.cc")
	add_test("test-${TEST}" qemu-system-i386 -no-reboot -nographic -kernel "${PROJECT_BINARY_DIR}/test-${TEST}.elf")
endmacro()
