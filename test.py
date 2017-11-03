a = [1, 3, 5, 7, 9, 11, 13, 15]
b = [0, 2, 4, 6, 8, 10]

def start():
    test = []
    test_len = len(a + b)

    position = 0
    for i in b:
        test.insert(position, i)
        position = position + 2

    position = 1
    for i in a:
        test.insert(position, i)
        position = position + 2

    print test
    print("====================")

start()


def fib(n):
    print n

    # 0 1 1 2 3 5 8 13

    mas = []
    a = 0
    b = 1
    result = a + b
    mas.append(a)
    mas.append(b)
    while result < n:
        mas.append(result)
        a = b
        b = result
        result = a + b

    print mas


fib(1010000000000)


def dec(somefunction):
    def wrapper():
        print "====================="

        somefunction()

        print "....................."
    return wrapper()


def hello():
    print "HELLO"

test = dec(hello)

