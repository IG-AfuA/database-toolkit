# Mat says:
# FIXME This code needs major cleanup before it can be merged.

# Usage: python convert_to_card2brain [-?] [-e06] [-a07] [-e24] [-a24] [-beta|-math]
# Parameters '-beta' and '-math' is only for beta testing
# For more info, use parameter '-?'

# Check before running the tool:
# Following file paths must exist in your project folder;
# a) always: /library/fonts/dejavu-sans-fonts/DejaVuSans.ttf
# b) for DLE2006 and DLA2007: /input-files/afu-group-trainer/... with the files
# c) for DLE2024 and DLA2024: /input-files/50ohm-pocket-main/... with the files
#
# The output files will be placed in a file folder named
# /output-files/ in your project folder.

# Standard packages:
import shutil
import re
import random
import itertools
import math
import os
import sys

# Additional packages (have to be installed):
import xlsxwriter

# Project files:
from json_parser import latex_to_utf8, latex_to_utf8_subsuperscript, to_card2brain, extract_image, math_signs_much_less_n_much_greater, remove_flaws_coming_from_json_source
     #FIXME Issue #12
from json_parser import json_parser as json_parser2007 # Parser for DLE2006 and DLA2007
from json_parser_DLEDLA2024 import json_parser as json_parser2024 # Parser for DLE2024 and DLA2024
import img_tk # Toolkit for the images (embed labels to images, stacking of images, ...)
import question_pool_tools as pool_tk


def shuffle(items, permutation):
    # Set the order in the delivered tuple according to the
    # order in PERMUTATIONS[permutation].
    # If this function is repeatedly delivered with different 'items'
    # but identical 'permutation', the order will be changed identically each time.
    return tuple(items[p] for p in PERMUTATIONS[permutation])

