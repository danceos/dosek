if(BUILD_ARM)
  DOSEK_BINARY(
    NAME zedboard
    SYSTEM_DESC system.oil
    LIBS libtest
    SOURCES dosek.cc;crc32.cc
    )
endif()

