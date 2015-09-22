#ifndef __OSEKV_FRONTEND_H
#define __OSEKV_FRONTEND_H

# define TOHOST_CMD(dev, cmd, payload)									\
	(((uint64_t)(dev) << 56) | ((uint64_t)(cmd) << 48) | (uint64_t)(payload))
#define FROMHOST_DEV(fromhost_value) ((uint64_t)(fromhost_value) >> 56)
#define FROMHOST_CMD(fromhost_value) ((uint64_t)(fromhost_value) << 8 >> 56)
#define FROMHOST_DATA(fromhost_value) ((uint64_t)(fromhost_value) << 16 >> 16)

#endif
