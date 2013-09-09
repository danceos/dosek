# List of include_directories (for cppcheck)
set(INCLUDEDIRS "" CACHE INTERNAL "List of include dirs")

macro(coredos_include_dir IDIR)
    set(INCLUDEDIRS ${INCLUDEDIRS} ${IDIR})
    include_directories(${IDIR})
endmacro()
