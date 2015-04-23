include(keso)

KESO_TRANSFORM(keso_gc_coffebreak dOSEK/gc_coffebreak.kcl .)

FILE(GLOB_RECURSE KESO_SOURCES
  RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
  "keso_gc_coffebreak/*.cpp")

config_valid(VALID --mpu false --systemcalls normal)
if(VALID)

DOSEK_BINARY(
  NAME keso_gc_coffebreak
  SYSTEM_DESC keso_gc_coffebreak/keso_main.oil
  GENERATOR_ARGS --ignore-interrupt-systemcalls yes
  TEST_ISO
  SOURCES
     ${KESO_SOURCES}
     shutdown.cc
)

endif()



