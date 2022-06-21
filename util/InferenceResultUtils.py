from collections import deque
from typing import Deque


class InferenceResultUtils:
    last_x_probabilities: Deque[float]

    def __init__(self):
        self.last_x_probabilities = deque(maxlen=100)

    def average_of_probabilities(self):
        lst = self.last_x_probabilities
        try:
            return sum(lst) / len(lst)
        except ZeroDivisionError:
            print(lst)
            return 0
