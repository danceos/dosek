#ifndef __APP_ZEDBOARD_CRC32
#define __APP_ZEDBOARD_CRC32

#include "stdint.h"

uint32_t crc32(uint32_t crc, const void *buf, uint32_t size);

#endif
