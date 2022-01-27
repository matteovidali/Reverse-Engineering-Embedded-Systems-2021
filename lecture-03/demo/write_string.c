#include <unistd.h>
#include <stdio.h>

int simple_strlen(const char *s)
{
	int len = 0;
	while (*s++ != 0)
		len++;
	return len;
}

void print_this_string(const char *s)
{
	write(1, s, simple_strlen(s));
}

int main(void)
{
	char s[] = "This is the output string.\n";
	puts("Printing the output string:");
	print_this_string(s);
	return 0;
}

