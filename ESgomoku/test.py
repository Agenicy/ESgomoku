class Test(object):
    value = 1
    node = None
    def PrintValue(self):
        node = Node(parent = self)
        print(self.value)
        print(node.value)

class Node(object):
    parent = None
    value = 1
    def __init__(self, parent, value = 0):
        self.value = parent.value

a=Test()
a.value = 2
b = a
b = Test()
print(a.value,b.value)

