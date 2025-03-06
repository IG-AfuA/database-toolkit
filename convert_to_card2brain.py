# Mat says:
# This code needs major cleanup before it can be merged

from json_parser import json_parser as json_parser2007, latex_to_utf8, latex_to_utf8_subsuperscript, to_card2brain, extract_image
from json_parser_DLEDLA2024 import json_parser as json_parser2024

import img_tk
import xlsxwriter
import shutil
import re
import random
import itertools
import math
import os

# values of QUESTION_POOL
DLE2006 = 0
DLA2007 = 1
DLE2024 = 2
DLA2024 = 3

# The name of the question pool as String is used for:
# -- path name
# -- info in the Excel in the field 'Ergänzung A'
names_of_question_pools = {
    DLE2006: 'DLE-2006',
    DLA2007: 'DLA-2007',
    DLE2024: 'DLE-2024',
    DLA2024: 'DLA-2024'
}

# DECIDE BEFORE RUNNING THE TOOL:
# QUESTION_POOL = DLE2006
QUESTION_POOL = DLA2007
# QUESTION_POOL = DLE2024
# QUESTION_POOL = DLA2024

QUESTION_POOL_NAME = names_of_question_pools.get(QUESTION_POOL, 'ERROR-POOL-UNKNOWN')

# CHECK BEFORE RUNNING THE TOOL:
# These paths must exist in ur project folder:
# 1)
IMG_BASE_PATH = 'afu-group-trainer/frontend/static/img/'
#
# 2) Path and ttf-font:
#    library/fonts/dejavu-sans-fonts/DejaVuSans.ttf
#    (needed by img_tk.py)

# The name of the folder for the output data can be
# chosen freely. It is created in the project folder.
OUTPUT_FILE_PATH = 'output-files/Card2Brain_' + QUESTION_POOL_NAME + '/'

# The name of the Excel file can be chosen freely.
OUTPUT_XLSX_FILE_NAME = "xlsx-for-c2b-import.xlsx"

# DO NOT CHANGE. Card2Brain needs exactly this subfolder with exact this name.
OUTPUT_IMG_PATH = OUTPUT_FILE_PATH + 'media/images/'

# Checking whether the folder path with all the required subfolders
# already exists. If not, it will be created.
if not os.path.exists(OUTPUT_IMG_PATH):
    try:
        os.makedirs(OUTPUT_IMG_PATH)
    except OSError as e:
        print(f"Fehler beim Erstellen des Ordnerpfads: {e}")

# Labels for those answers with pictures or math formulas:
LABELS = ('Œ','Ø','][','@')

# Multiple choice test with ... answers per question:
ANSWERS_PER_QUESTION = 4

# Generate a list of all possible tuple combinations:
PERMUTATIONS = [i for i in itertools.permutations(range(ANSWERS_PER_QUESTION))]

# Open the Excel file in the output file folder:
workbook = xlsxwriter.Workbook(OUTPUT_FILE_PATH + OUTPUT_XLSX_FILE_NAME)

# Open a worksheet in the Excel file:
worksheet = workbook.add_worksheet('Fragen')

# Write row[0], the title row, in the worksheet of the Excel file:
title=('Id','Stapel','','Frage-Typ','Frage','Antwort','Instruction','Ergänzung F','Phonetics F','Beispielsatz F','Audio F','Bild F','Ergänzung A','Phonetics A','Beispielsatz A','Audio A','Bild A','MCA1 Correct','MCA1 Text','MCA2 Correct','MCA2 Text','MCA3 Correct','MCA3 Text','MCA4 Correct','MCA4 Text','MCA5 Correct','MCA5 Text','Copyright Image F','Copyright Image A','Copyright Audio F','Copyright Audio A')
title_format = workbook.add_format({'bold': True})
worksheet.write_row(0, 0, title, title_format)

# ?
image_tag = r'<img src="([^"]*)">'


def shuffle(items, permutation):
    # Set the order in the delivered tuple according to the
    # order in PERMUTATIONS[permutation].
    # If this function is repeatedly delivered with different 'items'
    # but identical 'permutation', the order will be changed identically each time.
    return tuple(items[p] for p in PERMUTATIONS[permutation])


def export(questions, pool):
    for i,q in enumerate(questions):
