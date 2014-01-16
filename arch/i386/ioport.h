/**
 * @file
 * @ingroup i386
 * @brief i386 IO port access
 * */

#ifndef __IOPORT_H__
#define __IOPORT_H__

static inline
void outb( unsigned short port, unsigned char val )
{
    asm volatile( "outb %0, %1" :: "a"(val), "Nd"(port) );
}

static inline
void outw( unsigned short port, unsigned short val )
{
    asm volatile( "outw %0, %1" :: "a"(val), "Nd"(port) );
}

static inline
unsigned char inb( unsigned short port )
{
    unsigned char ret;
    asm volatile( "inb %1, %0" : "=a"(ret) : "Nd"(port) );
    return ret;
}

static inline
void io_wait( void )
{
    // port 0x80 is used for 'checkpoints' during POST.
    // the Linux kernel seems to think it is free for use
    asm volatile( "outb %al, $0x80");
}

#endif // __IOPORT_H__
