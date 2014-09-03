DOSEK_BINARY(
  NAME sysmodel_1alarm_a
  SYSTEM_DESC a.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME sysmodel_1alarm_aa
  SYSTEM_DESC aa.xml # OTHER XML!
  VERIFY verify_aa.py
  LIBS libtest
  TEST_ISO
  a.cc
)
