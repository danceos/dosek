DOSEK_BINARY(
  NAME bench-coptermock
  SYSTEM_DESC system.oil
  FAIL
  dosek.cc
)

## Should result in 1579971 system states for SSE
#DOSEK_BINARY(
#  NAME bench-coptermock-no-annotation
#  SYSTEM_DESC system-no-annotation.oil
#  dosek.cc
#)
