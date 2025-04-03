# Standard packages:
# import os

# Additional packages (have to be installed):
import openpyxl
# import xlsxwriter

# Project files:
from toolkit_system import exit_with_line_info, dev_print
# from json_parser import json_parser
# from convert_arguments import dict_pool_arguments


def read_new_categories_from_xls(xls_path_name, xls_file_name, xls_sheet_name) -> dict:

    # Open the Excel file:
    try:
        workbook = openpyxl.load_workbook(xls_path_name + xls_file_name)
    except OSError as e:
        exit_with_line_info("Could not open '" + xls_path_name + xls_file_name + "' ")

    # Open the sheet in the Excel file:
    worksheet = workbook[xls_sheet_name]

    # Initialize the dictionary
    result_dict = {}

    # Lets monitore if a Code (in column 0) is used more than once:
    check_duplicates = []

    # Read the needed rows in the Excel;
    # - there is a title row. So data starts in row 2 --> 'min_row'
    # - Needed data is in column 0 and column 2 --> 'min_col' and 'max_col'
    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=3, values_only=True):

        key = row[0]    # in column 0 is the code we use as key
        value = row[2]  # in column 2 is the category name

        if key is not None:
            if key not in check_duplicates:

                # Add a new pair to the dictionary:
                result_dict[key] = value
                check_duplicates.append(key)
            else:
                #  Exit wih error message because key exists twice
                dev_print("Key = '" + key + "' exists twice:")
                dev_print("--> First  value = '" + result_dict.get(key) + "'")
                dev_print("--> Second value = '" + value + "'")
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
    pepe_dict = read_new_categories_from_xls('input-files/new-category-names/','DLE-2024-new-category-names.xlsx', 'Kategorie-Namen')
    dev_print(pepe_dict.keys())