include(app)

SUBDIRLIST(SUBDIRS ${CMAKE_CURRENT_SOURCE_DIR})

FOREACH(subdir ${SUBDIRS})
  add_subdirectory(${subdir})
ENDFOREACH()

