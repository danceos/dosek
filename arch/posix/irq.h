#ifndef _POSIX_IRQ_H_
#define _POSIX_IRQ_H_

#include <signal.h>

#define SIGMAX 256

namespace arch {
class IRQ {
	bool ast_requested;
	int ast_level;
public:
	typedef void (*irq_handler_t)(int);
    static const int IPISIG = SIGCHLD;

    IRQ();

    void set_handler(int signum, irq_handler_t gate);
    void enable(int signum);
	void disable(int signum);
	void trigger_interrupt(int irq);

    void enable_interrupts();
    void disable_interrupts();

	bool forceinline in_interrupt() { return ast_level > 0;}

	void request_ast() { ast_requested = true; }
private:
    static void guardian(int signum);

    irq_handler_t m_gate[SIGMAX];
};

extern IRQ irq;

};

#endif /* _PIC_H */
