from toolkit_system import exit_with_line_info, dev_print

# Usage of this dictionary:
# Keys = allowed command line parameters
# Values = used as part of file path name
#          and used as info in the Excel in the field 'Ergänzung A'
dict_pool_arguments  = {
    "-e06":"DLE-2006",
    "-a07":"DLA-2007",
    "-e24":"DLE-2024", # NE-Katalog
    "-a24":"DLA-2024",
}
allowed_service_arguments = ["-?", "-c", "-l", "-dfrac", "-beta", "-math"]
allowed_pool_arguments = []     # see commend below; source is dict_pool_arguments
allowed_all_arguments = []      # see commend below
list_scheduled_pools = []       # see commend below
arg_active_pool = ""
# These variables will be filled initially in def read_out_arguments (see below)

def print_arguments():
    print('Find detailed infos in the README.md file ;-) ')
    print('Possible command line arguments are:')
    print('-?   : Is showing this overview of possible arguments')
    print('-e06 : Export question pool year 2006 for Novice Licence from BNetzA Germany')
    print('-a07 : Export question pool year 2007 for CEPT Licence from BNetzA Germany')
    print('-e24 : Export question pool year 2024 for Novice Licence (N+E) from BNetzA Germany')
    print('-a24 : Export question pool year 2024 for CEPT Licence from BNetzA Germany')
    print('-c   : Replace the category names according to list in folder input-files')
    print('-l   : Add link to "Lichtblicke" (only for "-e06" and "-a07")(not available for "Card2Brain")')
    print('-dfrac : LaTex terms with "frac" will be transformed to "dfrac" ')
    print('And only for beta testing: either "-beta" or "-math" ')
    print('-beta : Only some typical examples from the selected question pool will be exported')
    print('-math : Only questions containing LaTex code will be exported')

def set_active_pool(pool : str):
    global arg_active_pool
    arg_active_pool = pool

def get_active_pool():
    return arg_active_pool

def check_active_pool(pool_list: list):
    return arg_active_pool in pool_list

def read_out_arguments(arguments):

    global allowed_all_arguments
    global allowed_pool_arguments
    global allowed_service_arguments
    global list_scheduled_pools
    global arg_active_pool

    def print_arguments_n_exit():
        print("--------------------------------")
        print_arguments()
        print("--------------------------------")
        exit()

    # PART ONE : Initialize all the variables
    # =======================================

    # generate list_pool_arguments
    allowed_pool_arguments = list(dict_pool_arguments.keys())

    # generate list_all_arguments
    allowed_all_arguments.extend(allowed_pool_arguments)
    for i in allowed_service_arguments:
        allowed_all_arguments.append(i)

    # generate list_scheduled_pools
    for i in arguments:
        if i in allowed_pool_arguments:
            list_scheduled_pools.append(i)

    # PART TWO : Check, if the received arguments are correct
    # =======================================================

    # check for the '-?' argument
    if '-?' in arguments:
        print_arguments_n_exit()

    # check if received only allowed command line arguments
    for string_element in arguments[1:]:
        if string_element not in allowed_all_arguments:
            print("--------------------------------")
            print("Error: '" + string_element + "' is not a correct command line argument.")
            print_arguments_n_exit()

    # '-beta' and '-math' are not allowed as combination
    if '-beta' in arguments and '-math' in arguments:
        print("--------------------------------")
        print("'-beta' and '-math' can not be used together")
        print_arguments_n_exit()

    # check if at least 1 argument defines a question pool
    if '-beta' in arguments or '-math' in arguments:
        minimal_arg = 3
    else:
        minimal_arg = 2
        # sys.argv[0] contains path and script name
        # the arguments are in sys.argv[1] and following

    if len(arguments) < minimal_arg:
        print("--------------------------------")
        print("Please provide at least one question pool as command line argument.")
        print_arguments_n_exit()


