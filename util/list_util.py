def average_of_list(lst):
    try:
        return sum(lst) / len(lst)
    except ZeroDivisionError:
        print(lst)
        return 0