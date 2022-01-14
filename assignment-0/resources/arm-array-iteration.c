#include <stdio.h>

int main(int argc, char **argv)
{
	char a[256];

	for (int i = 0; i < 256; i++) {
		a[i] = i;
	}

	for (int j = 0; j < 256; j++) {
		printf("a[%i]: 0x%02x\n", j, a[j]);
	}

	return 0;
}

