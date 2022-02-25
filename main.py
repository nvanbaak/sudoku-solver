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

        @property
        def array(self):
            return self.__array

        @property
        def index(self):
            return self.__index

        @property
        def solved_digits(self):
            return self.__solved_digits

        @property
        def required_digits(self):
            return self.__required_digits

        @abstractmethod
        def has(self, digit):
            return digit in self.contents()

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
            return self.array[:, self.index]

        def has(self, digit):
            return super().has(digit)

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
            return self.array[self.index, :]

        def has(self, digit):
            return super().has(digit)

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
            box_row = 3 * floor(self.index / 3)
            # boxes 0, 3, 6 are col 0; and so on
            box_col = 3 * (self.index % 3)

            return self.array[box_row:box_row+3, box_col:box_col+3]

        def has(self, digit):
            return super().has(digit)

    # Finally got to the Puzzle init
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
            self.__rows[index] = self.Row(self.__array, index)
            self.__cols[index] = self.Column(self.__array, index)
            self.__boxes[index] = self.Box(self.__array, index)

    # boilerplate methods

    @property
    def array(self):
        return self.__array

    def __str__(self):
        """
        Returns puzzle as a string
        """
        output_str = "╔═══════╦═══════╦═══════╗\n"
        for row in range(0, 9):
            output_str += "║ "
            for col in range(0,9):
                value = int(self.array[row, col])
                if value == 0:
                    value = "·"
                output_str += f"{value} "
                if (col + 1) % 3 == 0:
                    output_str += "│ " if col != 8 else "║ "
            output_str += "\n"
            if (row+1) % 3 == 0:
                border = "╚═══════╩═══════╩═══════╝\n" if row == 8 else "╠───────┼───────┼───────╣\n"
                output_str += border
        return output_str

    def draw__with_fancy_borders(self):
        """
        Alternate version of __str__ that I mothballed for being too busy
        """
        output_str = "XX===========XX===========XX===========XX\n"
        for row in range(0, 9):
            output_str += "||"
            for col in range(0,9):
                value = int(self.array[row, col])
                if value == 0:
                    value = " "
                output_str += f" {value} |"
                if (col + 1) % 3 == 0:
                    output_str += "|" 
            output_str += "\n"
            if (row+1) % 3 == 0:
                output_str += "XX===========++===========++===========XX\n"
            else:
                output_str += "||---+---+---||---+---+---||---+---+---||\n"
        return output_str

    def get_box(self, row, col):
        """
        Returns the index of the Box object which contains the given location
        """
        row_index = 3 * floor(row/3)
        col_index = floor(col/3)
        return row_index + col_index

    def digit_allowed_at(self, value, row, col):
        """
        Helper function that determines whether a given value is allowed at the given location
        """
        # check row and col
        if self.__rows[row].has(value):
            return False
        if self.__cols[col].has(value):
            return False
        box_index = self.get_box(row, col)
        return not self.__boxes[box_index].has(value)

    def find_forced_digits_in_rows(self):
        """
        For all rows, find places where digits can only go in one position
        """
        digit_found = False
        for row in range(0, 9):
        # row = 2
        # if True:
            for digit in range (1, 10):
                # skip if the digit's already present
                if not self.__rows[row].has(digit):
                    # begin locating open cells
                    open_columns = []

                    # this loop iterates over the boxes the row is in
                    box_row = floor(row/3)
                    for box in [0, 1, 2]:
                        box_index = box + box_row

                        # if the digit isn't in the box, add all empty cells
                        if not self.__boxes[box_index].has(digit):
                            for num in range(0, 3):
                                col_index = num + box*3
                                if self.array[row, col_index] == 0:
                                    open_columns.append(col_index)

                    # weed out cells with column conflicts
                    candidate_cells = []
                    for column in open_columns:
                        if not self.__cols[column].has(digit):
                            candidate_cells.append(column)

                    # if only one cell remains, place the digit
                    if len(candidate_cells) == 1:
                        self.array[row, candidate_cells[0]] = digit
                        digit_found = True

        # recurse until no more digits are found
        # if digit_found:
        #     self.find_forced_digits_in_rows()








if __name__ == "__main__":
    test_puzzle = Puzzle("sudoku1.txt")
    print(test_puzzle)
    test_puzzle.find_forced_digits_in_rows()
    print(test_puzzle)