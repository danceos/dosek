macro(KESO_TRANSFORM name kcl outdir)
  if(EXISTS $ENV{KESOROOTPATH})
    SET(KESOROOTPATH $ENV{KESOROOTPATH})
    message(STATUS "KESO: ${KESOROOTPATH}")

    set(JINOFLAGS_${name} -nobuild -X:dbg_src:ssa:const_arg_prop:ssa_alias_prop CACHE STRING "the flags to pass to the JINO compiler")
    message(STATUS "JINOFLAGS: ${JINOFLAGS_${name}}")

    add_custom_target(transform-${name}
      COMMENT "Running the Java-to-C Compiler KESO"
      COMMAND bash -c 'cd ${KESOROOTPATH} && source ${KESOROOTPATH}/bin/setup.bash && cd src && env KESORC=${KESOROOTPATH}/src/rc/${kcl} KESOOUTPATH=${CMAKE_CURRENT_SOURCE_DIR}/${outdir} JINOFLAGS="${JINOFLAGS_${name}}" make'
      )

  else(EXISTS $ENV{KESOROOTPATH})
    message(INFO "Please set env variable KESOROOTPATH")
  endif(EXISTS $ENV{KESOROOTPATH})

endmacro()
