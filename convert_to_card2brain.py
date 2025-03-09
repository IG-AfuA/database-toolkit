# Usage: python convert_to_card2brain [-e06] [-a07] [-e24] [-a24]
# For more details, see below in 'def print_arguments()'

# Check for running the tool:
# Following file paths must exist in your project folder;
# always: /library/fonts/dejavu-sans-fonts/DejaVuSans.ttf
# for DLE2006 and DLA2007: /input-files/afu-group-trainer/... with the files
# for DLE2024 and DLA2024: /input-files/50ohm-pocket-main/... with the files
#
# The output files will be placed in a file folder named
# /output-files/ in your project folder.


import sys
#FIXME DEV modus # PEPETEST
sys.argv.append('-e06')

# Mat says:
# This code needs major cleanup before it can be merged.

# Standard packages:
import shutil
import re
import random
import itertools
import math
import os
# import sys

# Additional packages (have to be installed):
import xlsxwriter

# Project files:
from json_parser import latex_to_utf8, latex_to_utf8_subsuperscript, to_card2brain, extract_image
     #FIXME Issue #12
from json_parser import json_parser as json_parser2007 # Parser for DLE2006 and DLA2007
from json_parser_DLEDLA2024 import json_parser as json_parser2024 # Parser for DLE2024 and DLA2024
import img_tk # Toolkit for the images (embed labels to images, stacking of images, ...)

# Dictionary of allowed command line arguments
# Values are needed for:
# -- part of file path names
# -- info in the Excel in the field 'Ergänzung A'
dict_arguments  = {
    "-e06":"DLE-2006",
    "-a07":"DLE-2007",
    "-e24":"DLE-2024",
    "-a24":"DLA-2024"
}

def print_arguments():
    print("Possible command line arguments are:")
    print("-e06: Export question pool year 2006 for Novice Licence from BNetzA Germany")
    print("-a07: Export question pool year 2007 for Advanced Licence from BNetzA Germany")
    print("-e24: Export question pool year 2024 for Novice Licence from BNetzA Germany")
    print("-a24: Export question pool year 2024 for Advanced Licence from BNetzA Germany")

def print_separation_line():
    print("--------------------------------")


def check_arguments():
    count_error = 0
    if len(sys.argv) < 2:
        # sys.argv[0] contains path and script name
        # arguments in sys.argv[1] and following
        print_separation_line()
        print("Please provide at least one command line argument.")
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()
    else:
        for string_element in sys.argv[1:]:
            if string_element in list(dict_arguments.keys()): #LIST_OF_ARGUMENTS:
                pass
            else:
                count_error += 1
                print_separation_line()
                print("Error: '" + string_element + "' is not a correct command line argument.")
    if count_error > 0:
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()

    # FIXME temporary restriction
    # source code can so far only handle one argument
    if len(sys.argv) > 2:
        print_separation_line()
        print("*** temporary restriction ***")
        print("Please provide with exact one argument")
        print_separation_line()
        print_arguments()
        print_separation_line()
        exit()

# '≪' and '≫' instead of '<<' and '>>'
def math_signs_much_less_and_much_greater(text: str):
    text = re.sub(r'<<','≪', text)
    text = re.sub(r'>>', '≫', text)
    return text

def shuffle(items, permutation):
    # Set the order in the delivered tuple according to the
    # order in PERMUTATIONS[permutation].
    # If this function is repeatedly delivered with different 'items'
    # but identical 'permutation', the order will be changed identically each time.
    return tuple(items[p] for p in PERMUTATIONS[permutation])

def export(questions, pool):
    for i,q in enumerate(questions):
#       if q.question_id != 'TA204': continue #FIXME # FRAGEPEPE
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
        # (otherwise always the same label is the correct answer).
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
        info_question_id = '(Frage-ID: ' + dict_arguments.get(sys.argv[1]) + '-' + q.question_id + ')'

        # writing a row in the xlsx-file:
        if math_img_quirk:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],labels_new_order[0],solutions_new_order[1],labels_new_order[1],solutions_new_order[2],labels_new_order[2],solutions_new_order[3],labels_new_order[3],'','','','','',''])
        else:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],answers_new_order[0],solutions_new_order[1],answers_new_order[1],solutions_new_order[2],answers_new_order[2],solutions_new_order[3],answers_new_order[3],'','','','','',''])
# end of def export

# ----------------------------------------------------------
# End of def - main code starts
# ----------------------------------------------------------

#
check_arguments()

if '-e06' in sys.argv or '-e07' in sys.argv:
    IMG_BASE_PATH = 'input-files/afu-group-trainer/frontend/static/img/'
elif 'e24' in sys.argv or '-a24' in sys.argv:
    IMG_BASE_PATH = 'input-files/50ohm-pocket-main/assets/svgs/'
else:
    print_separation_line()
    IMG_BASE_PATH = '*** question pool does not exist ***'
    print(IMG_BASE_PATH)
    print_separation_line()
    exit()

if not os.path.exists(IMG_BASE_PATH):
    print_separation_line()
    print ('*** path to input files does not exist ***')
    print_separation_line()
    exit()

# The name of the folder for the output data can be
# chosen freely. It is created in the project folder.
OUTPUT_FILE_PATH = 'output-files/Card2Brain_' + dict_arguments.get(sys.argv[1]) + '/'

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

#  Links to images in the JSON file have this character sequence:
image_tag = r'<img src="([^"]*)">'

if '-e06' in sys.argv or '-a07' in sys.argv:
    qp = json_parser2007()
    qp.attach_text_processor(latex_to_utf8)
    qp.attach_text_processor(latex_to_utf8_subsuperscript)
    qp.attach_text_processor(to_card2brain)
    if '-e06' in sys.argv:
        export(qp.novice_questions(), 'HB3')
    else:  # '-e24' in sys.argv
        export(qp.cept_questions(), 'HB9')

elif '-e24' in sys.argv or '-a24' in sys.argv:
    qp = json_parser2024()
    qp.attach_text_processor(latex_to_utf8)
    qp.attach_text_processor(latex_to_utf8_subsuperscript)
    qp.attach_text_processor(to_card2brain)
    if '-e24' in sys.argv:
        export(qp.novice_questions(), 'HB3')
    else:  # 'a24' in sys.argv
        export(qp.cept_questions(), 'HB9')
else:
    assert True
    exit()

workbook.close()

print('-----------------')
print('The output data is stored in this path:')
print('  ' + OUTPUT_FILE_PATH)
print('-----------------')