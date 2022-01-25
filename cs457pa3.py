#############################
## Jason Brown             ##
## Project 3               ##
## CS 457 - September 2021 ##
#############################

import os # file manipulation
import re # regex searches for commands
from contextlib import contextmanager #needed for multiple file opening

# directory trackers to manage scope
global_directory = ""
current_directory = ""
database_title = "Jasons_DBMS"
flag = False

def main():
    print("+-------------------------+")
    print("| WELCOME TO JASON'S DBMS |")
    print("+-------------------------+")
    print("   .exit  to end program   ")

    try:
        # constant loop to search for user input commands
        while True:

            command = ""
            command += input("\nPlease Enter Command: \n").strip('\r')
            while not ";" in command and not "--" in command and command != "\n":
                if ".exit" in command:
                    print("Exiting program. Thank you!\n")
                    exit()
                command += input("").strip('\r')

            if ';' in command:
                command = command.split(";")[0]
            command_string = str(command)
            command_string = command_string.upper() # make all uppercase so program can recognize command
            
            # Execute functions triggered by terminal commands #
            # if "--" in command:  # skip comment
            #     pass
            if "CREATE DATABASE" in command_string:
                create_database(command)
            elif "CREATE TABLE" in command_string:
                create_table(command)
            elif "DROP DATABASE" in command_string:
                delete_database(command)
            elif "DROP TABLE" in command_string:
                delete_table(command)
            elif "USE" in command_string:
                use_database(command)
            elif "ALTER TABLE" in command_string:
                alter_table(command)
            elif "SELECT" in command_string:
                select_from(command, command_string)
            elif "INSERT INTO" in command_string:
                insert_into(command)
            elif "UPDATE" in command_string:
                update_command(command)
            elif "DELETE FROM" in command_string:
                delete_command(command)
                # elif ".exit" in command: 
                #     print("Exiting program. Thank you!\n")
                #     exit()
            else:
                print("Invalid input. Try again.")

    except (EOFError, KeyboardInterrupt) as e: 
        print("\nEnding Scipt.")

@contextmanager
def multi_file_manager(files, mode='rt'):
    files = [open(file, mode) for file in files]
    yield files
    for file in files:
        file.close()

# Helper Function #
# Check global scope for selected database, update the working directory with current path and global scope
def check_current_scope():
    if global_directory == "":
        raise ValueError("ERROR: No database selected.")
    else:
        global current_directory
        if global_directory is database_title:
            current_directory = os.path.join(os.getcwd(), global_directory)
        elif global_directory == "":
            current_directory = os.path.join(os.getcwd(), database_title)
        else:
            current_directory = os.path.join(os.getcwd(), database_title, global_directory)

# Create a database #
def create_database(input):
    try:
        global global_directory # global calls to update scope
        global database_title
        global_directory = database_title
        check_current_scope() # updating scope with correct directory
        database_name = input.split("CREATE DATABASE ")[1] # title database as user input
        database_file = os.path.join(current_directory, database_name) # append database path with user title
        if os.path.exists(database_file): 
            print(f"Database {database_name} already exists...")
        else:
            os.makedirs(database_file) # create directory
            print(f"Database {database_name} created.") 
    except IndexError:
        print("ERROR: Failed to create database. Invalid input.")

# Create a table #
def create_table(input):
    try:
        check_current_scope() # check scope to put table in right location
        # table_name = (re.search(r"(?<=CREATE TABLE\s).*(?=\s\()", input)).group()
        table_name = re.split("CREATE TABLE ", input, flags=re.IGNORECASE)[1] # retrieve the title of the table
        table_name = table_name.split("(")[0].lower() # make lowercase for path traversal
        table_file = os.path.join(current_directory, table_name) # add table name to working path
        if os.path.exists(table_file):
            print(f"Table {table_name} already exists...")
        else:
            with open(table_file, "w") as table:  # Create a file within folder to act as a table
                print(f"Table {table_name} created.")
                if "(" in input: # check for parameters
                    table_output = []  # array for table output
                    # table_data = (re.search(r"(?<=\(\s).*(?=\s\))", input)).group()
                    table_data = input.split("(", 1)[1]  # Delete (
                    table_data = table_data[:-1]  # Delete )
                    param_count = table_data.count(",")  # parameter count
                    for i in range(param_count + 1):
                        table_output.append(table_data.split(", ")[i])  # append array with table parameters
                    table.write(" | ".join(table_output))  # Output array to the file, separated by lines
    except IndexError:
        print("ERROR: Failed to create table. Invalid input.")

