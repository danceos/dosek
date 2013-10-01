#include "ostream.h"

O_Stream& O_Stream::operator << (char value) {
    putchar(value);

    return *this;
}

O_Stream& O_Stream::operator << (unsigned char value) {
    putchar(value);

    return *this;
}

O_Stream& O_Stream::operator << (char* value) {
    while (*value != 0)
    	putchar(*value++);

    return *this;
}

O_Stream& O_Stream::operator << (const char* value) {
    *this << const_cast<char*> (value);

    return *this;
}

template<typename T> O_Stream& O_Stream::itoa (T value) {
    char buf[sizeof(T)*8]; // worst case: unsigned -> base 2

    char *ptr = buf;

    if (base < 2 || base > 16) return *this;

    #pragma clang diagnostic push
    #pragma clang diagnostic ignored "-Wtautological-compare"
    if (value < 0) putchar('-');
    #pragma clang diagnostic pop

    do {
        T tmp_value = value;
        value /= base;
        *ptr++ = "fedcba9876543210123456789abcdef" [15 + (tmp_value - value * base)];
    } while ( value );
    ptr--;

    while(ptr >= buf) putchar(*ptr--);

    return *this;
}


O_Stream& O_Stream::operator << (unsigned short value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (short value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (unsigned int value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (int value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (unsigned long value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (long value) {
    return itoa(value);
}

O_Stream& O_Stream::operator << (void* value) {
    unsigned int oldbase = base;

    base = 16;
    *this << (unsigned long) value;
    base = oldbase;

    return *this;
}

O_Stream& O_Stream::operator << (O_Stream& (*stream) (O_Stream&)) {
    return (*stream)(*this);
}

O_Stream& endl(O_Stream &out) {
    out << '\n';
    return out;
}

O_Stream& bin(O_Stream &out) {
    out.base = 2;
    return out;
}

O_Stream& oct(O_Stream &out) {
    out.base = 8;
    return out;
}

O_Stream& dec(O_Stream &out) {
    out.base = 10;
    return out;
}

O_Stream& hex(O_Stream &out) {
    out.base = 16;
    return out;
}
