# Mat says:
# FIXME This code needs major cleanup before it can be merged.

# Usage: python convert_to_card2brain [-?] [-e06] [-a07] [-e24] [-a24] [-a] [-c] [-l] [-dfrac] [-beta|-math]
# Parameters '-beta' and '-math' is only for beta testing
# For more info, use parameter '-?'

# Check before running the tool:
# Following file paths must exist in your project folder;
# a) always:  /input-files/fonts/DejaVuSans.ttf
# b) for DLE2006 and DLA2007:  /input-files/afu-group-trainer/... with the files
# c) for DL-2024:  /input-files/50ohm-pocket/... with the files
# d) for DL-2024:  /input-files/50ohm-pocket__images-to-png-converted/ with the files
# e) when using parameter '-c': /input-files/new-category-names/new-category-names.xlsx
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
from json_parser import (latex_to_utf8, latex_to_utf8_subsuperscript, to_card2brain,
                         extract_image, math_signs_much_less_n_much_greater,
                         remove_flaws_coming_from_json_source, latex_frac_to_dfrac) # FIXME Issue #12
from json_parser import json_parser as json_parser2007 # Parser for DLE2006 and DLA2007
from json_parser_DLEDLA2024 import json_parser as json_parser2024 # Parser for DLE2024 and DLA2024
from convert_arguments import (read_out_arguments, list_scheduled_pools, set_active_pool,
                               dict_pool_arguments, beta_test_exam_questions, get_active_pool)
import toolkit_images as tk_img # Toolkit for the images (embed labels to images, stacking of images, ...)
from toolkit_system import exit_with_line_info, dev_print
from toolkit_categories import read_new_categories_from_xls


def shuffle(items, permutation):
    # Set the order in the delivered tuple according to the
    # order in PERMUTATIONS[permutation].
    # If this function is repeatedly delivered with different 'items'
    # but identical 'permutation', the order will be changed identically each time.
    return tuple(items[p] for p in PERMUTATIONS[permutation])

