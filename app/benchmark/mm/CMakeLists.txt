if(BUILD_ARM)
  add_library(libmatrix_mult mm.cc mat_final.cc)
  DOSEK_BINARY(
    NAME zedboard-mm
    SYSTEM_DESC system.oil
    LIBS libmatrix_mult
    SOURCES dosek.cc 
    )
endif()

