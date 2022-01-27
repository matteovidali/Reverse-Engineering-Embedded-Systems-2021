#include <stdlib.h>
#include <stdio.h>
#include "demo.h"

int add_two_numbers(int a, int b)
{
	return a + b;
}

int main(int argc, char **argv)
{
	int a, b;

	if (argc != 3) {
		fprintf(stderr, "Usage: %s num1 num2\n", argv[0]);
		exit(1);
	}

	a = atoi(argv[1]);
	b = atoi(argv[2]);

	a = add_two_numbers(a, b);
	a = do_some_math(a, b);

	printf("Result: %i\n", a);

	return 0;
}

