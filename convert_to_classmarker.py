from json_parser import json_parser, html_to_bbcode, latex_to_utf8, latex_to_bbcode, eszett_to_ss, BASE_URL
import argparse
import csv

# See https://www.classmarker.com/docs/importquestions/classmarker-multiple-choice-question-type-instructions.pdf
def write_csv(filename, questions, pool, lichtblicke_q, lichtblicke_f):
    filename_counter = 0
    i = None
    csvfile = None
    for q in questions:
        # Split into batches of 50 as per instructions
        if i is None or i >= 50:
            i = 0
            if csvfile is not None:
                csvfile.close()

            csvfile = open(filename.format(filename_counter), 'w')
            filename_counter += 1
            writer = csv.writer(csvfile)
            writer.writerow(['Question Type: multiplechoice','Parent Category',' Category','Random Answers','Correct Feedback','Incorrect Feedback','Points','Question','Correct','Answer A','Answer B','Answer C','Answer D'])

        lichtblicke_url = f'{BASE_URL}lichtblicke/{pool}/{q.question_id}.pdf'
        lichtblicke_text = f'[url={lichtblicke_url}]{q.question_id}[/url]'
        if lichtblicke_q:
            lichtblicke_q_text = f'{lichtblicke_text}: '
        else:
            lichtblicke_q_text = ''
        if lichtblicke_f:
            lichtblicke_f_text = lichtblicke_text
        else:
            lichtblicke_f_text = ''

        if pool == 'E':
            subcategory_name = 'Klasse E'
        elif pool == 'A':
            subcategory_name = 'Klasse A'
        else:
            assert(True)

        writer.writerow(['multiplechoice','D'+q.parent.category_id,subcategory_name,'Yes','',lichtblicke_f_text,1,lichtblicke_q_text+q.question_text,'A',q.answer_0,q.answer_1,q.answer_2,q.answer_3])
        i+= 1

parser = argparse.ArgumentParser()
parser.add_argument('-lq', '--lichtblicke-in-questions', action='store_true', help = 'Add links to Lichtblicke at the beginning of question')
parser.add_argument('-lf', '--lichtblicke-in-feedback',  action='store_true', help = 'Add links to Lichtblicke for incorrect feedback')
args = parser.parse_args()

qp = json_parser()
qp.attach_text_processor(html_to_bbcode)
qp.attach_text_processor(latex_to_utf8)
qp.attach_text_processor(latex_to_bbcode)
qp.attach_text_processor(eszett_to_ss)
write_csv('classmarker_export_E_{:02d}.csv', qp.novice_questions(), 'E', args.lichtblicke_in_questions, args.lichtblicke_in_feedback)
write_csv('classmarker_export_A_{:02d}.csv', qp.cept_questions(), 'A', args.lichtblicke_in_questions, args.lichtblicke_in_feedback)
