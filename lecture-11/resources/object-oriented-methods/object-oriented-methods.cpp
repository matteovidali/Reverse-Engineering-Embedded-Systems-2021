#include <iostream>

class Animal
{
	public:
		int num_legs;
		bool has_tail;
		Animal(void) : num_legs(4),has_tail(true) {}
		Animal(int nl, bool ht) : num_legs(nl),has_tail(ht) {}
		void print_attributes() {
			std::cout << "This animal has " << this->num_legs << " legs." << std::endl;
			std::cout << "Does this animal have a tail? " << this->has_tail << std::endl;
		}
};

int main(void)
{
	Animal * dog1 = new Animal();
	Animal * centipede1 = new Animal(100, false);

	dog1->print_attributes();
	centipede1->print_attributes();

	delete dog1;
	delete centipede1;
	return 0;
}

