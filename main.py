from abc import ABC, abstractmethod
import numpy as np
from math import floor

class Puzzle:
    """
    Class representing a single Sudoku puzzle

    :params:
    input: filepath to a .txt file containing a sudoku puzzle
          - see readme for more details
    """
    class Area(ABC):
        """
        Abstract class containing shared methods for Row, Column and Box
        """
        def __init__(self, array, index):
            self.__array = array
            self.__index = index
            self.__solved_digits = []
            self.__required_digits = []

            initial_values = self.contents()
            for digit in range(1, 10):
                if digit in initial_values:
                    self.__solved_digits.append(digit)
                else:
                    self.__required_digits.append(digit)

        @abstractmethod
        def contents(self):
            """
            Returns the slice of the array represented by this area
            """
            return None

    class Column(Area):
        """
        Class representing one column of the puzzle
        """
        def __init__(self, array, index):
            super().__init__(array, index)

        def contents(self):
            """
            Returns the slice of the array represented by this object
            """
            return self.__array[:, self.__index]

    class Row(Area):
        """
        Class representing one row of the puzzle
        """
        def __init__(self, array, index):
            super().__init__(array, index)

        def contents(self):
            """
            Returns the slice of the array represented by this object
            """
            return self.__array[self.__index, :]

    class Box(Area):
        """
        Class representing one box in the puzzle
        """
        def __init__(self, array, index):
            super().__init__(array, index)

        def contents(self):
            """
            Returns the slice of the array represented by this object
            """
            # boxes 0-2 are row 0, 3-5 are row 1, 6-8 are row 2
            box_row = floor(self.__index / 3)
            # boxes 0, 3, 6 are col 0; and so on
            box_col = (self.__index - 1) % 3

            return self.__array[box_row:box_row+3, box_col:box_col+3]

    def __init__(self, input) -> None:

        self.__array = np.zeros((9,9))

        # read data from file
        with open(input, "r", -1, "utf8") as input_file:
            for row in range(0, 9):
                row_data = input_file.readline().replace("\n", "")
                row_data = row_data.split(" ")
                for col in range(0, 9):
                    self.__array[row, col] = int(row_data[col])

        # set up rows, columns, and boxes
        self.__rows = {}
        self.__cols = {}
        self.__boxes = {}

        for index in range (0, 9):
            self.__rows[index] = self.Row(index)
            self.__cols[index] = self.Column(index)
            self.__boxes[index] = self.Box(index)