def export(questions, pool : str):

    # for i,q in enumerate(questions):
    xmlx_row =  0
    steps_of_100 = list(range(100, 2000, 100))
    for i,q in enumerate(questions):

        # print progress in steps of 100 converted and exported questions:
        if i in steps_of_100:
            print ('FYI: already ' + str(i) + ' questions checked and still running ...')

        if "-beta" in sys.argv:
            if not pool_tk.beta_test_exam_questions(q.question_id):
                continue

        # Card2Brain only allows plain-text answers. Thus, we have to implement
        # a quirk when answers contain math or images. In this case, answers
        # are integrated in to the question and prefixed with "A" to "D". This
        # looks weird when Card2Brain shuffles answers since "A" to "D" appears
        # in a strange order. We therefore only want to do that if necessary.

        # --- BEGIN export ---

        # Define a randomized order for the answers
        # and change then the order in an identical manner for answers and solutions:
        permutation_answers = random.randrange(math.factorial(ANSWERS_PER_QUESTION))
        answers_new_order = shuffle((q.answer_0, q.answer_1, q.answer_2, q.answer_3), permutation_answers)
        solutions_new_order = shuffle(('x','','',''), permutation_answers)

        # Change the order for the labels but use a different randomized order
        # (otherwise always the same label is the correct answer).
        permutation_labels = random.randrange(math.factorial(ANSWERS_PER_QUESTION))
        labels_new_order = shuffle(LABELS, permutation_labels)

        math_or_image_in_answer = False # info needed wenn writing a row in Excel sheet
        count_images = 0    # In case we have more than one image, we have to group them one image.
        image_col = []      # needed for grouping images

        question_text, question_images = extract_image(q.question_text)

        if question_images is not None:
            # If an image was embedded in the middle of the question text
            # then there was usually a <br> tag before and after it, which now has to be removed:
            question_text = re.sub(r'<br><br>', ' ', question_text)

            # If an image was embedded before or after the question text
            # then there was usually a <br> between image and text,
            # which now has to be removed:
            #FIXME Das geht eleganter
            if question_text[0] == '<' and question_text[1] == 'b' and question_text[2] == 'r' and question_text[3] == '>':
                question_text = question_text[4:]
            if question_text[-4] == '<' and question_text[-3] == 'b' and question_text[-2] == 'r' and question_text[-1] == '>':
                question_text = question_text[:-4]

        if question_images is None:
            new_question_image = ''

        elif len(question_images) == 1:
            # print('Pos. C2B l.103: 1 q-image at ' + q.question_id) #FIXME
            count_images += 1
            new_question_image = re.sub(r'/', '_', question_images[0])
            # and now wait if further images will be added from the answers.
            # Only then decide whether the image should remain unchanged or grouped.

        else: # len(question_images) > 1:
            # print('Pos. C2B l.110: >1 q-images at ' + q.question_id + 'len=' + len(question_images))  # FIXME
            count_images += len(question_images)
            new_question_image = re.sub(r'/', '_', question_images[0])
            for img_nr in range(len(question_images)):
                image_col.append(img_tk.load(IMG_BASE_PATH+question_images[img_nr]))

        # ---------------

        if '<img ' in q.answer_0:
            # if statement only checks answer_0 because either all four or none of the four
            # answer options each consist of one image.

            # if there is also 1 (one!) question image, it is now the time, to append it:
            if count_images == 1:
                # print('Pos. C2B l.124: 1 q-image attached to  row for ' + q.question_id)  # FIXME
                new_question_image = re.sub(r'/', '_', question_images[0])
                image_col.append(img_tk.load(IMG_BASE_PATH + question_images[0]))

            # answer options each consist of one image:
            math_or_image_in_answer = True
            count_images += 4

            # Separator between question (text with/without images) and answer options:
            image_col.append(img_tk.render_text('Vorgeschlagene Antworten:'))

            # grouping all infos to one picture
            for label,answer in zip(labels_new_order,answers_new_order):
                image_row = [img_tk.render_text(label),]
                image_tags = re.findall(image_tag, answer)
                assert(len(image_tags) == 1) # check if allways one image per answer option
                match = re.search(image_tag, answer)
                prefix = answer[:match.start()]
                postfix = answer[match.end():]
                image_row.append(img_tk.render_text(prefix))
                image_row.append(img_tk.load(IMG_BASE_PATH+image_tags[0]))
                image_row.append(img_tk.render_text(postfix))
                image_col.append(img_tk.tile_images_horizontally(image_row))

            answer_image = img_tk.tile_images_vertically(image_col)
            new_question_image = f'{pool}_{q.question_id}_a_stacked.png'
            answer_image.save(OUTPUT_IMG_PATH + f'{new_question_image}')

        else: # No pictures in answers

            if count_images == 1:
                new_question_image = re.sub(r'/', '_', question_images[0])
                shutil.copyfile(IMG_BASE_PATH + question_images[0], OUTPUT_IMG_PATH + new_question_image)
            elif count_images > 1:
                answer_image = img_tk.tile_images_vertically(image_col)
                new_question_image = f'{pool}_{q.question_id}_q_stacked.png'
                answer_image.save(OUTPUT_IMG_PATH + f'{new_question_image}')

            if '<span class="math-tex">' in q.answer_0 or '<span class="math-tex">' in q.answer_1 or '<span class="math-tex">' in q.answer_2 or '<span class="math-tex">' in q.answer_3:
                # The 4 answer variants have no images
                # but at least one answer option contains math-tex
                math_or_image_in_answer = True
                for a1, a2 in zip(labels_new_order, answers_new_order):
                    question_text += '<br><br>'
                    question_text += f'<strong>{a1}:</strong> {a2}'

        # End of: if '<img ' in q.answer_0: / else:

        # Text for field 'Ergänzung Antwort' in the XLSX file:
        info_question_id = '(Frage-ID: ' + pool_tk.dict_arguments.get(sys.argv[1]) + '-' + q.question_id + ')'

        # In case of parameter '-math' only export questions containing a LaTex term:
        if "-math" not in sys.argv or "<span" in question_text:
            xmlx_row += 1
            # write a row in the xlsx-file:
            if math_or_image_in_answer:
                worksheet.write_row(xmlx_row,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],labels_new_order[0],solutions_new_order[1],labels_new_order[1],solutions_new_order[2],labels_new_order[2],solutions_new_order[3],labels_new_order[3],'','','','','',''])
            else:
                worksheet.write_row(xmlx_row,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],answers_new_order[0],solutions_new_order[1],answers_new_order[1],solutions_new_order[2],answers_new_order[2],solutions_new_order[3],answers_new_order[3],'','','','','',''])

    # end of 'for q in questions'

    pool_tk.print_separation_line()
    print(str(xmlx_row) + " rows exported with parameter " + str(sys.argv[1:]))

