/**
 * @file
 * @ingroup osek-v
 * @brief Default output streams
 */
#ifndef __OUTPUT_H__
#define __OUTPUT_H__

#include "arch/generic/ostream.h"

typedef enum class  Color {
	BLACK    = 0,
	RED      = 1,
	GREEN    = 2,
	YELLOW   = 3,
	BLUE     = 4,
	MAGENTA  = 5,
	CYAN     = 6,
	WHITE    = 7,
} Color;

class HTIFOutputStream : public O_Stream<HTIFOutputStream> {
public:
	HTIFOutputStream() {};

	void putchar(char c);

	template<typename T>
		void setcolor(__attribute__((unused)) T fg, __attribute__((unused)) T bg) {};
};

extern HTIFOutputStream  kout;
extern Null_Stream debug;


#endif // __OUTPUT_H__
