config_valid(VALID --equal --arch ARM --inline-scheduler=no)
if(VALID)

  DOSEK_BINARY(
    NAME zedboard
    SYSTEM_DESC system.oil
    LIBS libtest
    SOURCES dosek.cc;crc32.cc
    )
endif()

