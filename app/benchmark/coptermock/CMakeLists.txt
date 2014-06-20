COREDOS_BINARY(
  NAME bench-coptermock
  SYSTEM_XML system.xml
  FAIL
  coredos.cc
)

## Should result in 1579971 system states for SSE
#COREDOS_BINARY(
#  NAME bench-coptermock-no-annotation
#  SYSTEM_XML system-no-annotation.xml
#  coredos.cc
#)
