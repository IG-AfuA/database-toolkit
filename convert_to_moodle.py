from json_parser import json_parser, latex_dollar_to_pars
from bs4 import BeautifulSoup
import base64
import sys

# Usage: python3 cnovert_to_moodle.py [-n] [-c] [-l]
# -n: Export novice pool
# -c: Export CEPT pool
# -l: Embed "Lichtblicke"

qp = json_parser()
qp.attach_text_processor(latex_dollar_to_pars)

lichtblicke = '-l' in sys.argv

# Extract <img> elements ...
def process_img(img):
    soup = BeautifulSoup(img, 'html.parser')
    img_tags = soup.find_all('img')
        
    for img in img_tags:
        img['src'] = process_src(img['src'])

    return(str(soup))

# ... and embed images
def process_src(src):
    with open('afu-group-trainer/frontend/static/img/'+src, 'rb') as img_file:
        img64 = base64.b64encode(img_file.read()).decode('utf-8')
        return f'data:image/png;base64, {img64}'

# See https://docs.moodle.org/403/en/Moodle_XML_format
def export(questions, pool):
    old_category_path = None
    fh = open(f'export_moodle_{pool}.xml', 'w')
    fh.write('<?xml version="1.0" encoding="utf-8"?>\n<quiz>\n')
    for q in questions:
        category_path = f'$module$/top/{pool}/{q.parent_category}/{q.category}'
        if old_category_path != category_path:
            fh.write(f'    <question type="category"><category><text>{category_path}</text></category></question>\n')
            old_category_path = category_path

        if lichtblicke:
            if pool == 'HB3':
                lichtblick_folder = 'E'
            elif pool == 'HB9':
                lichtblick_folder = 'A'
            else:
                assert True

            with open(f'afu-group-trainer/frontend/static/lichtblicke/{lichtblick_folder}/{q.question_id}.pdf.jpg', 'rb') as img_file:
                img64 = base64.b64encode(img_file.read()).decode('utf-8')
                lichtblick_64 = f'data:image/jpeg;base64, {img64}'
            lichtblick_str = f'''
            <incorrectfeedback format="html">
              <text><![CDATA[<img src="{lichtblick_64}">]]></text>
            </incorrectfeedback>'''
        else:
            lichtblick_str = ''

        question_text = process_img(q.question_text)
        answer_0 = process_img(q.answer_0)
        answer_1 = process_img(q.answer_1)
        answer_2 = process_img(q.answer_2)
        answer_3 = process_img(q.answer_3)

        fh.write(f'''
        <question type="multichoice">
            <name format="txt"><text>{q.question_id}</text></name>
            <questiontext format="html">
                <text><![CDATA[{question_text}]]></text>
            </questiontext>
            {lichtblick_str}
            <answer fraction="100"><text><![CDATA[{answer_0}]]></text></answer>
            <answer fraction="0"  ><text><![CDATA[{answer_1}]]></text></answer>
            <answer fraction="0"  ><text><![CDATA[{answer_2}]]></text></answer>
            <answer fraction="0"  ><text><![CDATA[{answer_3}]]></text></answer>
            <shuffleanswers>1</shuffleanswers>
            <single>true</single>
            <answernumbering>abc</answernumbering>
        </question>
        \n''')
    fh.write('</quiz>\n')

if '-n' in sys.argv:
    export(qp.novice_questions(), 'HB3')
if '-c' in sys.argv:
    export(qp.cept_questions(), 'HB9')
