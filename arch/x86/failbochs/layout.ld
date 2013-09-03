ENTRY(_start)

OUTPUT_FORMAT(elf32-i386)

SECTIONS {
   /* The kernel will live at 3GB + 1MB in the virtual
      address space, which will be mapped to 1MB in the
      physical address space. */
   . = 0x100000;

  /* standard segments */
   .ctors : ALIGN(4)
   {
     PROVIDE(__CTORS_START = .);
     KEEP (*(.ctors*))
     KEEP (*(.init_array*))
     PROVIDE(__CTORS_END = .);
   }

   .text : {
      *(".text.startup")
      *(".text")
      *(".rodata*")
   }

   /* Startcode fuer die APs, wird von SMPSystem::copyStartAPtoLowMem() reloziert */
   .setup_ap_seg ALIGN(0x10) :
    {
      PROVIDE(___SETUP_AP_START__ = .);
      KEEP(*(.setup_ap_seg*))
      KEEP(*(.setup_ap*))
      PROVIDE(___SETUP_AP_END__ = .);
    }

   .data ALIGN (0x1000) :  {
       *(".data")
   }

   .bss : {
       _sbss = .;
       *(COMMON)
       *(".bss")
       _ebss = .;
   }

	/*
	 * Get rid of unnecessary GCC bits.
	 */
	/DISCARD/ :
	{
		*(.comment)
		*(.eh_frame)
		*(.note.gnu.build-id)
	}
}
