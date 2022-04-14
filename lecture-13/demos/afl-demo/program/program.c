#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
	uint8_t len, special_byte;
	size_t bytes_read;
	char data[256];

	puts("Send in the message:");	

	fread(data, 1, 4, stdin);
	if (data[0] != 'M' || data[1] != 'A' || data[2] != 'G' || data[3] != 'C') {
		fprintf(stderr, "Incorrect magic number\n");
		exit(1);
	}

	// Read in the length byte
	fread(&len, 1, 1, stdin);
	// Read in the special byte
	fread(&special_byte, 1, 1, stdin);

	// Now read that many bytes into data
	bytes_read = fread(data, 1, (size_t)len, stdin);

	if (special_byte == 0xc8) {
		// Double the input
		memcpy(data + bytes_read, data, bytes_read);
		bytes_read *= 2;
	}

	puts("You sent:");
	fwrite(data, 1, bytes_read, stdout);
	puts("");

	return 0;
}

