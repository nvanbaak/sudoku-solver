from abc import ABC, abstractmethod
import numpy as np
from math import floor
import sys
import threading
import time

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
        output_str = "╔═══════╤═══════╤═══════╗\n"
        for row in range(0, 9):
            output_str += "║ "
            for col in range(0,9):
                value = int(self.array[row, col])
                if value == 0:
                    value = "·"
                elif value == -1:
                    value = "!"
                output_str += f"{value} "
                if (col + 1) % 3 == 0:
                    output_str += "│ " if col != 8 else "║"
            output_str += "\n"
            if (row+1) % 3 == 0:
                border = "╚═══════╧═══════╧═══════╝\n" if row == 8 else "╟───────┼───────┼───────╢\n"
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

    def solution_is_valid(self):
        """
        validation method called to ensure puzzle is valid once solved
        :params:
        returns: True if solution is correct, False otherwise
        """
        for index in range(0, 9):
            for digit in range(1, 10):
                if not self.__rows[index].has(digit):
                    return False
                if not self.__cols[index].has(digit):
                    return False
                if not self.__boxes[index].has(digit):
                    return False
        return True


    def solve(self):
        """
        runs through various solver methods
        """
        try:
            self.find_forced_digits()
            if not self.solution_is_valid():
                raise RuntimeError("Invalid solution!")
        except RuntimeError:
            print("ERROR: solve terminated with invalid solution")
        return

    def find_forced_digits(self):
        """
        Loops through rows, columns and boxes placing digits that can only go in one location.
        """
        while True:
            if self.find_naked_singles():
                pass
            elif self.find_forced_digits_in_rows():
                pass
            elif self.find_forced_digits_in_columns():
                pass
            elif self.find_forced_digits_in_boxes():
                pass
            else:
                break

    def solve_multithreaded(self):
        """
        Runs each solve method in a separate thread
        """

        method_dict = {
            "naked_singles" : True,
            "forced_rows" : True,
            "forced_columns" : True,
            "forced_boxes" : True
        }

        threads = []

        for technique in ["naked_singles", "forced_rows", "forced_columns", "forced_boxes"]:
            threads.append(threading.Thread(None, 
                target=self.run_methods_in_thread, 
                args=(technique, method_dict)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # while threading.active_count() > 0:
        #     pass


    def run_methods_in_thread(self, technique, dict):
        """
        Solve method intended to be threaded; loops the given solution method
        until no more progress is made
        """
        solution_dict = {
            "naked_singles" : self.find_naked_singles,
            "forced_rows" : self.find_forced_digits_in_rows,
            "forced_columns" : self.find_forced_digits_in_columns,
            "forced_boxes" : self.find_forced_digits_in_boxes
        }

        # loop as long as someone somewhere is making progress on the puzzle
        while True in dict.values():
            digit_placed = solution_dict[technique]()
            dict[technique] = digit_placed
            # once everything returns negative it runs one more time,
            # just in case another thread was slow bringing the good news 
            # if not True in dict.values():
            #     digit_placed = solution_dict[technique]()
            #     dict[technique] = digit_placed


    def find_forced_digits_in_rows(self):
        """
        For all rows, find places where digits can only go in one position
        :params:
        returns: True if a digit was placed; False otherwise.
        """
        digit_found = False
        for row in range(0, 9):
            for digit in range (1, 10):
                # skip if the digit's already present
                if not self.__rows[row].has(digit):
                    # begin locating open cells
                    open_columns = []

                    # this loop iterates over the boxes the row is in
                    box_row = 3 * floor(row/3)
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

        return digit_found

    def find_forced_digits_in_columns(self):
        """
        For all columns, find places where digits can only go in one position
        :params:
        returns: True if a digit was placed; False otherwise.
        """
        digit_found = False
        for col in range(0, 9):
            for digit in range (1, 10):
                # skip if the digit's already present
                if not self.__cols[col].has(digit):
                    # begin locating open cells
                    open_rows = []

                    # this loop iterates over the boxes the row is in
                    box_col = floor(col/3)
                    for box in [0, 3, 6]:
                        box_index = box + box_col

                        # if the digit isn't in the box, add all empty cells
                        if not self.__boxes[box_index].has(digit):
                            for num in range(0, 3):
                                row_index = num + box
                                if self.array[row_index, col] == 0:
                                    open_rows.append(row_index)

                    # weed out cells with column conflicts
                    candidate_cells = []
                    for row in open_rows:
                        if not self.__rows[row].has(digit):
                            candidate_cells.append(row)

                    # if only one cell remains, place the digit
                    if len(candidate_cells) == 1:
                        self.array[candidate_cells[0], col] = digit
                        digit_found = True

        return digit_found

    def find_forced_digits_in_boxes(self):
        """
        For all columns, find places where digits can only go in one position
        :params:
        returns: True if a digit was placed; False otherwise.
        """
        digit_found = False
        # for each box, check for missing digits
        for box in range(0, 9):
            for digit in range (1, 10):
                if not self.__boxes[box].has(digit):

                    # check which of the rows and columns are restricted
                    open_rows = []
                    open_cols = []
                    for index in range (0, 3):
                        row_index = 3*floor(box/3) + index
                        if not self.__rows[row_index].has(digit):
                            open_rows.append(row_index)
                        col_index = 3 * (box % 3) + index
                        if not self.__cols[col_index].has(digit):
                            open_cols.append(col_index)

                    candidate_cells = []
                    for row in open_rows:
                        for col in open_cols:
                            candidate_cells.append((row, col))

                    if len(candidate_cells) == 1:
                        location = candidate_cells[0]
                        self.array[location[0], location[1]] = digit
                        digit_found = True

        return digit_found

    def find_naked_singles(self):
        """
        Finds cells that can only have one value
        :params:
        returns: True if digit place, False otherwise
        """
        digit_found = False
        # oop over all empty cells in the puzzle
        for row in range(0, 9):
            for col in range (0, 9):
                if self.array[row, col] == 0:

                    # try each digit and store if viable
                    valid_digits = []
                    for digit in range(1,10):

                        if self.digit_allowed_at(digit, row, col):
                            valid_digits.append(digit)

                            # since we're only looking for naked singles,
                            # stop looping if we find a second viable digit
                            if len(valid_digits) > 1:
                                break

                    if len(valid_digits) == 1:
                        self.array[row, col] = valid_digits[0]
                        digit_found = True
                    elif len(valid_digits) == 0:
                        self.array[row, col] = -1
                        raise RuntimeError("found cell with no valid digits!")

        return digit_found


if __name__ == "__main__":

    for arg in sys.argv[1:]:
        def zipper_print(str1, str2):
            """
            prints two strings of equal size next to each other to save terminal space
            """
            str1 = str1.split("\n")
            str2 = str2.split("\n")

            output_str = ""
            for line in str1:
                other_line = str2.pop(0)
                output_str += f"{line}     {other_line}\n"
            return output_str

        test_puzzle = Puzzle(arg)
        test_puzzle_2 = Puzzle(arg)

        # test without threading
        start_time = time.time()

        before = str(test_puzzle)
        test_puzzle.solve()
        after = str(test_puzzle)

        single_time = f"Solve time without threading: {time.time()  - start_time} seconds"

        start_time = time.time()

        before_threaded = str(test_puzzle_2)
        test_puzzle_2.solve_multithreaded()
        after_threaded = str(test_puzzle_2)

        threaded_time = f"Solve time with threading: {time.time()  - start_time} seconds"

        print(zipper_print(before_threaded, after_threaded))
        print(single_time)
        print(threaded_time)

