# TODO: make configurable
set(ZEDBOARD ON)

# Hardware dependent code
if(PANDABOARD)
	set(PLATFORM_DIR "pandaboard")
	message(STATUS "[${PROJECT_NAME}] ARM hardware platform: Pandaboard")
elseif(VEXPRESS_EMM)
	set(PLATFORM_DIR "vexpress_emm")
	message(STATUS "[${PROJECT_NAME}] ARM hardware platform: VExpress EMM")
elseif(ZEDBOARD)
	set(PLATFORM_DIR "zedboard" CACHE STRING "")
	message(STATUS "[${PROJECT_NAME}] ARM hardware platform: Zedboard")
else()
	message(FATAL_ERROR "Hardware platform not found :(")
endif()

set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR}/${PLATFORM_DIR} CACHE INTERNAL STRING)
