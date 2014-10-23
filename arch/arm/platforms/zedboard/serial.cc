/**
 * @file
 * @ingroup ARM
 * @brief Serial driver implementation
 */
#include "serial.h"
#include "platform.h"

struct XUARTPS{
    uint32_t control_reg0; /* UART Control Register def=0x128 */
    uint32_t mode_reg0; /* UART Mode Register def=0 */
    uint32_t intrpt_en_reg0; /* Interrupt Enable Register def=0 */
    uint32_t intrpt_dis_reg0; /* Interrupt Disable Register def=0 */
    uint32_t intrpt_mask_reg0; /* Interrupt Mask Register def=0 */
    uint32_t chnl_int_sts_reg0; /* Channel Interrupt Status Register def=x200 */
    uint32_t baud_rate_gen; /* Baud Rate Generator Register def=0x28B */
    uint32_t Rcvr_timeout_reg0; /* Receiver Timeout Register def=0 */
    uint32_t Rcvr_FIFO_trigger_level0; /* Receiver FIFO Trigger Level Register */
    uint32_t Modem_ctrl_reg0; /* Modem Control Register def=0 */
    uint32_t Modem_sts_reg0; /* Modem Status Register */
    uint32_t channel_sts_reg0; /* Channel Status Register def=0 */
    uint32_t tx_rx_fifo; /* Transmit and Receive FIFO def=0 */
    uint32_t baud_rate_divider; /* Baud Rate Divider def=0xf */
    uint32_t Flow_delay_reg0; /* Flow Control Delay Register def=0*/
    uint32_t Tx_FIFO_trigger_level;}; /* Transmitter FIFO Trigger Level Register */

static struct XUARTPS *UART1=(struct XUARTPS*) SERIAL_BASE;

/* Bits defined in the Register Channel_sts_reg0 */
#define UART_STS_TXFULL 1<<4 /* Transmitter FIFO Full continuous status:
        0: Tx FIFO is not full
        1: Tx FIFO is full*/

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

Serial::Serial() {
	// nothing to do
    UART1->control_reg0= XUARTPS_CR_TXEN | XUARTPS_CR_RXEN | XUARTPS_CR_TXRES | XUARTPS_CR_RXRES ;
}

void Serial::putchar(char character) {
    // wait while transmit full
    bool full;
    do {
        full = *(volatile unsigned long*)(SERIAL_BASE + SERIAL_FLAG_REGISTER_OFFSET) & (SERIAL_BUFFER_FULL);
    } while(full);

    // put our character, c, into the serial buffer
    //*(volatile unsigned long*) (SERIAL_BASE + SERIAL_TX_OFFSET) = character;
    UART1->tx_rx_fifo= (unsigned int) character; /* Transmit char */
}

void Serial::puts(const char* data) {
	while(*data) putchar(*data++);
}