# Delete a database #
def delete_database(input):
    try:
        check_current_scope() # check scope to locate database to be deleted
        dir_to_delete = input.split("DROP DATABASE ")[1].lower() # collect name and make lowercase
        path_to_dir = os.path.join(current_directory, dir_to_delete) # append database to path
        if not os.path.exists(path_to_dir):
            print(f"Database {dir_to_delete} does not exist...")
        else:
            for contents in os.listdir(path_to_dir): # delete what's inside of the database
                os.remove(f"{path_to_dir}/{contents}") # Delete internal files
            os.rmdir(path_to_dir) # Delete directory
            print(f"Database {dir_to_delete} deleted.")
    except IndexError:
        print("ERROR: Failed to delete database. Invalid input.")

# Delete a table #
def delete_table(input):
    try:
        check_current_scope() # check scope to locate table to be deleted
        table_to_delete = input.split("DROP TABLE ")[1].lower()# collect name and make lowercase
        path_to_table = os.path.join(current_directory, table_to_delete) # append database to path
        if not os.path.isfile(path_to_table): # if not a file, print warning
            print(f"Table {table_to_delete} does not exist...")
        else:
            os.remove(path_to_table) # Delete table
            print(f"Table {table_to_delete} deleted.")
    except IndexError:
        print("ERROR: Failed to delete table. Invalid input.")
    except ValueError:
        print("ERROR: No database was found in the current directory.")

# Use database #
# Manually adjusts the scope of the directories in order to locate the correct items.
def use_database(input):
    try:
        global global_directory # global call 
        global_directory = input.split("USE ")[1] # make global_directory = name of directory
        check_current_scope() # update current directory with global directory # this is what does the bulk of the work
        # use_path = os.path.join(current_directory, global_directory)
        if os.path.exists(current_directory): # this tells the user the job is done
            print(f"Now using {global_directory}.")
        else:
            raise ValueError("Database does not exist...")
    except IndexError:
        print("ERROR: Failed to use database. Invalid input.")

# Alter table #
# Only has ADD capability now, appends to file (table)
def alter_table(input):
    try:
        check_current_scope() # update current directory and scope
        table_name = input.split("ALTER TABLE ")[1] # retrieve name of the file to alter
        table_name = table_name.split(" ")[0].lower() # still collecting name
        file_path = os.path.join(current_directory, table_name) # append name to current directory to locate file
        if os.path.isfile(file_path): # if file --> add new data
            if "ADD" in input:  
                with open(file_path, "a") as table: # open file and append to end of file
                    string_to_add = input.split("ADD ")[1] # collect parameters to add
                    table.write(f" | {string_to_add}") # separate new data with lines
                    print(f"Table {table_name} modified.")
        else:
            print(f"Table {table_name} does not exist.")
    except IndexError:
        print("ERROR: Failed to alter table. Invalid input.")

