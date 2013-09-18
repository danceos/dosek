#ifndef __OSTREAM_H__
#define __OSTREAM_H__

/** Output stream **/
class O_Stream {
protected:
  virtual void putchar(char c);

  template<typename T> O_Stream& itoa (T c);

public:
  unsigned char base;

  O_Stream() : base(10) {}

  /**
   * \brief Output a single character
   * \param c The character to output
   **/
  O_Stream& operator<< (unsigned char c);

  /**
   * \brief Output a single character
   * \param c The character to output
   **/
  O_Stream& operator<< (char c);

  O_Stream& operator<<(unsigned short ival);
  O_Stream& operator<<(short ival);
  O_Stream& operator<<(unsigned int ival);
  O_Stream& operator<<(int ival);

  /**
   * \brief Display numbers
   * \param ival The number to be displayed
   **/
  O_Stream& operator<<(long ival);

  /**
   * \brief Display numbers
   * \param ival The number to be displayed
   **/
  O_Stream& operator<<(unsigned long ival);

  /**
   * \brief Display a pointer
   * \param ptr The pointer to be displayed
   **/
  O_Stream& operator<<(void* ptr);

  /**
   * \brief Display a zero terminated string
   * \param string The string to be displayed
   **/
  O_Stream& operator<<(char* string);
  O_Stream& operator<<(const char* string);

  /**
   * \brief Call an appropriate manipulatpor function
   **/
  O_Stream& operator<<(O_Stream& (*f) (O_Stream&));
    
};

/* Manipulators */

/**
 * \brief Print a newline
 **/
O_Stream& endl(O_Stream& os);

/**
 * \brief Switch the numbering system to binary
 **/
O_Stream& bin(O_Stream& os);

/**
 * \brief Switch the numbering system to octal
 **/
O_Stream& oct(O_Stream& os);

/**
 * \brief Switch the numbering system to deccimal
 **/
O_Stream& dec(O_Stream& os);

/**
 * \brief Switch the numbering system to hexadecimal
 **/
O_Stream& hex(O_Stream& os);

#endif /* __OSTREAM_H__ */
