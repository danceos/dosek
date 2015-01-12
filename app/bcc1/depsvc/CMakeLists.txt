if( (${DOSEK_ARCHITECTURE} STREQUAL "posix") OR (${DOSEK_ARCHITECTURE} STREQUAL "i386") )
  DOSEK_BINARY (
    NAME bcc1_depsvc
    LIBS libdepsvc libtest
    SYSTEM_DESC system.oil
    TEST_ISO
    depsvc.cc
    )
endif()
