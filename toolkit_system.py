import sys
import inspect

# exit_with_line_info() is enhanced option of exit()
# When something went wrong and an exit was triggered
# the following info is useful:
# In which module and in which code line was this exit?
def exit_with_line_info(message=""):
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back
    path_n_file_name = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno

    # we need only the file name without the path:
    pos = len(path_n_file_name)
    while path_n_file_name[(pos-1)] != '\\':
        pos -= 1
    file_name = path_n_file_name[pos:]

    print("---------------------------------")
    exit_message = f"Exit at {file_name}, line {line_number}: {message}"
    sys.exit(exit_message)


# dev_print(msg) is an enhanced option of print(msg) during
# code development: It prints a message including the info,
# in which module and in which code line this print command
# was triggered:
def dev_print(message=""):
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back
    path_n_file_name = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno

    # we need only the file name without the path:
    pos = len(path_n_file_name)
    while path_n_file_name[(pos-1)] != '\\':
        pos -= 1
    file_name = path_n_file_name[pos:-3] # file name without ending '.py'

    # print the development message:
    dev_message = f"DEV MSG ({file_name},{line_number}): {message}"
    print(dev_message)