def export(questions, pool : str): #FIXME Parameter 'pool' is now longer used

    global xlsx_row

    # Sort the question pool by question_id
    sorted_questions = sorted(questions, key=lambda x: x.question_id)

    # for q in sorted_questions:
    rows_per_pool = 0
    for q in sorted_questions:

        # When parameter '-beta' then check if the question_id is
        # in the list of beta test question (in convert_arguments.py).
        # IF not, ignore this question and go on with next question.
        if "-beta" in sys.argv:
            if not beta_test_exam_questions(q.question_id):
                continue

        # Card2Brain only allows plain-text answers. Thus, we have to implement
        # a quirk when answers contain math or images. In this case, answers
        # are integrated in to the question and prefixed with "A" to "D". This
        # looks weird when Card2Brain shuffles answers since "A" to "D" appears
        # in a strange order. We therefore only want to do that if necessary.

        # --- BEGIN with preparing the export ---

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
            #FIXME Geht das  auch eleganter? @Mats
            if question_text[0] == '<' and question_text[1] == 'b' and question_text[2] == 'r' and question_text[3] == '>':
                question_text = question_text[4:]
            if question_text[-4] == '<' and question_text[-3] == 'b' and question_text[-2] == 'r' and question_text[-1] == '>':
                question_text = question_text[:-4]

        if question_images is None:
            new_question_image = ''

        elif len(question_images) == 1:
            count_images += 1
            new_question_image = re.sub(r'/', '_', question_images[0])
            # and now wait if further images will be added from the answers.
            # Only then decide whether the image should remain unchanged or grouped.

        else: # len(question_images) > 1:
            count_images += len(question_images)
            new_question_image = re.sub(r'/', '_', question_images[0])
            for img_nr in range(len(question_images)):
                image_col.append(tk_img.load(IMG_BASE_PATH+question_images[img_nr]))

        # End of: if question_images ... / elif len(question_images) ...

        if '<img ' in q.answer_0:
            # if statement only checks answer_0 because either all four or none of the four
            # answer options each consist of one image.

            # if there is also 1 (one!) question image, it is now the time, to append it:
            if count_images == 1:
                image_col.append(tk_img.load(IMG_BASE_PATH + question_images[0]))

            # answer options each consist of one image:
            math_or_image_in_answer = True
            count_images += 4

            # Separator between question (text with/without images) and answer options:
            image_col.append(tk_img.render_text('Vorgeschlagene Antworten:'))

            # grouping all infos to one picture
            for label,answer in zip(labels_new_order,answers_new_order):
                image_row = [tk_img.render_text(label),]
                image_tags = re.findall(image_tag, answer)
                assert(len(image_tags) == 1) # check if allways one image per answer option
                match = re.search(image_tag, answer)
                prefix = answer[:match.start()]
                postfix = answer[match.end():]
                image_row.append(tk_img.render_text(prefix))
                image_row.append(tk_img.load(IMG_BASE_PATH+image_tags[0]))
                image_row.append(tk_img.render_text(postfix))
                image_col.append(tk_img.tile_images_horizontally(image_row))

            answer_image = tk_img.tile_images_vertically(image_col)
            new_question_image = f'{q.question_id}_a_stacked.png'
            new_question_image = dict_pool_arguments.get(get_active_pool()) + "_" + new_question_image
            answer_image.save(OUTPUT_IMG_PATH + f'{new_question_image}')

        else: # No pictures in answers

            if count_images == 1:
                new_question_image = re.sub(r'/', '_', question_images[0])
                new_question_image = dict_pool_arguments.get(get_active_pool()) + "_" + new_question_image
                shutil.copyfile(IMG_BASE_PATH + question_images[0], OUTPUT_IMG_PATH + new_question_image)
            elif count_images > 1:
                answer_image = tk_img.tile_images_vertically(image_col)
                new_question_image = f'{q.question_id}_q_stacked.png'
                new_question_image = dict_pool_arguments.get(get_active_pool()) + "_" + new_question_image
                answer_image.save(OUTPUT_IMG_PATH + f'{new_question_image}')

            if '<span class="math-tex">' in q.answer_0 or '<span class="math-tex">' in q.answer_1 or '<span class="math-tex">' in q.answer_2 or '<span class="math-tex">' in q.answer_3:
                # The 4 answer variants have no images
                # but at least one answer option contains math-tex
                math_or_image_in_answer = True
                for a1, a2 in zip(labels_new_order, answers_new_order):
                    question_text += '<br><br>'
                    question_text += f'<strong>{a1}:</strong>&nbsp;&nbsp;&nbsp;{a2}' # 3 spaces between label and text are intentional

        # End of: if '<img ' in q.answer_0: / else:

        # In case of parameter '-math' only export questions containing a LaTex term:

        # Normally every question shall be exported:
        export_this_question = True

        # With command line parameter '-math' export
        # only question with a html tag for latex terms
        if '-math' in sys.argv:
            if '<span' not in question_text:
                export_this_question =  False

        # Don't export exam question when not in chapter 'Technische Kenntnisse'
        if '-e24' == get_active_pool():
            # Of the sources currently used for exam questions, only the DLE-2004 question pool
            # contains questions on regulations and operating, which now need to be sorted out.
            if q.question_id[0] in ['V', 'B']:
                # V = exam question in chapter 'Vorschriften'
                # B = exam question in chapter 'Betriebstechnik'
                export_this_question = False

        if export_this_question:
            xlsx_row += 1       # row in the Excel file, needed for the writing into the Excel file
            rows_per_pool += 1  # count for each question pool separately; needed just as info

            # Text for field 'Ergänzung Antwort' in the XLSX file:
            info_question_id = '(Frage-ID: ' + dict_pool_arguments.get(get_active_pool()) + '-' + q.question_id + ')'

            # Category name - and sorting_id according to category name
            if '-e24' == get_active_pool() and q.question_id[0] == 'N':  # exam level entry licence
                sort_n_e_a = '1'
            elif get_active_pool() in ['-e06', '-e24']:    # exam level novice licence
                sort_n_e_a = '2'
            else:                                           # exam level cept licence
                sort_n_e_a = '3'

            if '-c' in sys.argv:
                category_name = new_categories.get(q.question_id[:-2])
                if category_name is None:
                    exit_with_line_info("In '" + NEW_CATEGORY_XLSX + "' fehlt die Kategorie für den Code '" + q.question_id[:-2] +"' (Question-ID '" + q.question_id +  "'). ")

                sorted_question_id = category_name[:5] + '_' + sort_n_e_a + '_' + dict_pool_arguments.get(get_active_pool()) + '_' + q.question_id

            else:
                category_name = q.category
                sorted_question_id = sort_n_e_a + '_' + q.question_id

            # write a row in the xlsx-file:
            if math_or_image_in_answer:

                # Some Latex term are to lang for the C2B app
                # (in DLE-2006 2 questions and in DLA-2007 2 questions)
                # Therefore: Divide long <span></span> terms in smaller ones
                question_text = question_text.replace(r'+\text',r'\)</span> <span class="math-tex">\(\:+\:\text')
                question_text = question_text.replace(r'-\text', r'\)</span> <span class="math-tex">\(\:-\:\text')
                question_text = question_text.replace(r'·\text', r'\)</span> <span class="math-tex">\(\:·\:\text')

                # Write the next row (with answers with math or/and images) into the Excel worksheet
                worksheet.write_row(xlsx_row,0,[sorted_question_id,category_name,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],labels_new_order[0],solutions_new_order[1],labels_new_order[1],solutions_new_order[2],labels_new_order[2],solutions_new_order[3],labels_new_order[3],'','','','','',''])
            else:
                # Remove all <br> tags in the answers (in DLE-2007 in 6 questions):
                final_answer = []
                for i in range(0,ANSWERS_PER_QUESTION):
                    final_answer.append(answers_new_order[i].replace('<br>',' —— ')) # best result in C2B app with ' —— '

                # Write the next row (with only plain text answers) into the Excel worksheet
                worksheet.write_row(xlsx_row,0,[sorted_question_id,category_name,'','multipleChoice',question_text,'','','','','','',new_question_image,info_question_id,'','','','',solutions_new_order[0],final_answer[0],solutions_new_order[1],final_answer[1],solutions_new_order[2],final_answer[2],solutions_new_order[3],final_answer[3],'','','','','',''])

            # end of: if math_or_image_in_answer:

            if new_question_image != "":
                try:
                    shutil.copyfile(IMAGE_REPLACEMENT_PATH + new_question_image, OUTPUT_IMG_PATH + new_question_image)
                except:
                    pass
                    # There is no replacement image available.
                    # So the original image will be used, which
                    # is already exported (see code above).

            # end of: if new_question_image != "":
        # end of: if export_this_question:
    # end of: for q in questions:

    print(str(rows_per_pool) + " rows exported for " + get_active_pool())
