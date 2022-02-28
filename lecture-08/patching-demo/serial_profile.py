#!/usr/bin/env python3

import serial
import time
import argparse

PASSWORD=b"abcdef"

def serial_init(dev, baud, timeout):
    ser = serial.Serial(dev, baud, timeout=timeout)
    ser.reset_input_buffer()
    return ser

def profile_serial(dev="/dev/ttyACM0", baud=38400, timeout=0.1):
    ser = serial_init(dev, baud, timeout)
    t_start = time.time()
    attempts = 0
    print("Beginning profiling loop.")
    print("Press Ctrl-C to terminate and print statistics.")
    try:
        while True:
            # Attempt to read the prompt
            prompt = ser.readline()
            if prompt != b'' and prompt[0] != ord('P'):
                # We seem to be out of phase, so try again
                continue
            ser.write(bytes(PASSWORD) + b'\r\n')
            response = ser.readline()
            if (response[0] != ord('S')) and (response[0] != ord('I')):
                # Doesn't seem to be either the "SUCCESS" or
                # "Incorrect password" message
                raise ValueError(f"Unexpected response: {response}")

            attempts += 1

    except KeyboardInterrupt:
        pass

    delta_t = time.time() - t_start
    print("==============================================")
    print(f"{attempts} attempts in {delta_t} seconds")
    print(f"{attempts/delta_t} attempts/s")
    print(f"{delta_t*1000/attempts} ms/attempt")
    ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Brute force password over serial')
    parser.add_argument('--device', default='/dev/ttyACM0', type=str,
            help='Serial device name')
    parser.add_argument('--timeout', default=0.1, type=float,
            help='Serial read/write timeout')
    parser.add_argument('--baud', default=38400, type=int,
            help='Serial baud rate')
    args = parser.parse_args()
    profile_serial(dev=args.device, baud=args.baud, timeout=args.timeout)

