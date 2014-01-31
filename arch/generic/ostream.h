/**
 * \file
 *
 * \ingroup generic
 *
 * \brief C++ style output stream.
 */

#ifndef __OSTREAM_H__
#define __OSTREAM_H__

/**
 * @brief Generic output stream
 */
template<typename T>
class O_Stream {
	template<typename N> O_Stream& itoa (N c);

	void putchar(char c) {
		static_cast<T*>(this)->putchar(c);
	}

public:
	unsigned char base;

	O_Stream() : base(10) {}

	/**
	 * \brief Output a single character
	 * \param c The character to output
	 **/
	O_Stream<T>& operator<< (unsigned char c);

	/**
	 * \brief Output a single character
	 * \param c The character to output
	 **/
	O_Stream<T>& operator<< (char c);

	/**
	 * \name Display numbers
	 * \param ival The number to be displayed
	 **/
	//@{
	O_Stream<T>& operator<<(unsigned short ival);
	O_Stream<T>& operator<<(short ival);
	O_Stream<T>& operator<<(unsigned int ival);
	O_Stream<T>& operator<<(int ival);
	O_Stream<T>& operator<<(long ival);
	O_Stream<T>& operator<<(unsigned long ival);
	// @}

	/**
	 * \brief Display a pointer
	 * \param ptr The pointer to be displayed
	 **/
	O_Stream<T>& operator<<(void* ptr);

	/**
	 * \name Display a zero terminated string
	 * \param string The string to be displayed
	 **/
	//@{
	O_Stream<T>& operator<<(char* string);
	O_Stream<T>& operator<<(const char* string);
	// @}

	/**
	 * \brief Call an appropriate manipulatpor function
	 **/
	O_Stream<T>& operator<<(O_Stream<T>& (*f) (O_Stream<T>&));
 };


/**
 * @name Manipulators
 * @{
 */

/**
 * \brief Print a newline
 **/
template<typename T>
O_Stream<T>& endl(O_Stream<T>& os);

/**
 * \brief Switch the numbering system to binary
 **/
template<typename T>
O_Stream<T>& bin(O_Stream<T>& os);

/**
 * \brief Switch the numbering system to octal
 **/
template<typename T>
O_Stream<T>& oct(O_Stream<T>& os);

/**
 * \brief Switch the numbering system to deccimal
 **/
template<typename T>
O_Stream<T>& dec(O_Stream<T>& os);

/**
 * \brief Switch the numbering system to hexadecimal
 **/
template<typename T>
O_Stream<T>& hex(O_Stream<T>& os);

/**@}*/



/** \brief Color */
typedef enum class Color {
	BLACK   = 0,
	BLUE    = 1,
	GREEN   = 2,
	CYAN    = 3,
	RED     = 4,
	MAGENTA = 5,
	YELLOW  = 6,
	WHITE  = 15,
} Color;



/**
 * @brief No-op output stream
 */
class Null_Stream : public O_Stream<Null_Stream> {
public:
	void putchar(__attribute__((unused)) char c) {};

	void setcolor(__attribute__((unused)) Color fg, __attribute__((unused)) Color bg) {};

	template<typename T=Null_Stream>
	Null_Stream& operator<<(__attribute__((unused)) O_Stream<T>& (*f) (O_Stream<T>&)) {
		return *this;
	};

	template<typename T>
	Null_Stream& operator<< (T) { return *this; };
};



template<typename T>
O_Stream<T>& O_Stream<T>::operator << (char value) {
	putchar(value);

	return *this;
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (unsigned char value) {
	putchar(value);

	return *this;
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (char* value) {
	while (*value != 0)
		putchar(*value++);

	return *this;
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (const char* value) {
	*this << const_cast<char*> (value);

	return *this;
}

template<typename T>
template<typename N> O_Stream<T>& O_Stream<T>::itoa (N value) {
	char buf[sizeof(N)*8]; // worst case: unsigned -> base 2

	char *ptr = buf;

	if (base < 2 || base > 16) return *this;

	#pragma clang diagnostic push
	#pragma clang diagnostic ignored "-Wtautological-compare"
	if (value < 0) putchar('-');
	#pragma clang diagnostic pop

	do {
		N tmp_value = value;
		value /= base;
		*ptr++ = "fedcba9876543210123456789abcdef" [15 + (tmp_value - value * base)];
	} while ( value );
	ptr--;

	while(ptr >= buf) putchar(*ptr--);

	return *this;
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (unsigned short value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (short value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (unsigned int value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (int value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (unsigned long value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (long value) {
	return itoa(value);
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (void* value) {
	unsigned int oldbase = base;

	base = 16;
	*this << (unsigned long) value;
	base = oldbase;

	return *this;
}

template<typename T>
O_Stream<T>& O_Stream<T>::operator << (O_Stream<T>& (*stream) (O_Stream<T>&)) {
	return (*stream)(*this);
}

template<typename T>
O_Stream<T>& endl(O_Stream<T> &out) {
	out << '\n';
	return out;
}

template<typename T>
O_Stream<T>& bin(O_Stream<T> &out) {
	out.base = 2;
	return out;
}

template<typename T>
O_Stream<T>& oct(O_Stream<T> &out) {
	out.base = 8;
	return out;
}

template<typename T>
O_Stream<T>& dec(O_Stream<T> &out) {
	out.base = 10;
	return out;
}

template<typename T>
O_Stream<T>& hex(O_Stream<T> &out) {
	out.base = 16;
	return out;
}

#endif /* __OSTREAM_H__ */
