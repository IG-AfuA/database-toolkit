Overview
========

This repository contains tools to process sets of multiple choice exam questions for the amateur radio exam.

## Sources so far

So far the following exam sets can be processed:

* Recent exam sets from Germany, published 2024
* Former exam sets from Germany, published 2006/2007 (The data is from a [repository](https://github.com/ccoors/afu-group-trainer) by Christian F Coors).

Planned is for 2025:

* Former exam set from Switzerland, published 2023

## Output so far

Proessing tools are available for:

* Generating a file set which dan be imported into **Card2Brain**, a online flashcard learning tool. See for more details below.
* Generating a file set which can be imported into **ClassMaker**, a online exam training tool. See for more details below.
* Generating a file set,  which can bei imported into **Moodle**, a multi functional online course tool. See for more details below.

## How checking out  this repository

You are expected to check out this repository in the root folder. A git submodule is in place for this purpose. In consequence, we recommend to check out the codebase using

```
$ git clone --recurse-submodules https://github.com/IG-AfuA/database-toolkit.git
```

or, alternatively,

```
$ git clone https://github.com/IG-AfuA/database-toolkit.git
$ cd database-toolkit
$ git submodule update --init --recursive
```

# Command line parameters

The converting tools named `convert_to_...` are using command line parameters.

Possible command line arguments are (choose at least one):

* `-?`  : is showing this overview of possible arguments.

* `-e06` : Convert the former exam question pool (published 2006; in use from 2007 to 2023) for Novice Licence from BNetzA Germany.

* `-a07` : Convert the former exam question pool (published 2007; in use from 2007 to 2023) for Cept Licence from BNetzA Germany.

* `-e24`  : Convert the question exam pool (published 2024) for Novice Licence from BNetzA Germany.

* `-a24` : Convert the exam question pool (published 2024) for Cept Licence from BNetzA Germany.

* `-hb323` : Convert the former exam question pool (published 2023) for Novice Licence (HB3) from BAKOM Switzeland. (NOT YET IMPLEMENTED)

* `-hb923` : Convert the former exam question pool (published 2023) for CEPT Licence (HB9) from BAKOM Switzeland. (NOT YET IMPLEMENTED)

* `-l` : Add link to "Lichtblicke" (only in combination with `-e06` and `-a07` ) (not available for Card2Brain).

And experimental:

* `-dfrac` : LaTex terms with "frac" will be transformed to "dfrac".

And only for beta testing: either "-beta" or "-math": 

- `-beta` : Export only some typical examples from the selected question pools. 

- `-math` : Export only questions containing LaTex code.
  
  

Converter for Card2Brain
====================

## Providing the input data

...

...

...



## Using Card2Brain

Card2Brain is available as smartphone app or as web app. The functionality is identical, but the display is different.

### Available fields in C2B

In Card2Brain a flashcard consists of the following elements:

The question  page consists of

* Text (utf8) with math terms in LaTex. No URL allowed.

* one picture, which will be shown in the smartphone app avobe the text and in the web app below the text.

* one sound file, which will be shown in the smartphone app avobe the text and in the web app below the text.

* a comment line for text (utf8). No URL, no images.

The answer page consists of

* for each multiple choice answer a text field (utf8). No LaTex and no images.

* a comment line for text (utf8). No URL, no images.

### Dealing with these field restrictions

Exam questions may contain more than one image. In addition, multiple-choice answers may contain an image or a mathematical formula.

Since Card2Brain cannot map this one-to-one, the following workarounds have been chosen:

* If the  question contains more than one image, the images are merged into one image.

* If the possible answers include an image, the answer images are given a  label and combined with the question image. And only these labels are then mentioned as possible answers.

* If the possible answers include an mathematical term in LaTex, the answers are given a label and combined with the question text. And only these labels are then mentioned as possible answers.

### Displaying restrictions

Images are displayed in large format in the smartphone app. However, in the web app, they are reduced to a size of 140px wide. They are only displayed in large format when you click on the image.

There is no solution to this problem. We recommend using the smartphone app for learning. The web app, on the other hand, is suitable if adjustments need to be made to the learning sets.

Converter for ClassMarker
=========================

`convert_to_classmarker.py` is used to produce a collection of questions for
import into [ClassMarker](https://www.classmarker.com/). Note that you have to
set `BASE_URL` in `json_parser.py` to point to some web server that delivers
the images via https. During a quiz, questions are provided by classmarker
and images are retrieved from that web server. This was done for simplicity
since we avoid to import images into classmarker this way (we use the
`[img]URL[/img]` BB-code to do that).

Thus, the base URL needs to start with `https://` and have a trailing slash,
e.g. `https://classmarker.example.com/static/`. In this case, the following
paths are expected to exist, containing the images and 'Lichtblicke',
respectively:

```
https://classmarker.example.com/static/img/
https://classmarker.example.com/static/lichtblicke/
```

You can pull these files from `afu-group-trainer/frontend/static/`

To insert 'Lichtblicke' into the 'incorrect feedback' field or to add a
link to the question text, use the flags `-lf` and `-lq`, respectively:

```
usage: convert_to_classmarker.py [-h] [-lq] [-lf]

options:
  -h, --help            show this help message and exit
  -lq, --lichtblicke-in-questions
                        Add links to Lichtblicke at the beginning of question
  -lf, --lichtblicke-in-feedback
                        Add links to Lichtblicke for incorrect feedback
```

The converter will produce two sets of output files, `classmarker_export_E_##.csv`
and `classmarker_export_A_##.csv`, one set for each pool. Classmarker expects
you to import questions in batches of 50, thus each of these files contains
50 questions and `##` is an integer for the batch number. Importing all this is
somewhat tedious in particular for the A pool, but unfortunately this
limitation is by Classmarker. One may consider using the API to import
questions after ensuring that there is no access limit.

Classmarker expects you to create the parent- and subcategories before importing
the questions. This is another tedious task that can be automated, though. By
default, the category structure is:

```
├─ D01.1
│  ├─ Klasse E
│  ├─ Klasse A
├─ D01.2
│  ├─ Klasse E
│  ├─ Klasse A
├─ ...
```

We suggest the following process to automatically create those categories:

1. First we extract the categories into a file `categories.txt`:
   
   ```
   $ python3 dump_categories.py > classmarker_categories/categories.txt
   ```

2. Download `ClassMarkerApiClient.php` from the [github classmarker repo](https://github.com/classmarker/api-client/tree/master)
   and store it in the `classmarker_categories` subfolder.

3. Generate an API key by following the instructions [here](https://www.classmarker.com/online-testing/docs/api/#authentication)
   (section 'Generate an API key', pick a suitable name and keep the default settings.)

4. Enter your API key and secret in `classmarker_categories/config.inc`

5. Run `import_categories.php` which will iterate through your `categories.txt`
   and create the categories and corresponding subcategories 'Klasse E' and
   Klasse A'. You can use `tee` to log the process in case something goes wrong.
   
   ```
   $ cd classmarker_categories
   $ php import_categories.php | tee import.log
   [...]
   $
   ```

Then you can import the CSV files created by `convert_to_classmarker.py`. Since
the category names created in this way are not very descriptive, they should be
renamed to something more verbose after the import is completed. We also offer
a process for this:

1. Run `get_categories.php` (still from within the `classmarker_categories`
   subdirectory to create a JSON file of your current category structure:
   
   ```
   $ php get_categories.php > ../all_categories.json
   ```

2. Run `categories_json_to_xls.py` from within the main directory (i.e. not from
   within the `classmarker_categories` subfolder. This will generate a spreadsheet
   with the following columns:
   
   - `PK`: The classmarker category ID for a given category. Never change this number.
   - `Name E`: Name of the category in the E-pool TOC.
   - `Name A`: Name of the category in the A-pool TOC.
   - `Name neu`: Name that will be used for the import. This is the one you need to modify.
   
   The default for `Name neu` is the category name from the E-pool if it
   exists, otherwise we use the category name from the A-pool (we found the
   former to be a bit more descriptive but they are for the very most part
   equivalent). Classmarker imposes a limit of 30 characters for these
   names, so you will have to shorten the entries and use abbreviations.

3. Create a file `classmarker_categories/Classmarker_Kategorien_rename.txt` that has the
   `PK`, followed by a space character followed by the new name for the category (up to
   30 characters). For example:
   
   ```
   55 D01.1: Math. Grundkenntnisse
   59 D01.2: Grössen und Einheiten
   44 D10.1: Messinstrumente
   45 D10.2: Messungen I
   46 D10.3: Oszilloskop
   47 D10.4: Stehwellenmessgerät
   48 D10.5: Frequenzzähler
   49 D10.6: Absorptionsfreq.messer
   ...
   ```

4. Run `rename_categories.php` from within the `classmarker_categories` folder.
   This will rename each category according to
   `Classmarker_Kategorien_rename.txt`. Note that this program has no mercy, thus
   it is critical to ensure that the input file is correct. Do not simply copy the
   example mentioned above as the numbers at the beginning of each line will not
   correspond to your categories. In consequence, the script will rename the wrong
   gategories and you will have to clean up a great mess.

# Converter for Moodle

`convert_to_moodle.py` is used to produce a collection of questions for import
into Moodle.

Rescaling Images
================

Some images have a fairly large resolution. `rescale_large_images.sh` is a helper script used to shrink those images.

Text Comparison
===============

`analyze_similarities.py` is used for text comparisons between the two question
pools. The Levenshtein similarity, longest common substring and cosine
similarity is computed for each pair of questions from the respective pools.
This is done for the question text alone ("Q") and also for the concatenation
of questions and answers ("QA"). HTML tags are stripped before comparison.

This can be useful to identify identical or similar questions, thus helping in
structuring courses where the novice license is acquired first, followed by an
upgrade class.

Running the program involves many pairwise comparisons, thus you cannot expect
this to be quick.

JSON Parser
-----------

`json_parser.py` is used by the conversion and analysis scripts. The file
contains a class that reads the json file from the afu-group-trainer by
ccoors and offers ways to iterate through the questions. It also contains
data structures to store question exams and answers.

This file is not meant to be used directly, but instead imported and used
by other conversion and analysis scripts.