# end of: def export

# ----------------------------------------------------------
# End of def - main code starts
# ----------------------------------------------------------

#FIXME DEV modus
if len(sys.argv) < 2:
    sys.argv.append('-e06')
    # sys.argv.append('-a07')
    sys.argv.append('-e24')
    # sys.argv.append('-a24')
    # sys.argv.append('-a')
    sys.argv.append('-c')
    sys.argv.append('-dfrac')
    # sys.argv.append('-beta')
    # sys.argv.append('-math')

# Read out the command line arguments:
# -- Checking: are only expected arguments in the list?
# -- Schedule the asked question pools
read_out_arguments(sys.argv)

# Labels for those answers with pictures or math formulas:
LABELS = ('Œ','Ø','][','@')

# Multiple choice test with ... answers per question:
ANSWERS_PER_QUESTION = 4

# Generate a list of all possible tuple combinations:
PERMUTATIONS = [i for i in itertools.permutations(range(ANSWERS_PER_QUESTION))]

# If an original image should be replaced, the new image has to be in this path
# and need the same name after being exported (see dev export, var new_image_name):
IMAGE_REPLACEMENT_PATH = "input-files/new-images-as-replacement/"

# Separator on console output
print(' ')

xlsx_row = 0
workbook = None
worksheet = None

# Wird die nachfolgende for-Schleife zum ersten Mal durchlaufen?
first_pool_argument = True

