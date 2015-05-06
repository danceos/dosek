/**
 * @file
 * @ingroup ARM
 * @brief Serial driver implementation
 */
#include "serial.h"
#include "platform.h"

struct XUARTPS{
	// 0x00
    volatile uint32_t control_reg0; /* UART Control Register def=0x128 */
    volatile uint32_t mode_reg0; /* UART Mode Register def=0 */
    volatile uint32_t intrpt_en_reg0; /* Interrupt Enable Register def=0 */
    volatile uint32_t intrpt_dis_reg0; /* Interrupt Disable Register def=0 */
    // 0x10
	volatile uint32_t intrpt_mask_reg0; /* Interrupt Mask Register def=0 */
    volatile uint32_t chnl_int_sts_reg0; /* Channel Interrupt Status Register def=x200 */
    volatile uint32_t baud_rate_gen; /* Baud Rate Generator Register def=0x28B */
    volatile uint32_t Rcvr_timeout_reg0; /* Receiver Timeout Register def=0 */
	// 0x20
    volatile uint32_t Rcvr_FIFO_trigger_level0; /* Receiver FIFO Trigger Level Register */
    volatile uint32_t Modem_ctrl_reg0; /* Modem Control Register def=0 */
    volatile uint32_t Modem_sts_reg0; /* Modem Status Register */
    volatile uint32_t channel_sts_reg0; /* Channel Status Register def=0 */
	// 0x30
    volatile uint32_t tx_rx_fifo; /* Transmit and Receive FIFO def=0 */
    volatile uint32_t baud_rate_divider; /* Baud Rate Divider def=0xf */
    volatile uint32_t Flow_delay_reg0; /* Flow Control Delay Register def=0*/
    volatile uint32_t Tx_FIFO_trigger_level;
}; /* Transmitter FIFO Trigger Level Register */

static struct XUARTPS *UART1 = (struct XUARTPS*) SERIAL_BASE;

/* Bits defined in the Register Channel_sts_reg0 */
#define UART_STS_TXFULL 1<<4 /* Transmitter FIFO Full continuous status:
        0: Tx FIFO is not full
        1: Tx FIFO is full*/

#define UART_STS_TXEMPTY 1<<3

/*Register Control_reg0 BitMask */
#define XUARTPS_CR_STOPBRK (1<<8) /* Stop transmitter break */
#define XUARTPS_CR_STTBRK (1<<7) /* Start transmitter break */
#define XUARTPS_CR_RSTTO (1<<6) /* Restart receiver timeout counter */
#define XUARTPS_CR_TXDIS (1<<5) /* Transmit disable */
#define XUARTPS_CR_TXEN (1<<4) /* Transmit enable */
#define XUARTPS_CR_RXDIS (1<<3) /* Receive disable */
#define XUARTPS_CR_RXEN (1<<2) /* Receive enable */
#define XUARTPS_CR_TXRES (1<<1) /* Software reset for Tx data path */
#define XUARTPS_CR_RXRES (1<<0) /* Software reset for Rx data path */

/*Baudrates assuming input clock speed is 3125000L */
/*Baud_rate_gen_reg0*/
#define XUARTPS_BRGR_CD_115200       62 /*Baud Rate Clock Divisor*/
#define XUARTPS_BRGR_CD_9600       651 /*Baud Rate Clock Divisor*/


/*Register Baud_rate_divider_reg0 Details*/
#define XUARTPS_BDIV_CD_115200       6  /*Baud Rate Clock Divisor*/
#define XUARTPS_BDIV_CD_9600       7  /*Baud Rate Clock Divisor*/


#define XUARTPS_MR_PAR_NONE (1<<5)      /* 1xx: no parity*/

Serial::Serial() {
	while ((( UART1->channel_sts_reg0 ) & UART_STS_TXEMPTY) != UART_STS_TXEMPTY) {};

	/* Disable the transmitter and receiver before writing to the Baud Rate Generator */
	UART1->control_reg0=0;

	// 8N1
	UART1->mode_reg0 = XUARTPS_MR_PAR_NONE;

	/* Set Baudrate to 115,200 Baud */
	UART1->baud_rate_divider = XUARTPS_BDIV_CD_115200;
	UART1->baud_rate_gen = XUARTPS_BRGR_CD_115200;

	/*Enable Rx & Tx*/
	UART1->control_reg0 = XUARTPS_CR_TXEN | XUARTPS_CR_RXEN | XUARTPS_CR_TXRES | XUARTPS_CR_RXRES;
}

void Serial::putchar(char character) {
	/*Make sure that the uart is ready for new char's before continuing*/

	if (character == '\n') {
		while ((( UART1->channel_sts_reg0 ) & UART_STS_TXEMPTY) != UART_STS_TXEMPTY) {};
		UART1->tx_rx_fifo = (unsigned int)'\r'; /* Transmit char */
	}


	while ((( UART1->channel_sts_reg0 ) & UART_STS_TXEMPTY) != UART_STS_TXEMPTY) {};
	/* Loop until end of string */
	UART1->tx_rx_fifo= (unsigned int) character; /* Transmit char */



}

void Serial::puts(const char* data) {
	while(*data) putchar(*data++);
}
