# Standard packages:
import os

# Additional packages (have to be installed):
import xlsxwriter
import openpyxl
# import pandas

# Project files:
from toolkit_system import exit_with_line_info, dev_print
# from json_parser import json_parser
# from convert_arguments import dict_pool_arguments


def read_new_categories_from_xls(xls_path_name, xls_file_name, xls_sheet_name) -> dict:

    # Open the Excel file:
    workbook = openpyxl.load_workbook(xls_path_name + xls_file_name)

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

""" === NOT IN USE ===

def write_categories_to_xls(qp, pool_argument):

    # Set path and file name #FIXME Issue N° 3
    OUTPUT_FILE_PATH = 'output-files/'
    OUTPUT_XLSX_FILE_NAME = 'replace-categories-in-' + str(dict_pool_arguments.get(pool_argument) + '.xlsx')

    # If folder path does not exist, it will be created.
    if not os.path.exists(OUTPUT_FILE_PATH):
        try:
            os.makedirs(OUTPUT_FILE_PATH)
        except OSError as e:
            print(f"Error message was generated when creating the folder path: {e}")
            exit_with_line_info("Could not generate path 'OUTPUT_FILE_PATH = " + OUTPUT_FILE_PATH)

    # Open the Excel file in the output file folder:
    workbook = xlsxwriter.Workbook(OUTPUT_FILE_PATH + 'LEERE_VORLAGE_'+ OUTPUT_XLSX_FILE_NAME)

    # Open first worksheet in the Excel file for a readme text:
    worksheet_readme = workbook.add_worksheet('README')
    title_format = workbook.add_format({'bold': True, })
    worksheet_readme.write_row(0, 0, ['INFO zu Spalte "Kategoriename NEU"'], title_format)
    worksheet_readme.write_row(1, 0, ['Lässt man in einer Zeile das Feld in Spalte "Kategorienname NEU" leer,'])
    worksheet_readme.write_row(2, 0, ['so wird diese Kategorie nicht exportiert.'])

    worksheet_readme.write_row(4, 0, ['TIPP: So kann man beim Fragenkatalog DLE-2024 die Vorschriften-'])
    worksheet_readme.write_row(5, 0, ['und Betriebstechnik-Fragen aussortieren.'])

    # Open second worksheet in the Excel file for the data:
    worksheet_data = workbook.add_worksheet('Kategorie-Namen')

    # Write row[0], the title row, in the worksheet of the Excel file:
    title = ('Hauptkategorie (Fragenkatalog)', 'Kategorie (Fragenkatalog)','Kategoriename NEU')
    title_format = workbook.add_format({'bold': True, })
    worksheet_data.write_row(0, 0, title, title_format)

    # Set the column widths
    worksheet_data.set_column('A:A', 30)
    worksheet_data.set_column('B:C', 50)

    if pool_argument in ['-e06', '-e24']:  # novice licence question pools
        pool = qp.novice_questions()
    elif pool_argument in ['-a07', '-a24']:  # cept licence question pools
        pool = qp.cept_questions()
    else:
        pool = None
        exit_with_line_info("active question pool is not mentioned in the lists in the code lines above.")

    # Sort the question pool by the question-id
    sorted_pool = sorted(pool, key=lambda x: x.question_id[1:])

    # Write the category names into the Excel file
    # but each category name only once.
    if pool_argument in ['-e06', '-a07']:  # old question pools from 2006/2007
        xlsx_row = 0
        categories_done = []
        for q in sorted_pool:
            if q.category not in categories_done:
                xlsx_row += 1
                categories_done.append(q.category)
                worksheet_data.write_row(xlsx_row, 0, ["---", q.category])
    elif pool_argument in ['-e24', '-a24']:  # new question pools from 2024
        xlsx_row = 0
        categories_done = []
        for q in sorted_pool:
            if q.question_id[0] in ['E','N']:
                if q.question_id[:-2] not in categories_done:
                    xlsx_row += 1
                    categories_done.append(q.question_id[:-2])
                    worksheet_data.write_row(xlsx_row, 0, [q.question_id[:-2], q.category, q.subcategory])

    else:
        exit_with_line_info("active question pool is not mentioned in the lists in the code lines above.")



    # Close the Excel file
    workbook.close()

    # Job is done
    print('/' + OUTPUT_FILE_PATH + OUTPUT_XLSX_FILE_NAME + ' created')

=== END OF 'NOT IN USE' === """


if __name__ == '__main__':

    pepe_dict = read_new_categories_from_xls('input-files/new-category-names/','DLE-2024-new-category-names.xlsx', 'Kategorie-Namen')

    dev_print("Pepe's Test")
    dev_print(pepe_dict.keys())