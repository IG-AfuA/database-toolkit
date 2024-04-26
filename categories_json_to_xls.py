import json
import xlsxwriter
from collections import defaultdict

from json_parser import json_parser, eszett_to_ss

workbook = xlsxwriter.Workbook('Classmarker_Kategorien.xlsx')
worksheet = workbook.add_worksheet('Kategorien')

title = ('PK', 'ID', 'Name E', 'Name A', 'Name Neu')
title_format = workbook.add_format({'bold': True})
worksheet.write_row(0, 0, title, title_format)

classmarker_category_dict = {}

# Some categories are only present in one of the two question pools.
# We use defaultdict here to return an empty string on lookup when
# writing the output.
novice_category_dict = defaultdict(lambda: '')
cept_category_dict = defaultdict(lambda: '')

fh = open('all_categories.json')
categories = json.load(fh)
for category in categories['parent_categories']:
    classmarker_category_dict[category['parent_category_name']] = category['parent_category_id']

qp = json_parser()

i = 0
for q in qp.novice_questions():
    assert('D'+q.parent.category_id in classmarker_category_dict)
    novice_category_dict['D'+q.parent.category_id] = 'D'+q.category

for q in qp.cept_questions():
    assert('D'+q.parent.category_id in classmarker_category_dict)
    cept_category_dict['D'+q.parent.category_id] = 'D'+q.category

for category in classmarker_category_dict:
    if category not in novice_category_dict and category not in cept_category_dict:
        # Category unrelated to this import --> skip
        continue

    # Use text from novice TOC unless topic does not exist
    if category in novice_category_dict:
        new_text = eszett_to_ss(novice_category_dict[category])
    else:
        new_text = eszett_to_ss(cept_category_dict[category])

    worksheet.write_row(i+1,0,[classmarker_category_dict[category], category, novice_category_dict[category], cept_category_dict[category], new_text])
    i += 1

workbook.close()