#       if q.question_id != 'TA204': continue
#       if q.question_id != 'TF505': continue
#       if q.question_id != 'TH405': continue
#       if q.question_id != 'TC505': continue

        # Card2Brain only allows plain-text answers. Thus, we have to implement
        # a quirk when answers contain math or images. In this case, answers
        # are integrated in to the question and prefixed with "A" to "D". This
        # looks weird when Card2Brain shuffles answers since "A" to "D" appears
        # in a strange order. We therefore only want to do that if necessary.

        math_img_quirk = False
        question_text, question_image = extract_image(q.question_text)


        # If an image was embedded in the middle of the question text,
        # then there was usually a <br> tag before and after it, which now has to be removed:
        question_text = re.sub(r'<br><br>', ' ', question_text)

        if question_image is not None:
            new_question_image = re.sub(r'/', '_', question_image)
            shutil.copyfile(IMG_BASE_PATH + question_image, OUTPUT_IMG_PATH + new_question_image)
        else:
            new_question_image = ''

        # Define a randomized order for the answers
        # and change then the order in an identical manner for answers and solutions:
        permutation_answers = random.randrange(math.factorial(ANSWERS_PER_QUESTION))
        answers_new_order = shuffle((q.answer_0, q.answer_1, q.answer_2, q.answer_3), permutation_answers)
        solutions_new_order = shuffle(('x','','',''), permutation_answers)

        # Change the order for the labels but use a different randomized order
        # (otherwise allways the same label is the correct answer).
        permutation_labels = random.randrange(math.factorial(ANSWERS_PER_QUESTION))
        labels_new_order = shuffle(LABELS, permutation_labels)

        if '<img ' in q.answer_0:
            # assert(question_image is None) #FIXME Weshalb dieser Assert, der bei Prüfungsfrage TC515 auslöst?
            math_img_quirk = True
            image_col = []
            for label,answer in zip(labels_new_order,answers_new_order):
                image_row = [img_tk.render_text(label),]
                image_tags = re.findall(image_tag, answer)
                assert(len(image_tags) == 1)
                match = re.search(image_tag, answer)
                prefix = answer[:match.start()]
                postfix = answer[match.end():]
                image_row.append(img_tk.render_text(prefix))
                image_row.append(img_tk.load(IMG_BASE_PATH+image_tags[0]))
                image_row.append(img_tk.render_text(postfix))
                image_col.append(img_tk.tile_images_horizontally(image_row))

            answer_image = img_tk.tile_images_vertically(image_col)
            new_question_image = f'{pool}_{q.question_id}_a_stacked.png'
            #print(new_question_image)
            answer_image.save(OUTPUT_IMG_PATH + f'{new_question_image}')
        elif '<span class="math-tex">' in q.answer_0 or '<span class="math-tex">' in q.answer_1 or '<span class="math-tex">' in q.answer_2 or '<span class="math-tex">' in q.answer_3:
            math_img_quirk = True
            for a1, a2 in zip(labels_new_order, answers_new_order):
                question_text += '<br><br>'
                question_text += f'<strong>{a1}:</strong> {a2}'

        #FIXME Workaround for bug 'Question string starts or ends with '<br>'
        if question_text[0] == '<' and question_text[1] == 'b' and question_text[2] == 'r' and question_text[3] == '>':
            question_text = question_text[4:]
        if question_text[-4] == '<' and question_text[-3] == 'b' and question_text[-2] == 'r' and question_text[-1] == '>':
            question_text = question_text[:-4]

        # for field 'Ergänzung Antwort' in the XLSX file:
        info_question_id = '(Frage-ID: ' + QUESTION_POOL_NAME + '-' + q.question_id + ')'

        # writing a row in the xlsx-file:
        if math_img_quirk:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],labels_new_order[0],solutions_new_order[1],labels_new_order[1],solutions_new_order[2],labels_new_order[2],solutions_new_order[3],labels_new_order[3],'','','','','',''])
        else:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],answers_new_order[0],solutions_new_order[1],answers_new_order[1],solutions_new_order[2],answers_new_order[2],solutions_new_order[3],answers_new_order[3],'','','','','',''])

if QUESTION_POOL == DLE2006 or QUESTION_POOL == DLA2007:
    qp = json_parser2007()
    qp.attach_text_processor(latex_to_utf8)
    qp.attach_text_processor(latex_to_utf8_subsuperscript)
    qp.attach_text_processor(to_card2brain)
    if QUESTION_POOL == DLE2006:
        export(qp.novice_questions(), 'HB3')
    else:  # QUESTION_POOL == DLA2007
        export(qp.cept_questions(), 'HB9')

elif QUESTION_POOL == DLE2024 or QUESTION_POOL == DLA2024:
    qp = json_parser2024()
    #FIXME

else:
    assert True

workbook.close()

print('-----------------')
print('The output data is stored in this path:')
print('  ' + OUTPUT_FILE_PATH)
print('-----------------')