# end of def export

# ----------------------------------------------------------
# End of def - main code starts
# ----------------------------------------------------------

#FIXME DEV modus # PEPE
if len(sys.argv) < 2:
    sys.argv.append('-a24')
    sys.argv.append('-beta')

# Checking command line arguments: Only expected arguments in the list?
pool_tk.check_arguments(sys.argv)

# Set the active-pool:
#FIXME Assumption: In the command line arguments we only accept one pool (and "-beta").
if pool_tk.dict_arguments.get(sys.argv[1]) == "-beta":
    pool_tk.set_active_pool(sys.argv[2])
else:
    pool_tk.set_active_pool(sys.argv[1])

if pool_tk.check_active_pool(['-e06','-a07']):      # Is it one of these two pools?
    img_tk.set_font_size(24)
    IMG_BASE_PATH = 'input-files/afu-group-trainer/frontend/static/img/'
elif pool_tk.check_active_pool(['-e24','-a24']):    # or is it one of these two pools?
    img_tk.set_font_size(36)
    IMG_BASE_PATH = 'input-files/50ohm-pocket_images-to-png-converted/'
else:
    pool_tk.print_separation_line()
    IMG_BASE_PATH = '*** question pool does not exist ***'
    print(IMG_BASE_PATH)
    pool_tk.print_separation_line()
    exit()

if not os.path.exists(IMG_BASE_PATH):
    pool_tk.print_separation_line()
    print ('*** path to input files does not exist ***')
    pool_tk.print_separation_line()
    exit()

# The name of the folder for the output data can be
# chosen freely. It is created in the project folder.
OUTPUT_FILE_PATH = 'output-files/Card2Brain_' + pool_tk.dict_arguments.get(sys.argv[1]) + '/'

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
        print(f"Error message was generated when creating the folder path: {e}")

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

#  Links of images in the JSON file have this character sequence:
image_tag = r'<img src="([^"]*)">'  # Regular Expression: https://www.w3schools.com/python/python_regex.asp

# Choose the correct parser
if '-e06' in sys.argv or '-a07' in sys.argv:
    qp = json_parser2007()
elif '-e24' in sys.argv or '-a24' in sys.argv:
    qp = json_parser2024()
    qp.attach_text_processor(remove_flaws_coming_from_json_source)
else:
    qp = json_parser2007()
    pool_tk.print_separation_line()
    print("Error with 'sys.argv' when choosing the parser")
    pool_tk.print_separation_line()
    assert False

# Parsing elements
qp.attach_text_processor(latex_to_utf8)
qp.attach_text_processor(latex_to_utf8_subsuperscript)
qp.attach_text_processor(to_card2brain)
if '-a07' in sys.argv:
    qp.attach_text_processor(math_signs_much_less_n_much_greater)

if '-e06' in sys.argv or '-e24' in sys.argv:
    export(qp.novice_questions(), 'HB3')
elif '-a07' in sys.argv or '-a24' in sys.argv:
        export(qp.cept_questions(), 'HB9')
else:
    pool_tk.print_separation_line()
    print("Error with 'sys.argv' when calling 'def export'")
    pool_tk.print_separation_line()
    assert False

workbook.close()

print('Excel file closed; export completed.')
print('The output data is stored in this path:')
print('  ' + OUTPUT_FILE_PATH)
pool_tk.print_separation_line()