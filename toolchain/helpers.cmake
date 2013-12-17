# List of include_directories (for cppcheck)
set(INCLUDEDIRS "" CACHE INTERNAL "List of include dirs")
set(INCLUDEDIRS_FLAGS "" CACHE INTERNAL "List of include dirs (in flag form)")


macro(coredos_include_dir IDIR)
    set(INCLUDEDIRS ${INCLUDEDIRS} ${IDIR})
    set(INCLUDEDIRS_FLAGS ${INCLUDEDIRS_FLAGS} -I${IDIR})

    include_directories(${IDIR})
endmacro()

MACRO(SHIFT RESULT LISTVAR)
  LIST(GET ${LISTVAR} 1 ${RESULT})
  LIST(REMOVE_AT ${LISTVAR} 1)
ENDMACRO(SHIFT)
