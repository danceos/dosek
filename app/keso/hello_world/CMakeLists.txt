include(keso)

KESO_TRANSFORM(keso_helloworld dOSEK/hello_world.kcl .)

FILE(GLOB_RECURSE KESO_SOURCES
  RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
  "keso_helloworld/*.cpp")

if("${GENERATOR_ARGS}" MATCHES "--system-calls fsm")
else()

DOSEK_BINARY(
  NAME keso_helloworld
  SYSTEM_DESC keso_helloworld/keso_main.oil
  TEST_ISO
  SOURCES ${KESO_SOURCES} idle.cc
)

endif()


