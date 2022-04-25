import generate

def assert_equals(v1, v2):
    if type(v1) == type(set()):
        print([i for i in v1], [i for i in v2])
        if type(v2) != type(set()) or v1 != v2:
            raise Exception("Assert Exception")

        

def testUnion(gen):
    s1 = set([1,2,3])
    s2 = set([1,2,3])

    assert_equals(set([1,2,3]), gen.union(s1,s2))

    s1 = set([1,2,3])
    s2 = set([1,2,4])

    assert_equals(set([1,2]), gen.union(s1,s2))

    s1 = set()
    s2 = set([1,2,4])

    assert_equals(set(), gen.union(s1,s2))


def testWFC():
    gen = generate.WFC(5,5,None)

    testUnion(gen)

if "__main__" in __name__:
    testWFC()