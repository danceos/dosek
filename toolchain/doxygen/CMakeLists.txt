### Setup doxygen documentation 
find_package(Doxygen)
if(DOXYGEN_FOUND)
# Using a .in file means we can use CMake to insert project settings
# into the doxyfile.  For example, CMake will replace @PROJECT_NAME@ in
# a configured file with the CMake PROJECT_NAME variable's value.
#
#set(DOXY_OUTPUT ${CMAKE_CURRENT_BINARY_DIR})
set(DOXY_OUTPUT /proj/i4danceos/coredos/doc)
set(DOXY_HTML_OUTPUT "html")
set(DOXY_XML_OUTPUT ${DOXY_OUTPUT}/xml CACHE INTERNAL "Path to doxygen xml data for sphinx/breathe")

set(DOXY_SOURCE "${PROJECT_SOURCE_DIR}")

# Do not include any build dir within the source tree
# Although a build folder should not lie within the source tree anyway.
set(DOXY_EXCLUDE_PATTERNS "${PROJECT_SOURCE_DIR}/build ${PROJECT_SOURCE_DIR}/toolchain ${CMAKE_CURRENT_SOURCE_DIR}")

file(MAKE_DIRECTORY ${DOXY_OUTPUT})

# Additional files regarding OSEK
set(OSEK_SPEC_PATH ${PROJECT_SOURCE_DIR}/doc/osek/osek)
set(OSEK_SPEC_PDF os223.pdf)
set(OSEK_TESTSPEC_PDF ostestplan20.pdf)

# Additional doc files regarding concepts
set(DOC_CONCEPTS_PATH ${PROJECT_SOURCE_DIR}/doc/concepts)
set(CONCEPT_FIG concepts.png)

set(DOXY_PY ${CMAKE_CURRENT_SOURCE_DIR}/doxypy.py)
set(DOXYFILE ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
configure_file(Doxyfile.in ${DOXYFILE}  @ONLY )

## call make doc to generate documentation
set(line0 "[${PROJECT_NAME}] Generating CoRedOS documentation with Doxygen")
set(line1 "       Directories: ${DOXY_SOURCE}")
set(line2 "       Excluded patterns: ${DOXY_EXCLUDE_PATTERNS}")
set(line3 "       HTML output: ${DOXY_OUTPUT}/${DOXY_HTML_OUTPUT}")

add_custom_target(doc
  ${DOXYGEN_EXECUTABLE} ${DOXYFILE}
  DEPENDS ${DOXYFILE}
  COMMENT "${line0}\n${line1}\n${line2}\n${line3}" VERBATIM
)

endif(DOXYGEN_FOUND)

