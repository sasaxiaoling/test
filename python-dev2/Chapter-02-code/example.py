def permit(func):
    print('sss')
    def wrapper():
        print('123')
    return wrapper


@permit
def test1():
    data = "1,2,3"
    print(data)

@permit
def test2():
    data = "4,5,6"
    print(data)

test1()