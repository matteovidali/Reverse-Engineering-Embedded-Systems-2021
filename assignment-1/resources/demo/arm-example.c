#include <stdio.h>
#include <stdlib.h>

void failed_input()
{
	puts("Incorrect input!");
	exit(1);
}

void evaluate_input(const char * input)
{	
	int a, b, c, nconvs;

	nconvs = sscanf(input, "%d %d %d", &a, &b, &c);

	if (nconvs != 3)
		failed_input();

	if (c != a * b)
		failed_input();

	return;
}

int main()
{
	char input[80];

	puts("Input the key:");
	fgets(input, 80, stdin);
	
	evaluate_input(input);
	puts("You made it!");

	return 0;
}

