#!/usr/bin/env python3

""" Implements a client for the Arduino Uno bootloader

The command sequences below were derived from reverse-engineering the
bootloader contained in a factory-fresh Arduino Uno's program memory. The boot
loader code begins at 16-bit code address 0x3f00 in the program memory, with
the reset address set by the BOOTRST, BOOTSZ0, and BOOTSZ1 bits of the fuse
high byte (hfuse).

The bootloader is able to read and write program memory. It does not access
fuses and can not issue a chip erase command. Only individual pages are erased
within the bootloader code immediately before page programming.

The watchdog timer ensures that the main application's bootloader will be
executed if there is no activity on the UART for approximately one second.

The ATmega16U2, with serves as the USB-UART bridge on the Arduino Uno, will
sometimes issue device resets to the ATMEGA328P when the UART connection is
initialized. Its behavior is not consistent, and I haven't examined its code to
understand the logic. In the event that a device reset is not issued, the
'Reset' button can be used to issue the reset manually after starting this
script.

Example usages of this script are:

View help:
    ./arduino_uno_bootloader_client.py -h

Read 0x400 bytes of program memory and dump results:
    ./arduino_uno_bootloader_client.py -r 0x400 -p

Read all program memory to a file named 'filename':
    ./arduino_uno_bootloader_client.py -r -o filename

Erase the application area and program with contents of filename:
    ./arduino_uno_bootloader_client.py -e -w filename

All commands can be issued with the -v flag to enable verbose debug output.
"""

import serial
import time
import argparse

# Print verbose debug messages
DEBUG = False

# ANSI escape sequences
RED = "\x1B[91m"
GREEN = "\x1B[92m"
YELLOW = "\x1B[93m"
BLUE = "\x1B[94m"
RESET = "\x1B[0m"

