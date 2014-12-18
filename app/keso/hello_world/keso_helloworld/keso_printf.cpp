/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/********************************************************
 * Generated from c-templates/CodeTemplate/kesoPrintf.c *
 ********************************************************/
#include "keso_printf.h"
/* keso_parity.h is needed for NATIVE_ADDR */
#include "keso_parity.h"

#include <stdarg.h>
#include <string.h>

#ifndef KESO_NO_WRITE

#define MAXBUF (sizeof(long int) * 8)	/* enough for binary */
#define Ctod(c) ((c) - '0')

int __keso_printc(jchar);

static int isdigit(int d) {
	return ((d) >= '0' && (d) <= '9');
}

#define PUT(c) {\
	if (putchar((c))) {\
		++o;\
	} else {\
		return o;\
	}\
}

/**
 * print string formatted using output function putchar(), return number of
 * characters printed. Printing ends if either putchar() returns 0 or if all
 * characters have been printed.
 */
static int __vprintf(int (*putchar)(jchar), const char *fmt, va_list args) {
	int length;
	int n;
	int o = 0; /* written chars */
	int prec;
	int ladjust;
	char padc;
	int plus_sign;
	int sign_char;
	int altfmt;
	int base;
	char c;
	unsigned long u;

	while (*fmt != '\0') {
		if (*fmt != '%') {
			PUT( *fmt++);
			continue;
		}

		fmt++;

		length = 0;
		prec = -1;
		ladjust = 0;
		padc = ' ';
		plus_sign = 0;
		sign_char = 0;
		altfmt = 0;

		if(*fmt == '0') {
			padc = '0';
			++fmt;
		}
		if (isdigit(*fmt)) {
			while (isdigit(*fmt)) {
				length = 10 * length + Ctod(*fmt++);
			}
		} else if (*fmt == '*') {
			length = va_arg(args, int);
			fmt++;
			if (length < 0) {
				ladjust = !ladjust;
				length = -length;
			}
		}

		if (*fmt == '.') {
			fmt++;
			if (isdigit(*fmt)) {
				prec = 0;
				while (isdigit(*fmt))
					prec = 10 * prec + Ctod(*fmt++);
			} else if (*fmt == '*') {
				prec = va_arg(args, int);
				fmt++;
			}
		}

		if (*fmt == 'l') {
			fmt++;	/* need it if sizeof(int) < sizeof(long) */
		}

		switch (*fmt) {
			case 'c':
				c = va_arg(args, int);
				PUT( c);
				break;

			case 's':
				{
					register char *p;
					register char *p2;

					if (prec == -1)
						prec = (int) ((unsigned int) ~1>>1); /* MAXINT */

					p = va_arg(args, char *);

					if (p == (char *) 0)
						p = "";

					if (length > 0 && !ladjust) {
						n = 0;
						p2 = p;

						for (; *p != '\0' && n < prec; p++)
							n++;

						p = p2;

						while (n < length) {
							PUT( ' ');
							n++;
						}
					}

					n = 0;

					while (*p != '\0') {
						if (++n > prec)
							break;

						PUT( *p++);
					}

					if (n < length && ladjust) {
						while (n < length) {
							PUT( ' ');
							n++;
						}
					}

					break;
				}

			case 'o':
			case 'O':
				base = 8;
				goto print_unsigned;

			case 'd':
			case 'i':
			case 'D':
				base = 10;
				goto print_signed;

			case 'u':
			case 'U':
				base = 10;
				goto print_unsigned;

			case 'p':
				padc = '0';
				length = 8;
				/*
				 * We do this instead of just setting altfmt to TRUE
				 * because we want 0 to have a 0x in front, and we want
				 * eight digits after the 0x -- not just 6.
				 */
				PUT( '0');
				PUT( 'x');
			case 'x':
			case 'X':
				base = 16;
				goto print_unsigned;

			case 'z':
			case 'Z':
				base = 16;
				goto print_signed;

print_signed:
				n = va_arg(args, long);
				if (n >= 0) {
					u = n;
					sign_char = plus_sign;
				} else {
					u = -n;
					sign_char = '-';
				}
				goto print_num;

print_unsigned:
				u = va_arg(args, unsigned long);
				goto print_num;

print_num:
				{
					char buf[MAXBUF];	/* build number here */
					register char *p = &buf[MAXBUF - 1];
					static char digits[] = "0123456789abcdef";
					char *prefix = 0;

					if (base == 16) {	/* special case handling MG */
						do {
							*p-- = digits[u & 0xf];
							u = u >> 4;
						} while (u != 0);

						while (++p != &buf[MAXBUF])
							PUT( *p);

					} else {	/* general case */

						if (u != 0 && altfmt) {
							if (base == 8)
								prefix = "0";
							else if (base == 16)
								prefix = "0x";
						}

						do {
							*p-- = digits[u % base];
							u /= base;
							prec--;
						} while (u != 0);

						length -= (&buf[MAXBUF - 1] - p);
						if (sign_char)
							length--;
						if (prefix)
							length -= strlen(prefix);

						if (prec > 0)
							length -= prec;
						if (padc == ' ' && !ladjust) {
							/* blank padding goes before prefix */
							while (--length >= 0) {
								PUT( ' ');
							}
						}
						if (sign_char) {
							PUT( sign_char);
						}
						if (prefix) {
							while (*prefix) {
								PUT( *prefix++);
							}
						}
						while (--prec >= 0) {
							PUT( '0');
						}
						if (padc == '0') {
							/* zero padding goes after sign and prefix */
							while (--length >= 0) {
								PUT( '0');
							}
						}
						while (++p != &buf[MAXBUF]) {
							PUT( *p);
						}

						if (ladjust) {
							while (--length >= 0) {
								PUT( ' ');
							}
						}
					}
					break;
				}

			case '\0':
				fmt--;
				break;

			default:
				PUT( *fmt);
		}
		fmt++;
	}

	putchar('\0');
	return o;
}

int keso_printf(const char *fmt, ...) {
	va_list args;
	int res;

	va_start(args, fmt);
	res = __vprintf(__keso_printc, fmt, args);
	va_end(args);

	return res;
}

unsigned int keso_write(const jchar *buf, unsigned int count) {
	unsigned int i;
	buf = NATIVE_ADDR(buf);
	for (i = 0; i < count; i++) {
		if (0 == __keso_printc(buf[i])) {
			return i;
		}
	}
	__keso_printc('\0');
	return i;
}

#endif /* defined(KESO_NO_WRITE) */
