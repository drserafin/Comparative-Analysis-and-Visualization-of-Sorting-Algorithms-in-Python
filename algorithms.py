def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j+ 1], arr[j]
                yield arr, [j, j+1] 

            else:
                 yield arr, [j, j+1]

# -----------------------------------------------------------------------------
# MERGE SORT IMPLEMENTATION
# NOTE: This is split into 3 functions to handle the recursion with Python's
# 'yield' generator system:
#
# 1. merge_sort(arr): The "Wrapper"
#    - The main entry point. It hides the complexity of indices (start/end)
#    - It simply calls the recursive function on the whole list.
#
# 2. merge_sort_recursive(arr, start, end): The "Splitter"
#    - Handles the "Divide" phase of Divide-and-Conquer.
#    - It recursively splits the list into smaller halves using 'yield from'.
#
# 3. merge(arr, start, mid, end): The "Worker"
#    - Handles the "Conquer" phase.
#    - This is where the actual sorting happens and where we yield the
#      visual updates (bar movements) to the screen.
# -----------------------------------------------------------------------------

def merge_sort(arr):
    """
    Starts the recursive merge sort.
    """
    yield from merge_sort_recursive(arr, 0, len(arr) - 1)

def merge_sort_recursive(arr, start, end):
    """
    Recursive helper function.
    Uses 'yield from' to pass animation steps up to the main loop.
    """
    if start < end:
        mid = (start + end) // 2

        # Sort left half
        yield from merge_sort_recursive(arr, start, mid)
        
        # Sort right half
        yield from merge_sort_recursive(arr, mid + 1, end)
        
        # Merge the two halves
        yield from merge(arr, start, mid, end)

def merge(arr, start, mid, end):
    left_part = arr[start:mid + 1]
    right_part = arr[mid + 1:end + 1]

    i = 0
    j = 0
    k = start

    while i < len(left_part) and j < len(right_part):
        yield arr, [start + i, mid + 1 + j]

        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        
        yield arr, [k]
        k += 1

    while i < len(left_part):
        arr[k] = left_part[i]
        yield arr, [k]
        i += 1
        k += 1

    while j < len(right_part):
        arr[k] = right_part[j]
        yield arr, [k]
        j += 1
        k += 1
