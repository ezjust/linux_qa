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

#start()


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


#fib(1010000000000)


def dec(somefunction):
    def wrapper():
        print "====================="

        somefunction()

        print "....................."
    return wrapper()


def hello():
    print "HELLO"

#test = dec(hello)


def massiv(a, b):
    # diagonal for matrix \
    import random
    data = [[random.randint(0, 9) for x in range(a)] for y in range(b)]
    print data
    i = 0
    j = 0
    print('................')
    while i < len(data):
        while j < len(data[0]):
            print data[i][j]
            i+=1
            j+=1

    # diagonal for matrix /
    i = 0
    j = 0
    print('================')
    while i < len(data):
        while j < len(data[0]):
            #print(len(data[0])-j)
            print data[i][(len(data[0])-1)-j]
            i+=1
            j+=1
#massiv(6, 6)

print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


class Palindrome:
    @staticmethod
    def is_palindrome(word):

        new_word = []

        i = 0

        for i in range(0, len(word)):
            new_word.append(word[len(word) - i - 1])

        new_word = "".join(new_word)
        print(new_word)
        print(word)
        if word.lower() == new_word.lower():
            return True
        else:
            return False


#print(Palindrome.is_palindrome('Deleveled'))
def merge_lists():
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    c = []
    import random
    m = [[random.randint(0,10) for x in range(0, 10)] for y in range(0, 5)]
    print m
    print a
    print b
    max_amount = max(len(m), len(b))
    for i in range(0, max_amount):
        try:
            c.append(a[i])
        except IndexError:
            pass
        try:
            c.append(b[i])
        except IndexError:
            pass
    print c

merge_lists()