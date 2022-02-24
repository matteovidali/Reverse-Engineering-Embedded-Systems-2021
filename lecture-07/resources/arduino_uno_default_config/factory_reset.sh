#!/bin/bash

avrdude -v -e -F -V -c usbtiny -p ATMEGA328P -b 115200 -U flash:w:flash.bin:r
avrdude -v -F -V -c usbtiny -p ATMEGA328P -b 115200 -U efuse:w:efuse.bin:r
avrdude -v -F -V -c usbtiny -p ATMEGA328P -b 115200 -U hfuse:w:hfuse.bin:r
avrdude -v -F -V -c usbtiny -p ATMEGA328P -b 115200 -U lfuse:w:lfuse.bin:r

