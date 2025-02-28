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

# values of QUESTION_POOL
DLE2006 = 0
DLA2007 = 1
DLE2024 = 2
DLA2024 = 3

# DECIDE BEFORE RUNNING THE TOOL:
# QUESTION_POOL = DLE2006
QUESTION_POOL = DLA2007
# QUESTION_POOL = DLE2024
# QUESTION_POOL = DLA2024

# CHECK BEFORE RUNNING THE TOOL:
# These pathes must exist in ur project folder:
# 1)
IMG_BASE_PATH = 'afu-group-trainer/frontend/static/img/'
#
# 2) box/media/images/   #FIXME
#    (the output for Card2Brain)
#
# 3) library/fonts/dejavu-sans-fonts/DejaVuSans.ttf'
#    (needed by img_tk.py)

# CHECK ALSO:
# the pyton file json-parser.py respectively json-parser_DLEDLA2024.py
# for value settings before running the tool.

# NOW YOU ARE READY

LABELS = ('Œ','Ø','][','@')

ANSWERS_PER_QUESTION = 4
PERMUTATIONS = [i for i in itertools.permutations(range(ANSWERS_PER_QUESTION))]

workbook = xlsxwriter.Workbook('box/box.xlsx')
worksheet = workbook.add_worksheet('Fragen')
image_tag = r'<img src="([^"]*)">'

title=('Id','Stapel','','Frage-Typ','Frage','Antwort','Instruction','Ergänzung F','Phonetics F','Beispielsatz F','Audio F','Bild F','Ergänzung A','Phonetics A','Beispielsatz A','Audio A','Bild A','MCA1 Correct','MCA1 Text','MCA2 Correct','MCA2 Text','MCA3 Correct','MCA3 Text','MCA4 Correct','MCA4 Text','MCA5 Correct','MCA5 Text','Copyright Image F','Copyright Image A','Copyright Audio F','Copyright Audio A')

title_format = workbook.add_format({'bold': True})
worksheet.write_row(0, 0, title, title_format)

def shuffle(items, permutation):
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
        if question_image is not None:
            new_question_image = re.sub(r'/', '_', question_image)
            shutil.copyfile(IMG_BASE_PATH+question_image, 'box/media/images/'+new_question_image)
        else:
            new_question_image = ''

        permutation = random.randrange(math.factorial(ANSWERS_PER_QUESTION))
        answers = shuffle((q.answer_0, q.answer_1, q.answer_2, q.answer_3), permutation)
        solution = shuffle(('x','','',''), permutation)

        if '<img ' in q.answer_0:
            # assert(question_image is None) #FIXME Weshalb dieser Assert, der bei Prüfungsfrage TC515 auslöst?
            math_img_quirk = True
            image_col = []
            for label,answer in zip(LABELS, answers):
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
            print(new_question_image)
            answer_image.save(f'box/media/images/{new_question_image}')
        elif '<span class="math-tex">' in q.answer_0 or '<span class="math-tex">' in q.answer_1 or '<span class="math-tex">' in q.answer_2 or '<span class="math-tex">' in q.answer_3:
            math_img_quirk = True
            question_text += '<br><br>'
            for a1, a2 in zip(LABELS, answers):
                question_text += f'<strong>{a1}:</strong> {a2}<br>'
        if math_img_quirk:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,'','','','','',solution[0],LABELS[0],solution[1],LABELS[1],solution[2],LABELS[2],solution[3],LABELS[3],'','','','','',''])
        else:
            worksheet.write_row(i+1,0,[q.question_id,q.category,'','multipleChoice',question_text,'','','','','','',new_question_image,'','','','','',solution[0],answers[0],solution[1],answers[1],solution[2],answers[2],solution[3],answers[3],'','','','','',''])

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
    print("---------------------------------------")
    print("Wrong value in QUESTION_POOL")
    print("See top of file 'convert_to_card2brain.py")
    print("---------------------------------------")

# print("EOP")
workbook.close()
