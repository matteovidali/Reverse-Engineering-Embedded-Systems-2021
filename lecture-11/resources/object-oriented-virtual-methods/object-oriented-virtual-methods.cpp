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
		virtual void print_sound(void) =0;
		virtual void print_food(void) =0;
};

class Dog: public Animal
{
	public:
		Dog(void) : Animal(4, true) {}
		void print_sound(void)
		{
			std::cout << "Woof!" << std::endl;
		}
		void print_food(void)
		{
			std:: cout << "Dog food." << std::endl;
		}
};

class Centipede: public Animal
{
	public:
		Centipede(void) : Animal(100, false) {}
		void print_sound(void)
		{
			std::cout << "*silence*" << std::endl;
		}
		void print_food(void)
		{
			std:: cout << "Bugs and stuff." << std::endl;
		}
};

void print_animal_info(Animal * animal)
{
	animal->print_attributes();
	animal->print_sound();
	animal->print_food();
}

int main(void)
{
	Dog * dog1 = new Dog();
	Centipede * centipede1 = new Centipede;

	print_animal_info(dog1);
	print_animal_info(centipede1);

	delete dog1;
	delete centipede1;
	return 0;
}