# Select from algorithm #
# Reads and writes data from file. Very standard right now. 
def select_from(command, line):
    try:
        table_array = []
        table_varibles = []
        file_names = []
        table_search = {}
        input_tables = []

        check_current_scope() # check scope to ensure correct file is selected
        if "JOIN" in line:
            input_to_read = re.split("FROM ", command, flags =re.IGNORECASE)[1]

            if "LEFT" in line:
                # first and second table organization
                table_left = re.split("LEFT", input_to_read, flags=re.IGNORECASE)[0].lower()
                table_right = re.split("JOIN ", input_to_read, flags=re.IGNORECASE)[1].lower()
                table_right = re.split("ON", table_right, flags=re.IGNORECASE)[0].strip()
                table_left = re.split(" ", table_left, flags=re.IGNORECASE)[0].strip()
                table_right = re.split(" ", table_right, flags=re.IGNORECASE)[0].strip()
                table_array.append(table_left) 
                table_array.append(table_right)
                location = 'left'

            elif "INNER" in line:
                # first and second table organization
                table_left = re.split("INNER", input_to_read, flags=re.IGNORECASE)[0].lower()
                table_right = re.split("JOIN ", input_to_read, flags=re.IGNORECASE)[1].lower()
                table_right = re.split("ON", table_right, flags=re.IGNORECASE)[0].strip()
                table_left = re.split(" ", table_left, flags=re.IGNORECASE)[0].strip()
                table_right = re.split(" ", table_right, flags=re.IGNORECASE)[0].strip()
                table_array.append(table_left) 
                location = 'inner'
                table_array.append(table_right) 

            elif "RIGHT" in line: 
                # first and second table organization
                # not used completely
                table_array = re.split("RIGHT", input_to_read, flags=re.IGNORECASE)[0].lower() #left table
                table_array = re.split("JOIN", input_to_read, flags=re.IGNORECASE)[1].lower() #right table
                location = 'right'

        elif "WHERE" in line:
            input_tables = re.split("FROM ", command, flags=re.IGNORECASE)[1].lower() 
            input_tables = re.split("WHERE", input_tables, flags=re.IGNORECASE)[0]
        else:
            input_tables = re.split("FROM ", command, flags=re.IGNORECASE)[1].lower()
            if "," in input_tables:
                for table in re.split(", ", input_tables):
                    table_array.append(table)
            else:
                table_array.append(input_tables)
        if " " in input_tables:
            input_tables = input_tables.strip("\r") #removes any leftover returns
            input_tables = input_tables.strip() #removes any whitespace

        if "," in input_tables:
            for table in re.split(", ", input_tables):
                table, table_varible = re.split(" ", table, flags=re.IGNORECASE) #grab the left table name
                table_search[table_varible] = table
                table_array.append(table)
                table_varibles.append(table_varible)
        
        for table_name in table_array:
            if table_name:
                file_names.append(os.path.join(current_directory, table_name))

        output = "" # empty string to append

        # allows for the select function to work on multiple tables 
        with multi_file_manager(file_names, "r+") as tables:
            data_to_sort = []
            array_of_input_data = []
            if "JOIN" in line:
                for table in tables:
                    data_to_sort = table.readlines()
                    array_of_input_data.append(data_to_sort)
                toJoinOn = re.split("on", command, flags=re.IGNORECASE)[1]
                counter, output = join_where(toJoinOn, array_of_input_data, location)
            elif "WHERE" in line:
                search_item = re.split("WHERE ", command, flags=re.IGNORECASE)[1]
                counter = 0

                if len(tables) == 1: # old function
                    data_to_sort = tables[0].readlines()
                    counter, output = where(search_item, "select", data_to_sort)
                else: # new capability
                    for table in tables:
                        data_to_sort = table.readlines()
                        array_of_input_data.append(data_to_sort)
                        counter += 1
                    counter, output = join_where(search_item, array_of_input_data)

            # terminal output    
            if "SELECT *" in line:
                if not output == "":  
                    for lines in output:
                        print(lines)
                else: 
                    for table in tables:
                        output += table.read()
                    print(output)
            else:
                parameters_temp = re.split("SELECT", command, flags=re.IGNORECASE)[1]
                params = re.split("FROM", parameters_temp, flags=re.IGNORECASE)[0]
                params = params.split(",")
                if not output == "":  # Checks if the output is allocated
                    lines = output
                else:
                    lines = table.readlines() # splits tables into array of lines
                    data_to_sort = lines 
                for line in lines:
                    out = []
                    for param in params:
                        param = param.strip() # remove whitespace
                        column_index = get_column(data_to_sort)
                        if param in column_index:
                            separated_line = separate(line)
                            out.append(separated_line[column_index.index(param)].strip())
                    print(" | ".join(out))
    except IndexError:
        print("ERROR: No table name specified.")
    except ValueError as err:
        print(err.args[0])


# Insert into #
# Modifies existing tables with specific values.
def insert_into(input):
    try:
        check_current_scope()
        table_name = input.split(" ")[2]  # Retrieve table name from command
        table_name.lower()
        file_name = os.path.join(current_directory, table_name)
        if os.path.isfile(file_name): # check if table exists
            if "values" not in input: # check for parenthesis
                print("ERROR: Failed to insert. Invalid input.")
            else:
                with open(file_name, "a") as table:  # open the file to insert into
                    output_arr = []  # create list for output to file
                    parameter = input.split("(", 1)[1]  # remove first paranthesis
                    parameter = parameter[:-1]  # remove last parenthesis
                    counter = parameter.count(",")  # count number of arguments
                    for i in range(counter + 1):
                        output_arr.append(parameter.split(",")[i].lstrip())  # import arguments for printing
                        if "\"" == output_arr[i][0] or "\'" == output_arr[i][0]:
                            output_arr[i] = output_arr[i][1:-1]
                    table.write("\n")
                    table.write(" | ".join(output_arr))  # output the array to a file
                    print("1 new record inserted.")
        else:
            print(f"Table {table_name} does not exist...")
    except IndexError:
        print("ERROR: No table name specified. Please try again.")

