#ifndef __MULTIBOOTINFO_H__
#define __MULTIBOOTINFO_H__

#include <stdint.h>

#include "multiboot.h"

struct MemoryInfo {
	uint32_t mem_lower;
	uint32_t mem_upper;


	void setup(multiboot_info_t const * const info)
	{
		mem_lower = info->mem_lower;
		mem_upper = info->mem_upper;
	}



};


#endif //  MULTIBOOTINFO_H

