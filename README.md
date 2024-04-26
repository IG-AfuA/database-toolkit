Overview
========

This repository contains tools to process questions for the amateur radio exam that are published in [the following repository](https://github.com/ccoors/afu-group-trainer) by Christian F Coors. Thus, you are expected to check out this repository in the root folder. A git submodule is in place for this purpose. In consequence, we recommend to check out the codebase using

```
$ git clone --recurse-submodules https://github.com/IG-AfuA/database-toolkit.git
```

or, alternatively,

```
$ git clone https://github.com/IG-AfuA/database-toolkit.git
$ cd database-toolkit
$ git submodule update --init --recursive
```


Converter for Moodle
====================

`convert_to_moodle.py` is used to produce a collection of questions for import
into Moodle.


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
