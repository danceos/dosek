include(app)

set(COREDOS_APPS "bcc1_tasks" CACHE STRING "Application(s) to compile (semicolon seperated)")

foreach(app_name ${COREDOS_APPS})
    add_subdirectory(${app_name})
endforeach(app_name)
