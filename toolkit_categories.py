# Standard packages:
# ---

# Additional packages (have to be installed):
import openpyxl  # read Excel files

# Project files:
from toolkit_system import exit_with_line_info, dev_print


def read_new_categories_from_xls(xls_path_name, xls_file_name, xls_sheet_name) -> dict:

    # Open the Excel file:
    try:
        workbook = openpyxl.load_workbook(xls_path_name + xls_file_name)
    except:
        exit_with_line_info("Could not open '" + xls_path_name + xls_file_name + "' ")

    # Open the sheet in the Excel file:
    try:
        worksheet = workbook[xls_sheet_name]
    except:
        exit_with_line_info("Could not open Excel worksheet '" + xls_sheet_name + "'. Please check the correct name.")

    # Initialize the dictionary
    result_dict = {}

    # Lets monitore if a Code (in column 1) is used more than once:
    check_duplicates = []

    # Read the needed rows in the Excel;
    # - there is a title row. So data starts in row 2 --> 'min_row'
    # - Needed data is in column 1 and column 3 --> 'min_col' and 'max_col'
    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=4, values_only=True):

        key = row[1]    # in column 1 is the code we use as key
        value = row[3]  # in column 3 is the category name

        if key is not None:
            if key not in check_duplicates:

                # Add a new pair to the dictionary:
                result_dict[key] = value
                check_duplicates.append(key)
            else:
                #  Exit wih error message because key exists twice
                dev_print("Key = '" + key + "' exists twice:  <--- check this key")
                if result_dict.get(key) is not None:
                    dev_print("--> First  value = '" + result_dict.get(key) + "'")
                else:
                    dev_print("--> First  value = None")
                if value is not None:
                    dev_print("--> Second value = '" + value + "'")
                else:
                    dev_print("--> Second value = None")
                dev_print("worksheet.max_row = " + str(worksheet.max_row) + " <--- check, if correct")
                exit_with_line_info("Duplicates in column 0 in worksheet '" + xls_sheet_name + "' in file '" + xls_file_name + "'")
        else:
            if value is not None:
                #  Exit wih error message because of invalid pair of code and category name
                dev_print("key = None; value = '" + value + "'")
                exit_with_line_info("Value in column 2 without key in column 0 in worksheet '" + xls_sheet_name + "' in file '" + xls_file_name + "'")

    # Return a dictionary with all codes and category names
    return result_dict


if __name__ == '__main__':

    dev_print("Pepe's Test")
    pepe_dict = read_new_categories_from_xls('input-files/new-category-names/','new-category-names.xlsx', 'DLA-2024')
    dev_print(pepe_dict.keys())