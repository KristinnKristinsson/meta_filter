# Scenario for full tool usage — includes functions with issues and complexities

# @issue bug: Function throws division by zero error when input is zero
def divide(a, b):
    return a / b

# @issue logic: Function always returns wrong sum due to off-by-one error
def add_numbers(n):
    total = 0
    for i in range(n):  # should be range(n+1)
        total += i
    return total

# @issue arch: This function contains two responsibilities and should be split
def update_user_profile(user_id, new_data):
    # update database (side-effect)
    db = connect_to_db()
    db.update(user_id, new_data)

    # compute analytics (pure)
    summary = {
        'length': len(new_data),
        'uppercase_fields': [k for k in new_data if k.upper() == k]
    }
    return summary

# @issue algo: Bubble sort is slow, consider replacing with merge sort
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# @issue algo: Merge sort is more efficient, but still recursive and stack-heavy
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# @issue algo: Red-black tree sort is advanced but poorly explained; add clarity
def red_black_tree_sort(arr):
    class Node:
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None
            self.color = 'red'  # just a placeholder for actual color logic

    def insert(root, node):
        if root is None:
            return node
        if node.key < root.key:
            root.left = insert(root.left, node)
        else:
            root.right = insert(root.right, node)
        return root

    def inorder(root):
        if root is None:
            return []
        return inorder(root.left) + [root.key] + inorder(root.right)

    root = None
    for value in arr:
        root = insert(root, Node(value))
    return inorder(root)


if __name__ == '__main__':
    print("Test scenario ready. Run sweep.py on this file to extract issues.")
