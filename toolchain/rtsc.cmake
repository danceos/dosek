# The RTSC Source code and a compiled rtsc version
SET(RTSC_SOURCE_DIR "/proj/i4danceos/tools/rtsc/rtsc" CACHE STRING "Source directory of the RTSC")
SET(RTSC_BINARY_DIR "/proj/i4danceos/tools/rtsc/rtscbuild" CACHE STRING "Build directory of the RTSC")
SET(RTSC_LLVM_BINARY_DIR "/proj/i4danceos/tools/rtsc/llvmbuild" CACHE STRING "Build directory of the LLVM (used for RTSC)")

SET(EAG_BINARY "${RTSC_BINARY_DIR}/bin/eag")
SET(CLANG_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/clang")
SET(CLANGPP_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/clang++")
SET(LLVM_NM_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/llvm-nm")
SET(LLVM_LINK_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/llvm-link")
SET(LLVM_OPT_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/opt")
SET(LLVM_LLC_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/llc")
SET(LLVM_LD_BINARY "${RTSC_LLVM_BINARY_DIR}/bin/llvm-ld")


