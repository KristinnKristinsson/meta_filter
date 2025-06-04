from pathlib import Path

# Rewriting ai_test.py after environment reset

# @issue logic: Function does not return any value
def no_return_add(a, b):
    c = a + b

# @issue logic: Function does not use the input parameter
def constant_result(input):
    return 42

# def broken_syntax():
#     print("Hello

# @issue perf: Function will cause a stack overflow due to infinite recursion
def recursive_bomb(n):
    return recursive_bomb(n + 1)

# @issue bug: Function will throw a ZeroDivisionError
def divide_by_zero():
    return 1 / 0

# @issue perf: Unnecessary repeated computation of sum(range(n))
def repeated_sum(n):
    total = 0
    for i in range(n):
        total += sum(range(n))
    return total

count = 0

# @issue arch: Function modifies a global variable, which is generally not recommended
def increment_global():
    global count
    count += 1
    return count

# @issue style: Nested if statements are redundant and make the code harder to read
def check_even(n):
    if n % 2 == 0:
        if True:
            if not False:
                return True
    return False


# @issue style: Function has variable shadowing which can lead to confusion
def shadow_example(val):
    val = 10
    def inner():
        val = 20
        return val
    return inner()

# @issue style: Variable 'unused' is declared but never used
def stuff(a):
    unused = 12345
    asdf = a * a
    return asdf