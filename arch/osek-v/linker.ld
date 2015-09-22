/*----------------------------------------------------------------------*/
/* Setup                                                                */
/*----------------------------------------------------------------------*/

/* The OUTPUT_ARCH command specifies the machine architecture where the
   argument is one of the names used in the BFD library. More
   specifically one of the entires in bfd/cpu-mips.c */

OUTPUT_ARCH( "riscv" )

/* The ENTRY command specifies the entry point (ie. first instruction to
   execute). The symbol _start is defined in crt0.S */

ENTRY( _start )


OUTPUT_ARCH( "riscv" )

SECTIONS
{
    .text : {
         . = 0x100;
         KEEP(*(.text.vectors))

         . = 0x200;
         KEEP(*(.text.boot))
         /* constructors */
         PROVIDE(__CTORS_START = .);
         KEEP (*(.ctors*))
         KEEP (*(.init_array*))
         PROVIDE(__CTORS_END = .);

         *(.text)
    }

/* rodata: Read-only data */
  .rodata : 
  {
    *(.rdata)
    *(.rodata)
    *(.rodata.*)
    *(.gnu.linkonce.r.*)
  }

  /*--------------------------------------------------------------------*/
  /* Initialized data segment                                           */
  /*--------------------------------------------------------------------*/

  /* Start of initialized data segment */
  . = ALIGN(16);
   _fdata = .;

  /* data: Writable data */
  .data : 
  {
    *(.data)
    *(.data.*)
    *(.gnu.linkonce.d.*)
  }

  /* End of initialized data segment */
  PROVIDE( edata = . );
  _edata = .;

  /* Have _gp point to middle of sdata/sbss to maximize displacement range */
  . = ALIGN(16);
  _gp = . + 0x800;

  /* Writable small data segment */
  .sdata : 
  {
    *(.sdata)
    *(.sdata.*)
    *(.srodata.*)
    *(.gnu.linkonce.s.*)
  }

  /*--------------------------------------------------------------------*/
  /* Uninitialized data segment                                         */
  /*--------------------------------------------------------------------*/

  /* Start of uninitialized data segment */
  . = ALIGN(8);
  _fbss = .;

  /* Writable uninitialized small data segment */
  .sbss : 
  {
    *(.sbss)
    *(.sbss.*)
    *(.gnu.linkonce.sb.*)
  }

  /* bss: Uninitialized writeable data section */
  . = .;
  _bss_start = .;
  .bss : 
  {
    *(.bss)
    *(.bss.*)
    *(.gnu.linkonce.b.*)
    *(COMMON)
  }

  /* End of uninitialized data segment (used by syscalls.c for heap) */
  PROVIDE( end = . );
  _end = ALIGN(8);
}
