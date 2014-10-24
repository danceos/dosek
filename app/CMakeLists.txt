include(app)

#set(DOSEK_APPS "bcc1_tasks" CACHE STRING "Application(s) to compile (semicolon seperated)")

SUBDIRLIST(SUBDIRS ${CMAKE_CURRENT_SOURCE_DIR})

FOREACH(subdir ${SUBDIRS})
  add_subdirectory(${subdir})
ENDFOREACH()

