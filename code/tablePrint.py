"""Prints over itself in a tablized format"""
import time
from math import floor

class Table_Print:
    print_var           = {}
    print_var_reporting = {}
    t0                  = time.time()
    longest_key = -1
    longest_string = -1
    def time_helper(self):
        elapsed = int(time.time() - self.t0)
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        self.print_var['TIME_ELAPSED'] = "%d:%02d:%02d" % (h, m, s)

    def table_left_just(self, slot, string):
        if len(slot) > self.longest_key:
            self.longest_key = len(slot)
        if len(string) > self.longest_string:
            self.longest_string = len(string)
        height = len(self.print_var)+len(self.print_var_reporting)
        width  = self.longest_key * self.longest_string
        self.bksp_count = height * width

    def table_print(self):
        # Backspace all printed characters
        print('\b'*self.bksp_count)
        # Print all of the keys inside of the box
        for k,v in self.print_var.items():
            # Print carriage return so we can print over ourselves
            print("#" + k + ":" + ' '*(self.longest_key - len(k)) + v, end="\r")
        # Print reporting separate from crawling
        for k,v in self.print_var_reporting.items():
            print("#" + k + ":" + ' '*(self.longest_key - len(k)) + v, end="\r")

    #Sets the string passed in, and prints it in a table format
    def tabularize(self, slot, string):
        s = str(string)
        self.print_var[slot] = s
        self.time_helper()
        self.table_left_just(slot, s)
        # self.table_print()

    def tabularize_reporting(self, slot, string):
        s = str(string)
        self.print_var_reporting[slot] = s
        self.time_helper()
        self.table_left_just(slot, s)
        self.table_print()

    def save_to_disk(self, string):
        try:
            print(string, self.file, end='\n')
        except:
            print("Failed to save to disk, saving as tmp.log")
            print(string, "tmp.log", end='\n')
