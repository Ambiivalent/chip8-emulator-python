import numpy as np

class Stack:
    def __init__(self):
        self.stack = np.zeros(16, dtype=np.uint16)
        self.top = -1
    def pop(self):
        if len(self.stack) == 1: print("Stack is empty")
        else: self.top -= 1
    def push(self,item):
        if self.size() == 15: print("Stack is full")
        else:
            self.top += 1
            self.stack[self.top] = item
    def size(self):
        return self.top
    def peek(self):
        return self.stack[self.top]