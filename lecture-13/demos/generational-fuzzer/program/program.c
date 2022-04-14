#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv)
{
	uint8_t len;
	size_t bytes_read;
	char data[224];

	puts("Send in the message:");	

	fread(data, 1, 4, stdin);
	if (memcmp(data, "MAGC", 4) != 0) {
		fprintf(stderr, "Incorrect magic number\n");
		exit(1);
	}

	// Read in the length byte
	fread(&len, 1, 1, stdin);

	// Now read that many bytes into data
	bytes_read = fread(data, 1, (size_t)len, stdin);

	puts("You sent:");
	fwrite(data, 1, bytes_read, stdout);
	puts("");

	return 0;
}

