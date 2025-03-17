import sys
import inspect

def exit_with_line_info(message=""):
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back
    file_name = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno
    print("---------------------------------")
    exit_message = f"Exit at {file_name}, line {line_number}: {message}"
    sys.exit(exit_message)