def beta_test_exam_questions(question : str):

    if check_active_pool(['-e06']):
        selection = [
            "TA104",    # answer with superscript
            "TB105",    # answers with very long texts
            "TB604",    # answers with number with kommas
            "TB610",    # question with image in square
            "TB902",    # answers with math term
            "TC105",    # answer with image in portrait
            "TC106",    # answers are images in portrait
            "TC203",    # question with text and small image
            "TC301",    # question with text and image in landscape
            "TC506",    # each answer has text, an immage in the middle and again text
            "TC612",    # answer with 1, 2, 3
            "TD102",    # question with text and middle size image; Omega   sign in question and answer; subscript in question
            "TD203",    # answers with wide images
            "TE307",    # short question; short answers
            "TF205",    # question with a lage image
            "TH201",    # answers with lamda / 2 term
            "TH205",    # answers with %
            "TI204",    # answer with 4-digit numbers
            "TL201",    # answer with long math term
            "TL202",    # answer with long math term
            "TL302"    # answer with superscript
        ]
        return question in selection

    elif check_active_pool(['-a07']):
        selection = [
            "TA105",    # answers with math terms
            "TA113",    # answers with superscript and comma in superscript
            "TA116",    # answers with numbers and comma
            "TA117",    # answer with %
            "TA118",    # answers with long numbers
            "TA122",    # answers with lamda-sign
            "TB102",    # answers with Omega-sign
            "TB106",    # long answers
            "TB111",    # picture in question and long answers
            "TB201",    # answers with <br> tags
            "TB207",    # answers with R_L and R_i
            "TB209",    # answers with << and >>
            "TB601",    # answers with subscript
            "TB611",    # answers with Pi and math terms
            "TB909",    # answers with long math terms
            "TB910",    # answers with long math terms
            "TB923",    # answers with frac math terms
            "TC202",    # answers with images
            "TC206",    # answers with micro
            "TC507",    # answers with image between text
            "TC511",    # big image in question; answers with 1,2,3
            "TC512",    # big image in question; answers with 1,2,3
            "TC513",    # big image in question; answers with 1,2,3 and <br> tags
            "TC115",    # answers with big images
            "TC526",    # images in question and answer
            "TC601",    # answers with 1,2
            "TC619",    # big image in question
            "TC626",    # big images in question AND answers
            "TC716",    # big images in answers
            "TD108",    # answer with math term with /
            "TD204",
            "TD406",    # answers with 'sz' and v_u
            "TD605",
            "TE202",    # answers with math terms between text
            "TF211",    # answers with <br> tags
            "TG101",    # question with big picture
            "TG111",    # question with big picture
            "TG223",    # question with big picture
            "TG233",    # answers with long texts
            "TG315",    # answers with C_load
            "TG316",    # answers with C_1
        ]
        return question in selection

    elif check_active_pool(['-e24']):
        selection = [
            "EA108",    # answers with superscript
            "EA112",    # answer with omega sign
            "EA113",    # answer with micro sign
            "EA116",    # answers with long numbers
            "EB203",    # question with small image; answers with /
            "EB303",    # answers with °
            "EB305",    # one answer with lamda sign
            "EB310",    # question with big image im portrait format
            "EB411",    # question with big image
            "EB505",    # answers with square root math term
            "EB506",    # answers with math term
            "EC110",    # answers with small images
            "EC113",    # answer with numbers and omega sign
            "EC115",    # question with small image
            "EC301",    # answers with big images
            "EC306",    # question with 2 images, different size
            "EC506",    # question with big image
            "EC512",    # answers with images between text
            "EC516",    # answers with omega sign and /
            "EC520",    # big images as answers
            "EC609",    # answers with 1,2,3
            "ED101",    # answers with frac math term
            "ED120",    # answers with micro signs
            "EE101",    # answer with images im landscape format
            "EE203",
            "EE403",    # question with 'sz'; answer with square root
            "EF309",    # question with big image
            "EG102",    # answers with lamda sign
            "EG111",    # image in question should be one big image
            "EG502"     # answers with long math terms
        ]
        return question in selection

    elif check_active_pool(['-a24']):
        selection = [
            "AB103",    # Testen frac --> dfrag #FIXME
            "AB104",    # answers with long texts
            "AB208",    # answers with omega signs
            "AC405",    # 2 images in question and 1 per answer #FIXME question images in 1 file
            "AC406",    # 2 images in question and 1 per answer #FIXME question images in 1 filer
            "AC522",    # question with originally 'kOhm'
            "AC523",    # question with originally with 'm\Omega'
            "AD109",    # question with image in landscape format
            "AD110",    # subscript in answers # FIXME in app R_1 is not displayed
            "AD111",    # subscript in answers # FIXME in app R_1 is not displayed
            "AD114",    # question with image in portrait format
            "AD305",    # square size images in all answers
            "AD307",    # images in landscape format in all answers
            "AD308",    # 1 image in question and 1 in each answer
            "AD402",    # questions and answers with v_U #FIXME utf/LaTex-Combo
            "AD406",    # 2 images in question and 1 in each answer #FIXME question images in 1 file
            "AD408",    # 3? images in question and 1 in each answer #FIXME question images in 1 file
            "AD410",    # questions and answers with v_U #FIXME utf/LaTex-Combo
            "AD416",    # subscript in answers # FIXME : in the app R_1 is not displayed
            "AF120",    # question with large size image in landscape format
            "AF210",    # question with large size image in landscape format
            "AF426",    # question with big square size image
            "AG502",    # question with long math term #FIXME
            "AH102",    # answers with long texts
            "AH204",    # question with originally 'foF2'
            "AK103"     # testen frac --> dfrac
        ]
        return question in selection

    else:
        print(question)
        exit_with_line_info("question pool unknown in function 'beta_test_exam_questions' " )
        return True
