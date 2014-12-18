// @formatter:off
/**(c)

  Copyright (C) 2006-2013 Christian Wawersich, Michael Stilkerich,
                          Christoph Erhardt

  This file is part of the KESO Java Runtime Environment.

  KESO is free software: you can redistribute it and/or modify it under the
  terms of the Lesser GNU General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option)
  any later version.

  KESO is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
  more details. You should have received a copy of the GNU Lesser General
  Public License along with KESO. If not, see <http://www.gnu.org/licenses/>.

  Please contact keso@cs.fau.de for more info.

  (c)**/
// @formatter:on
package keso.core.io;

import keso.core.*;

/**
 *  PacketStream sends packets with unique ID's and can receive
 *  packets within a range of ID's. It's implementation depends upon
 *  the underlying network layer e.g. device driver. It is used by the RPC layer.
 *
 */
public interface PacketStream {

    public static final int NO_TIMEOUT = 0;


    /**
     *
     * NOTE: The constructor of an implementing class must have a special
     * signature:
     *
     * public <Implementation>(<DriverInterface> port, int rxId, int rxMask, int bufferMask, byte idBits, byte numRxBuffers);
     *
     * @param port The driver to use for communication. It must be setup properly before calling this constructor.
     * @param rxId The receive identifier.
     * @param rxMask The receive mask. This mask determines wether a packet is accepted or not. Any packet
     * that matches (rxId & rxMask) == (packetId & rxMask) will be accepted. One could also say that a one
     * in the mask means this bit must match between rxId and packetId and a zero means this bit is a don't care bit.
     * @param bufferMask The buffer mask. This mask determines which receive buffer will be used when a packet is received. The buffer which id matches (bufferId & bufferMask) == (packetId & bufferMask) will be used.
     * @param idBits Number of bits reserved for the id.
     * @param numRxBuffers Maximum number of receive buffers.
     *
     */


    /**
     * Allocates a memory block for receiving packets from ID. Size is the
     * maximum expected number of data bytes in a packet.
     *
     *
     * @return true if the buffer was successfully allocated else false.
     */
    public boolean allocReceiveBuffer(int id, short size, int timeout);

    /**
     * Allocate a memory block for transmitting packets.
     * @return A memory object that can be used as transmit buffer.
     */
    public Memory allocTransmitBuffer(short size, int timeout);



    /**
     * Returns the data of the next packet. The corresponding receive buffer
     * will be locked upon read() and must be released by releaseReceiveBuffer()
     * after use.
     *
     * @param usTimeout Timeout in micro seconds. If an Timeout occurs null is returned.
     * The value NO_TIMEOUT indicates that no timeout shall be used. Thus this method might probably NEVER return!
     * @return The data of the next packet. A null value indicates that an error occured (e.g. timeout)
     */
    public Memory read(int usTimeout);


    /**
     * Returns the ID of the packet. Valid between read() and releaseReceiveBuffer().
     * require read(), !releaseReceiveBuffer()
     *
     */
    public int getPacketID();

    /**
     * Returns the length of the packet. Valid between read() and releaseReceiveBuffer().
     * require read(), !releaseReceiveBuffer()
     *
     */
    public short getPacketLength();

    /**
     * Unlocks the receive buffer that was locked when calling read().
     * require read()
     */
    public void releaseReceiveBuffer();


    /**
     * Write a packet to the output stream.
     * require releaseReceiveBuffer()
     * @param id         The ID of the packet
     * @param length     The length of the data.
     * @param usTimeout  Timeout in micro seconds.
		 *                   The value NO_TIMEOUT indicates that no timeout shall be used. Thus this method might NEVER return!
     * @return true if the operation was successful.
     */
    public boolean write(int id, short length, int usTimeout);

}
