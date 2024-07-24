import os
from sample_b import f, g

def main():
    print("hello world!", os.path.join(__file__, "a/b"))
    x = 3
    y = 4
    print("f", f(x, y))
    print("g", g(x, y))

main()