def hexdump(bs, width=0x10, offset=0):
    """ Print a hexdump of provided bytestring

    Parameters
    ----------
    bs : array_like or bytestring
        Contains data to print
    width : int, optional
        Number of bytes to print per line (defaults to 0x10)
    offset : int, optional
        Offset to apply to printed addresses (defaults to 0)

    Returns
    -------
    None
    """

    # Full lines
    for i in range(len(bs)//width):
        print(f"{i*width + offset:08x}  ",
                "%02x "*width % tuple(bs[i*width:(i+1)*width]), end='', sep='')
        print(" ", end='', sep='')
        for j in range(width):
            c = bs[i*width + j]
            if c < 0x20 or c > 0x7e:
                print(".", end='', sep='')
            else:
                print(chr(c), end='', sep='')
        print("")
    # Stragglers
    s = len(bs) % width
    if s == 0:
        return
    n = len(bs) - s
    print(f"{n + offset:08x}  ", "%02x "*s % bs[n:], end='', sep='')
    print("   "*(width - s), end='', sep='')
    print(" ", end='', sep='')
    for i in range(s):
        c = bs[n + i]
        if c < 0x20 or c > 0x7e:
            print(".", end='', sep='')
        else:
            print(chr(c), end='', sep='')
    print("")
    return

def ser_init(device, baud=115200, timeout=0.1):
    """ Initialize a serial device
    
    Parameters
    ----------
    device : string
        Device to intialize (for example "/dev/ttyUSB0")
    baud : int, optional
        Baudrate (defaults to 115200)
    timeout: float, optional
        Read/write timeout (defaults to 0.1 seconds)

    Returns
    -------
    serial.Serial object
    """

    return serial.Serial(port=device, baudrate=baud, timeout=timeout)

def sync(ser, with_delay=False):
    """ Perform Arduino bootloader sync sequence

    There is a frequent pattern in the bootloader state machine that this
    subroutine implements:

    Client sends to bootloader: 0x20
    Bootloader sends to client: 0x14
    Bootloader sends to client: 0x10
    State machine resets

    For some commands the 0x20/0x14 subsequences are separate from the
    0x10/reset subsequences. For those commands, these sync steps are
    implemented inline.

    Parameters
    ----------
    ser : serial.Serial object

    Returns
    -------
    None
    """

    while True:
        ser.write(b"\x20")
        if DEBUG:
            print("Sent 0x20")
        # Delay seems to help avoid sync issues after reset
        if with_delay:
            time.sleep(0.1)
        if ser.read(1) == b"\x14":
            if DEBUG:
                print("Received 0x14")
            break

    while True:
        if ser.read(1) != b"\x10":
            if DEBUG:
                print("Received 0x10")
            break

def enable_watchdog_reset(ser):
    """ Watchdog system reset enable

    The 'Q' command in the Arduino bootloader performs the 'Watchdog system
    reset enable' action. Typically this command will not need to be executed,
    because the Watchdog action will already be set to system reset.

    Parameters
    ----------
    ser : serial.Serial object

    Returns
    -------
    None
    """

    ser.write(b"Q")
    if DEBUG:
        print("Sent command byte Q")
    sync(ser)

def write_program_memory_address(ser, address):
    """ Write program memory address

    The 'U' command in the Arduino bootloader sets the internal program memory
    address variable. This address is used as the address for the read program
    memory and write program memory commands.

    Note that the address here is a 16-bit code address. The bootloader
    multiplies this value by two to generate the associated byte address.

    The bootloader does not require that this address be page-aligned, but for
    writing program memory it probably should be since the bootloader erases
    pages before writing.

    Parameters
    ----------
    ser : serial.Serial object
    address : int

    Returns
    -------
    None
    """

    ser.write(b"U")
    if DEBUG:
        print("Sent command byte U")
    # Send address low byte
    ser.write(bytes([address & 0xff]))
    if DEBUG:
        print(f"Sent low address byte 0x{address & 0xff:02x}")
    # Send address high byte
    ser.write(bytes([(address >> 8) & 0xff]))
    if DEBUG:
        print(f"Sent high address byte 0x{(address >> 8) & 0xff:02x}")
    sync(ser)

def read_program_memory_single_cmd(ser, n):
    """ Send a single 'read program memory' command to bootloader

    The 't' command in the Arduino bootloader reads a single contiguous chunk
    of program memory. The start address is determined by the internal program
    memory address variable set previously set with the 'U' command.

    Parameters
    ----------
    ser : serial.Serial object
    n : int
        Number of bytes to read. Must be <= 255 to be encoded in one byte.

    Returns
    -------
    bytestring containing memory contents
    """

    if n > 255 or n < 1:
        raise ValueError("Invalid number of bytes for reading")
    # Second command byte
    ser.write(b"t")
    if DEBUG:
        print("Sent command byte t")
    # Next byte is discarded
    ser.write(b"\xff")
    if DEBUG:
        print("Sent discarded byte 0xff")
    # Send number of bytes to read
    ser.write(bytes([n]))
    if DEBUG:
        print(f"Sent data length 0x{n:02x}")
    # Next byte is discarded
    ser.write(b"\xff")
    if DEBUG:
        print("Sent discarded byte 0xff")
    # 0x20/0x14 operation is here for some reason
    while True:
        ser.write(b"\x20")
        if DEBUG:
            print("Sent 0x20")
        if ser.read(1) == b"\x14":
            if DEBUG:
                print("Received 0x14")
            break
    # Now the bootloader sends the requested number of bytes out the UART
    recv = ser.read(n)
    if len(recv) != n:
        raise ValueError("Missed data in 't' command")

    if DEBUG:
        print(f"Received data: {recv.hex()}")

    # Boot loader sends 0x10 before state machine reset
    while True:
        if ser.read(1) != b"\x10":
            if DEBUG:
                print("Received 0x10")
            break

    return recv

def read_program_memory(ser, size=0x8000, pagesize=0x80, outputfile=None):
    """ Read program memory

    Read program memory starting at address 0, up to specified size. For
    similarity to the write commands we will read in pagesize chunks, although
    the read command can read up to 255 bytes per command.

    Parameters
    ----------
    ser : serial.Serial object
    size : int, optional
        Number of bytes to read. Defaults to 0x8000.
    pagesize : int, optional
        Number of bytes to read per transaction. Defaults to 0x80.
    outputfile : string, optional
        Filename of location to save results

    Returns
    -------
    bytestring containing read program memory contents
    """

    mem = b""
    # Read whole pages
    for i in range(size//pagesize):
        # Note that we're sending a *code* address.
        write_program_memory_address(ser, i*pagesize//2)
        mem += read_program_memory_single_cmd(ser, pagesize)
    # Read any remaining bytes
    if size % pagesize != 0:
        write_program_memory_address(ser, (size//pagesize)*pagesize//2)
        mem += read_program_memory_single_cmd(ser, size % pagesize)

    if outputfile:
        f = open(outputfile, "wb")
        f.write(mem)
        f.close()

    return mem

def write_program_memory_single_cmd(ser, data, pagesize=0x80):
    """ Send a single 'write program memory' command to bootloader

    The 'd' command in the Arduino bootloader writes a single page of program
    memory. The start address is determined by the internal program memory
    address variable set previously set with the 'U' command. The bootloader
    erases each page of program memory individually before writing.

    Parameters
    ----------
    ser : serial.Serial object
    data : bytestring
        Data to write in program memory. Must be of length pagesize or less.

    Returns
    -------
    None
    """

    # Can send up to 255 bytes, but only pagesize will be written. So makes
    # sense to limit ourselves to that number.
    if pagesize > 255:
        raise ValueError("No way to encode pagesize in a single byte...")
    if len(data) > pagesize or len(data) < 1:
        raise ValueError("Invalid number of bytes for writing")
    # Second command byte
    ser.write(b"d")
    if DEBUG:
        print("Sent command byte d")
    # Next byte is discarded
    ser.write(b"\xff")
    if DEBUG:
        print("Sent discarded byte 0xff")
    # Send number of bytes that we plan to send
    ser.write(bytes([len(data)]))
    if DEBUG:
        print(f"Sent data len 0x{len(data):02x}")
    # Next byte is discarded
    ser.write(b"\xff")
    if DEBUG:
        print("Sent discarded byte 0xff")
    # Send all of the data
    ser.write(data)
    if DEBUG:
        print(f"Sent data: {data.hex()}")
    # Sync when operation is completed
    sync(ser)

def write_program_memory(ser, data, offset=0,  pagesize=0x80):
    """ Write program memory

    Write program memory starting at address 'offset'

    Parameters
    ----------
    ser : serial.Serial object
    data : bytestring
        Data to be written
    offset : int, optional
        Code address to start writing data. This should be pagesize aligned.
    pagesize: int, optional
        Size of a page in bytes. Defaults to 0x80.

    Returns
    -------
    None
    """
    if offset % pagesize != 0:
        raise ValueError("Offset must be n increment of pagesize")
    # Write whole pages
    for i in range(len(data)//pagesize):
        # Note that we're sending a *code* address.
        write_program_memory_address(ser, (offset + i*pagesize)//2)
        write_program_memory_single_cmd(ser, data[i*pagesize:(i+1)*pagesize],
                pagesize)
    if len(data) % pagesize != 0:
        # Write any remaining bytes
        write_program_memory_address(ser, (offset + (len(data)//pagesize)*pagesize)//2)
        write_program_memory_single_cmd(ser, data[len(data) - (len(data) % pagesize):],
                pagesize)

def erase_application_memory(ser, application_memsize=0x7e00):
    """ Erase application memory

    Program application memory space to 0xff. (Pages will be erased, defaulting
    to 0xff state.) Note that this does *not* need to be performed before
    writing the memory, because the bootloader will erase each page as needed.
    But if you plan to program a smaller program than is programmed in the
    device, this can make things look a little bit cleaner.

    Parameters
    ----------
    ser : serial.Serial object
    application_memsize : int, optional
        Size of application space in memory in bytes. Defaults to 0x7e00.

    Returns
    -------
    None
    """

    write_program_memory(ser, b"\xff"*application_memsize)

def read_device_type(ser):
    """ Send a single 'read device type' command to bootloader

    The 'u' command in the Arduino bootloader reads back three device type
    bytes. The byte values will probably be programmed to match the 'signature
    bytes' accessible in serial/parallel programming modes, though in this case
    they are just coded into the bootloader.

    Parameters
    ----------
    ser : serial.Serial object

    Returns
    -------
    Bytestring of length 3
    """

    # Send command byte
    ser.write(b"u")
    if DEBUG:
        print("Sent u")
    # 0x20/0x14 operation is here for some reason
    while True:
        ser.write(b"\x20")
        if DEBUG:
            print("Sent 0x20")
        if ser.read(1) == b"\x14":
            if DEBUG:
                print("Received 0x14")
            break
    # Now the bootloader sends three bytes out the UART
    recv = ser.read(3)
    if len(recv) != 3:
        raise ValueError("Missed data in 't' command")

    if DEBUG:
        print(f"Received: {recv.hex()}")

    # Boot loader sends 0x10 before state machine reset
    while True:
        if ser.read(1) != b"\x10":
            if DEBUG:
                print("Received 0x10")
            break

    return recv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Interact with Arduino Uno bootloader')
    parser.add_argument("-v", "--verbose", dest='verbose', action='store_true',
            help="Print verbose debug messages")
    parser.add_argument("-d", "--device", type=str, default="/dev/ttyACM0",
            help="Set serial device name")
    parser.add_argument("-b", "--baud", type=int, default=115200,
            help="Set serial baud rate")
    parser.add_argument("-e", "--erase", dest='erase', action='store_true',
            help="Erase application program memory")
    parser.add_argument("-w", "--write", dest='input_filename', type=str,
            default=None, help="Write program memory using contents from file")
    parser.add_argument("-r", "--read", dest='read_size', nargs='?', type=str,
            default='', const="0x8000", help="Read program memory")
    parser.add_argument("-p", "--print", dest='print', action='store_true',
            help="Print dump of program memory contents")
    parser.add_argument("-o", "--output", dest='output_filename', type=str,
            default=None, help="Save program memory contents to file")
    
    args = parser.parse_args()
    ser = ser_init(args.device, baud=args.baud)
    if args.verbose:
        DEBUG = True
    print(BLUE + "[+] Waiting for device reset" + RESET)
    print(YELLOW + "Reset the ATMega328p now." + RESET)
    sync(ser, with_delay=True)
    print(BLUE + "[+] Verifying device type..." + RESET)
    if read_device_type(ser) != b"\x1e\x95\x0f":
        raise ValueError("Read invalid device type for Arduino Uno")
    if args.erase:
        print(BLUE + "[+] Erasing program memory..." + RESET)
        erase_application_memory(ser)
    if args.input_filename:
        print(BLUE + "[+] Writing program memory..." + RESET)
        f = open(args.input_filename, "rb")
        data = f.read()
        f.close()
        write_program_memory(ser, data)
    if args.read_size:
        print(BLUE + "[+] Reading program memory..." + RESET)
        mem = read_program_memory(ser, size=int(args.read_size, 0),
                outputfile=args.output_filename)
        if args.print:
            hexdump(mem)

    ser.close()