# Update Command # 
# Changes the values of pre-existing tuples in the table. 
def update_command(input):
    try:
        check_current_scope()  # update current directory
        table_name = re.split("UPDATE ", input, flags=re.IGNORECASE)[1]  # collect table name
        table_name = re.split("SET", table_name, flags=re.IGNORECASE)[0].lower().strip() # collect attribute to change
        file_name = os.path.join(current_directory, table_name) # add name to path

        if not os.path.isfile(file_name): # if path doesnt exist
            print(f"Table {table_name} does not exist...")
        else:
            with open(file_name, "r+") as table_to_read: # open table to read
                data_to_read = table_to_read.readlines() # split file into array of lines
                parameter_to_update = re.split("WHERE ", input, flags=re.IGNORECASE)[1] # parameter to compare
                parameter = re.split("SET ", input, flags=re.IGNORECASE)[1] # value to change parameter to 
                parameter = re.split("WHERE ", parameter, flags=re.IGNORECASE)[0] # condition in where statement
                record_count, output = where(parameter_to_update, "update", data_to_read, parameter) # call to WHERE() 
                table_to_read.seek(0) # get current location in file
                table_to_read.truncate() 
                for line in output:
                    if not "\n" in line: #
                        line += "\n"
                    table_to_read.write(line)
                if record_count > 0: # terminal output
                    print(f"{record_count} records modified.")
                else:
                    print("No records modified.")
    except IndexError:
        print(f"ERROR: Invalid input. Table name not specified. ")

# Where Function #
# Very important. Makes comparisions of table data and command parameters = and >. Called by numerous functions to traverse table. 
def where(search_arguments, action, data_to_find, value_to_update = ""):
    attribute_counter = 0
    column_index = data_to_find[0].split(" | ") # split columns of data
    for x in range(len(column_index)): # for rows
        column_index[x] = column_index[x].split(" ")[0] # split by spaces, pick first index
    attribute_name = column_index
    input_data = list(data_to_find)
    output = [] # array to append and output
    flag_to_raise = 0

    # Case that parameter is being compared with inequality
    if "=" in search_arguments:
        if "!=" in search_arguments: # if not equal
            right_column = search_arguments.split(" !=")[0] # collect arg
            flag_to_raise = 1
        else:
            right_column = search_arguments.split(" =")[0] # collect arg 
        search_arg = search_arguments.split("= ")[1]
        if "\"" in search_arg or "\'" in search_arg: #gets rid of \n or \r
            search_arg = search_arg[1:-1]

        for line in data_to_find: # iterate lines
            line_test = line.split(" | ") # split by vertical lines
            for x in range(len(line_test)):  # Check that each column has an item
                line_test[x] = line_test[x].split(" ")[0] # split and 1st index

            if search_arg in line_test: #if matched
                column_index = attribute_name.index(right_column) 
                line_index = line_test.index(search_arg)
                if line_index == column_index:  #double check if matched field is correct field
                    # Case that we are deleting object WHERE __
                    if action == "delete": 
                        del input_data[input_data.index(line)]  # Remove matching field
                        output = input_data
                        attribute_counter += 1
                    # Case that we are selecting object WHERE __
                    if action == "select":
                        output.append(input_data[input_data.index(line)]) # append output array with selected data
                    # Case that we are updated object WHERE __
                    if action == "update":
                        attribute, field = value_to_update.split(" = ")
                        if attribute in attribute_name:
                            sep_line = line.split(" | ")
                            for x in range(len(sep_line)):  # check if column is empty
                                sep_line[x] = sep_line[x].split(" ")[0] # separate and get 1st index
                            sep_line[attribute_name.index(attribute)] = field.strip().strip("'") # strip quotes from command line
                            input_data[input_data.index(line)] = ' | '.join(sep_line) # print cleanly
                            output = input_data
                            attribute_counter += 1 # count number of records modified

    # Case that parameter is greater than some value
    elif ">" in search_arguments:  # Evaluate operator
        right_column = search_arguments.split(" >")[0] # param to compare
        search_arguments = search_arguments.split("> ")[1] # value to compare
        for line in data_to_find: # iterates lines in table
            line_test = line.split(" | ")
            for x in range(len(line_test)):  # Evaluate each column item
                line_test[x] = line_test[x].split(" ")[0]
                try:
                    line_test[x] = float(line_test[x])  # Check numeric values
                    if line_test[x] > float(search_arguments):  # make 'greater than' comparison
                        temp_column = column_index.index(right_column) # retrieve index of column
                        if x == temp_column: # 
                            if action == "delete":
                                del input_data[input_data.index(line)] 
                                output = input_data
                                attribute_counter += 1 # num of records to print
                            if action == "select":
                                output.append(input_data[input_data.index(line)])
                            if action == "update":
                                print("Update has been called.")
                except ValueError: # case of parameter titles on first row
                    continue
    if flag_to_raise: 
        output = list(set(data_to_find) - set(output))
    return attribute_counter, output

