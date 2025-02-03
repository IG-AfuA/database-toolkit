import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QSLearn.settings")
django.setup()

from json_parser import json_parser, latex_dollar_to_pars, prefix_static_image_path
from app.models import *
import logging

# FIXME: Strip zero
# FIXME: Maintain order with novice/cept staggered approach
# FIXME: Use dedicated categories for HB3 and HB9

qp = json_parser()
qp.attach_text_processor(latex_dollar_to_pars)
qp.attach_text_processor(prefix_static_image_path)

# Used to create category order that increments
class auto_increment:
    def __init__(self):
        self.counter = 0

    # Get and increment
    def get(self):
        ret = self.counter
        self.counter += 1
        return self.counter

def ammend_categories(q, category_order, subcategory_order):
    # Install category
    try:
        c = Category.objects.get(category_id=q.parent.parent.category_id)
    except Category.DoesNotExist:
        c = Category(category_id=q.parent.parent.category_id, category_name=q.parent.parent.category_name, category_order = category_order.get())

    if c.category_name != q.parent.parent.category_name:
        logging.warning(f'Category mismatch for {c.category_id}: {c.category_name} vs. {q.parent.parent.category_name}')
    c.save()
    # Install subcategory
    try:
        sc = Subcategory.objects.get(subcategory_id=q.parent.category_id)
        if sc.subcategory_name != q.parent.category_name:
            logging.warning(f'Subcategory mismatch for {sc.subcategory_id}: {sc.subcategory_name} vs. {q.parent.category_name}')
    except Subcategory.DoesNotExist:
        sc = c.subcategory_set.create(subcategory_id=q.parent.category_id, subcategory_name=q.parent.category_name, subcategory_order = subcategory_order.get())

def insert_question(q, pool):
        pool.question_set.create(
            subcategory = Subcategory.objects.get(subcategory_id=q.parent.category_id),
            question_id = q.question_id,
            question_text = q.question_text,
            answer_0 = q.answer_0,
            answer_1 = q.answer_1,
            answer_2 = q.answer_2,
            answer_3 = q.answer_3,
            solution = 0,
            outdated = q.outdated,
)

# First we flush the database ...
Category.objects.all().delete()
Pool.objects.all().delete()

# ... then we create the pools ...
e_pool = Pool(pool_name='HB3')
e_pool.save()
a_pool = Pool(pool_name='HB9')
a_pool.save()

# ... and finally we collect categories and questions

category_order = auto_increment()
subcategory_order = auto_increment()

for q in qp.novice_questions():
    ammend_categories(q, category_order, subcategory_order)
    insert_question(q, e_pool)
for q in qp.cept_questions():
    ammend_categories(q, category_order, subcategory_order)
    insert_question(q, a_pool)
