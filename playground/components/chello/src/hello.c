
#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
#include <direct.h>
#define getcwd _getcwd
#else
#include <unistd.h>
#endif

#include <hello.h>
#include <playground.h>
#include <math.h>

int main(int argc, char* argv[])
{
	char buf[1024];

	say_hello();

	printf("The current directory is: %s\n", getcwd(buf, sizeof(buf)));
	printf("Playground: %s\n", PLAYGROUND);
	printf("sin: %f\n", sin(1.0));
	return EXIT_SUCCESS;
}

void say_hello()
{
	printf("Hello! (version %s)\n", HELLO_VERSION);
}
