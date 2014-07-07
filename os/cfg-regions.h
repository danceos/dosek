#ifndef __OS_CFG_REGIONS_H
#define __OS_CFG_REGIONS_H

#include "os/util/inline.h"
#include "os/util/assert.h"

namespace os {

	struct CFGRegion {
		forceinline static void check(uint32_t &markers, uint32_t enter_mask,
									  uint32_t check_mask, uint32_t leave_mask) {
			uint32_t tmp = markers;
			// enable bits for regions that we entered
			tmp = tmp | enter_mask;
			// Check that we are in all regions, we should be in
			color_assert( (tmp & check_mask) == check_mask,
						  COLOR_ASSERT_CFG_REGION);
            // kout << tmp << " " << check_mask << endl;
			// Leave all Regions we are not part of
			tmp = tmp & (~leave_mask);
			// writeback
			markers = tmp;
		}
	};

}
#endif
