DOSEK_BINARY(
  NAME bench-coptermock
  SYSTEM_DESC system.oil
  FAIL
  dosek.cc
)

# The bench-coptermock-isorc application is a very precise replication
# of the experiments from our ISORC'13 Paper. It reveals 110
# Tracepoints @ 50Mhz on i386. The whole testrun needs 1.30 seconds.
config_valid(VALID --systemcalls normal)
if(VALID)

DOSEK_BINARY(
  NAME bench-coptermock-isorc
  SYSTEM_DESC isorc.oil
  TEST_DISABLE
  FAIL
  isorc.cc
)

endif()


## Should result in 1579971 system states for SSE
#DOSEK_BINARY(
#  NAME bench-coptermock-no-annotation
#  SYSTEM_DESC system-no-annotation.oil
#  dosek.cc
#)
