# Simple iterator example

numbers = [1, 2, 3, 4]

my_iter = iter(numbers)

print(next(my_iter))
print(next(my_iter))
print(next(my_iter))
print(next(my_iter))


# Simple generator example

def my_generator():
    for i in range(5):
        yield i

gen = my_generator()

for value in gen:
    print(value)