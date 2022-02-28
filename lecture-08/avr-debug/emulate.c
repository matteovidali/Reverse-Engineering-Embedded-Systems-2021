/*
 * Emulate the ATmega328p program with simavr
 *
 * Accepts a single command-line argument specifying the file containing the
 * flash memory contents of the target.
 *
 * Compile with gcc -o emulate emulate.c -lsimavr
 * Depending on the compiled library version, may need to
 * compile with gcc -o emulate emulate.c -lsimavr -lelf
 */

#include <stdio.h>
#include <stdlib.h>

#include <simavr/sim_avr.h>
#include <simavr/avr_uart.h>
#include <simavr/avr_ioport.h>
#include <simavr/sim_gdb.h>

int main(int argc, char **argv)
{
	char * filename;
	FILE * in_fd;
	char mem_byte;

	avr_t * avr;
	int state, ctr;

	// Parse the input arguments
	if (argc != 2) {
		printf("Usage: %s flash_filename\n", argv[0]);
		exit(1);
	}
	filename = argv[1];

	// Set up the AVR target with the details for our project.
	avr = avr_make_mcu_by_name("atmega328p");
	if (!avr) {
		fprintf(stderr, "Error creating avr object.\n");
		exit(1);
	}

	avr_init(avr);
	avr->frequency = 16000000;
	avr->vcc = 5000;
	avr->avcc = 5000;

	// Open the flash memory file for reading
	in_fd = fopen(filename, "r");
	if (!in_fd) {
		fprintf(stderr, "Error opening %s for reading.\n",
		        filename);
		exit(1);
	}

	// Read in the flash contents
	ctr = 0;
	while (ctr < 0x8000) {
		if (fread(&mem_byte, 1, 1, in_fd) != 1) {
			break;
		}
		avr->flash[ctr] = mem_byte;
		ctr++;
	}
	fclose(in_fd);
	printf("Read %i bytes from %s.\n", ctr, filename);

	// Set up the target for debug
	// Note that there appears to be a bug when setting breakpoints in
	// GDB. You'll have to do something like b *(void (*)())0x268
	avr->gdb_port = 1234;
	avr_gdb_init(avr);

	// Run for a fixed number of cycles, or until the processor halts
	avr->state = cpu_Stopped;
	state = avr->state;
	while ((state != cpu_Done) && (state != cpu_Crashed)
	       && (avr->cycle < 10000000)) {
		state = avr_run(avr);
	}
	avr_terminate(avr);

	return 0;
}

