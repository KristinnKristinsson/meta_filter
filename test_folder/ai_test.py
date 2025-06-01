from pathlib import Path

# Rewriting ai_test.py after environment reset

# @issue logic: Function does not return a value
def no_return_add(a, b):
    c = a + b

# @issue logic: Function ignores input and always returns 42
def constant_result(input):
    return 42

# def broken_syntax():
#     print("Hello

# @issue logic: Infinite recursion with no base case
def recursive_bomb(n):
    return recursive_bomb(n + 1)

# @issue logic: Division by zero
def divide_by_zero():
    return 1 / 0

# @issue perf: Inefficient use of sum in a loop
def repeated_sum(n):
    total = 0
    for i in range(n):
        total += sum(range(n))
    return total

count = 0

# @issue arch: Global variable used
def increment_global():
    global count
    count += 1
    return count

# @issue style: Unnecessary nested if statements
def check_even(n):
    if n % 2 == 0:
        if True:
            if not False:
                return True
    return False

# @issue style: Variable shadowing
def shadow_example(val):
    val = 10
    def inner():
        val = 20
        return val
    return inner()

# @issue style: Unused variable in the code
def stuff(a):
    unused = 12345
    asdf = a * a
    return asdf