# Loop for every question pool in the command line arguments
for pool_argument in list_scheduled_pools:

    set_active_pool(pool_argument)

    if pool_argument in ['-e06','-a07']:      # Is it one of these two pools?
        tk_img.set_font_size(24)
        IMG_BASE_PATH = 'input-files/afu-group-trainer/frontend/static/img/'
    elif pool_argument in ['-e24','-a24']:    # or is it one of these two pools?
        tk_img.set_font_size(36)
        IMG_BASE_PATH = 'input-files/50ohm-pocket__images-converted-to-png/'
    else:
        IMG_BASE_PATH = 'ERROR'
        exit_with_line_info("active question pool is not mentioned in the lists in the code lines above.")

    if not os.path.exists(IMG_BASE_PATH):
        exit_with_line_info('path to input files does not exist')

    # Set path, file name and worksheet for new category names:
    NEW_CATEGORY_PATH = 'input-files/new-category-names/'
    NEW_CATEGORY_XLSX = 'new-category-names.xlsx'
    NEW_CATEGORY_SHEET = dict_pool_arguments.get(get_active_pool())
    new_categories = {}

    # Read the new categories (Dictionary):
    if '-c' in sys.argv:
        if not os.path.exists(NEW_CATEGORY_PATH):
            exit_with_line_info("Path to '" + NEW_CATEGORY_PATH +"' does not exist (used with parameter '-c') ")

        new_categories = read_new_categories_from_xls(NEW_CATEGORY_PATH,NEW_CATEGORY_XLSX, NEW_CATEGORY_SHEET)

    # The name of the folder for the output data can be
    # chosen freely. It is created in the project folder.
    OUTPUT_FILE_PATH = 'output-files/Card2Brain_'
    if '-a' in sys.argv:
        OUTPUT_FILE_PATH += 'All-in-one'
    else:
        OUTPUT_FILE_PATH += dict_pool_arguments.get(get_active_pool())
    OUTPUT_FILE_PATH += '/'

    # The name of the Excel file can be chosen freely.
    OUTPUT_XLSX_FILE_NAME = "xlsx-for-c2b-import.xlsx"

    # DO NOT CHANGE. Card2Brain needs exactly this subfolder with exact this name.
    OUTPUT_IMG_PATH = OUTPUT_FILE_PATH + 'media/images/'

    # Choose the correct parser
    if pool_argument in ['-e06','-a07']:
        qp = json_parser2007()
    elif pool_argument in ['-e24','-a24']:
        qp = json_parser2024()
        qp.attach_text_processor(remove_flaws_coming_from_json_source)
    else:
        qp = json_parser2007() # qp assignment just for stopping PyCharm annoying me with an error message.
        exit_with_line_info("active question pool is not mentioned in the lists in the code lines above.")

    # Checking whether the folder path with all the required subfolders
    # already exists. If not, it will be created.
    if not os.path.exists(OUTPUT_IMG_PATH):
        try:
            os.makedirs(OUTPUT_IMG_PATH)
        except OSError as e:
            print(f"Error message was generated when creating the folder path: {e}")
            exit_with_line_info("Could not generate path 'OUTPUT_IMG_PATH = " + OUTPUT_IMG_PATH)

    # Check if an Excel file has to be opened or if an already opened Excel file will be used
    if first_pool_argument or '-a' not in sys.argv:

        if not first_pool_argument:
            # close the Excel file from previous pool argument
            workbook.close()
            print('  --> the output data is stored in <' + OUTPUT_FILE_PATH + '>')

        # Open (the next) Excel file in the output file folder:
        workbook = xlsxwriter.Workbook(OUTPUT_FILE_PATH + OUTPUT_XLSX_FILE_NAME)

        # Open a worksheet in the Excel file:
        worksheet = workbook.add_worksheet('Fragen')

        # Write row[0], the title row, in the worksheet of the Excel file:
        title = (
            'Id', 'Stapel', '', 'Frage-Typ', 'Frage', 'Antwort', 'Instruction', 'Ergänzung F', 'Phonetics F',
            'Beispielsatz F', 'Audio F', 'Bild F', 'Ergänzung A', 'Phonetics A', 'Beispielsatz A', 'Audio A',
            'Bild A', 'MCA1 Correct', 'MCA1 Text', 'MCA2 Correct', 'MCA2 Text', 'MCA3 Correct', 'MCA3 Text',
            'MCA4 Correct', 'MCA4 Text', 'MCA5 Correct', 'MCA5 Text', 'Copyright Image F', 'Copyright Image A',
            'Copyright Audio F', 'Copyright Audio A')
        title_format = workbook.add_format({'bold': True})
        worksheet.write_row(0, 0, title, title_format)

        # Initialize the counter, which row was written last
        xlsx_row = 0
    # end of: if first_pool_argument or '-a' not in sys.argv:

    # Links of images in the JSON file have this character sequence:
    image_tag = r'<img src="([^"]*)">'  # Regular Expression: https://www.w3schools.com/python/python_regex.asp

    if '-dfrac' in sys.argv:
        qp.attach_text_processor(latex_frac_to_dfrac)

    # Parsing elements
    qp.attach_text_processor(latex_to_utf8)
    qp.attach_text_processor(latex_to_utf8_subsuperscript)
    qp.attach_text_processor(to_card2brain)
    if '-a07' in sys.argv:
        qp.attach_text_processor(math_signs_much_less_n_much_greater)

    # Generate the Excel file and image folder for Card2Brain:
    if pool_argument in ['-e06','-e24']: # novice licence question pools
        export(qp.novice_questions(), 'HB3')
    elif pool_argument in ['-a07','-a24']: # cept licence question pools
        export(qp.cept_questions(), 'HB9')
    else:
        exit_with_line_info("active question pool is not mentioned in the lists in the code lines above.")

    first_pool_argument = False
# end of: for pool_argument in list_scheduled_pools

# close (the last) Excel file
workbook.close()
print('  --> the output data is stored in <' + OUTPUT_FILE_PATH + '>')

# Print final infos
print("Mission accomplished for the arguments " + str(sys.argv[1:]))
if '-l' in sys.argv:
    print("Argument '-l' (Lichtblicke) is not supported by the Card2Brain app.")
print('Recommendation:')
print('Sort the generated Excel files by the first column before importing them into Card2Brain.')