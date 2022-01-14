#include <stdio.h>

int __attribute__ ((noinline)) add_two_numbers(int a, int b)
{
	return a + b;
}

int __attribute__ ((noinline)) multiply_two_numbers(int a, int b)
{
	return a*b;
}

int main(int argc, char **argv)
{
	int a, b;
	printf("Enter two numbers: ");
	scanf("%d %d", &a, &b);
	printf("The sum of the two numbers is %i\n", add_two_numbers(a, b));
	printf("The product of the two numbers is %i\n", multiply_two_numbers(a, b));
	return 0;
}