# Delete Command #
# Deletes specific tuples from specified table in command. 
def delete_command(input):
    try:
        check_current_scope() # update current directory
        table_name = re.split("DELETE FROM ", input, flags=re.IGNORECASE)[1]  # retrieve table name from command
        table_name = table_name.split(" ")[0].lower()
        file_name = os.path.join(current_directory, table_name) # add name to path
        if not os.path.isfile(file_name): # edge case
            print(f"Table {table_name} does not exist...")
        else:
            with open(file_name, "r+") as table_to_read: # open table to read
                data_to_read = table_to_read.readlines() # split into array of lines
                delete_item = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                attribute_counter, output = where(delete_item, "delete", data_to_read)
                table_to_read.seek(0) # set current position in file
                table_to_read.truncate() # clean input data
                for line_to_read in output:
                    table_to_read.write(line_to_read) 
                if attribute_counter > 0: # terminal output
                    print(f"{attribute_counter} records deleted.")
                else:
                    print(f"Zero records deleted.")
    except IndexError:
        print("ERROR: Invalid input. No table name specified. ")

def get_column(data):
    column_index = data[0].split(" | ")
    column_index = data.split(" | ")
    for x in range(len(column_index)):
        column_index[x] = column_index[x].split(" ")[0]

    return column_index

def separate(line):
    line_tester = line.split(" | ")
    for x in range(len(line_tester)):  # Check that each column has an item
        line_tester[x] = line_tester[x].split(" ")[0]
    return line_tester

# funtion for inner and outer join
def join_where(search_item, data_array, location = 'inner'):

    counter = 0
    out = []
    flag_to_raise = 0
    num_tables = len(data_array)
    matched_data = []
    empty_cols = ""

    #collect column data in array
    #check if column data matches

    if "=" in search_item:  # Evaluate operator
        if "!=" in search_item:
            r_col = search_item.split(" !=")[0]
        else:
            left_search = search_item.split(" =")[0]
            left_search = left_search.split(".")[1]

        right_search = search_item.split("= ")[1]
        right_search = right_search.split(".")[1]


    if num_tables == 2:
        left_table = data_array[0]
        right_table = data_array[1]
    else:
        print("Error: Invalid Input.")
        return -1, -1

    left_data = []
    right_data = []

    left_column = get_column(left_table[0])
    right_column = get_column(right_table[0])

    for line in left_table:
    #if not left_search in line:
        #print line
        line_seperated = separate(line)
        left_data.append(line_seperated[left_column.index(left_search)])


    for line in right_table:
        line_seperated = separate(line)
        right_data.append(line_seperated[right_column.index(right_search)])

    #both inner and out joins start with matching data
    for x in range(len(left_data)):
        for y in range(len(right_data)):
            if left_data[x] == right_data[y]:
                right_table[y] = right_table[y].strip('\n')
                out.append(right_table[y] + ' | ' + left_table[x])
                counter += 1

                if location == 'left':
                    matched_data.append(left_table[x])

    if location == 'left':
        number_of_data = len(right_column)

        for x in range(number_of_data):
            empty_cols += ' | '

        for x in range(len(left_data)):
            if not left_column[0] in left_table[x]: #remove the table key

                if not left_table[x] in matched_data: #dont run unless no matches with this data
                    out.append(left_table[x].strip('\n') + empty_cols )
                    counter += 1

    return counter, out


## Run all code ##
if __name__ == '__main__':
    main()