COREDOS_BINARY(
  NAME sysmodel_1alarm_a
  SYSTEM_XML a.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME sysmodel_1alarm_aa
  SYSTEM_XML aa.xml # OTHER XML!
  VERIFY verify_aa.py
  LIBS libtest
  TEST_ISO
  a.cc
)
