#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
%(scriptName)s Script Description:

   Look for files ending in '.expected' or '.actual' and do a diff of files with the same basenames, e.g., test1.expected exists, so compare test1.expected against test1.actual.

Runstring help:

   %(scriptName)s directory_path
   %(scriptName)s .

"""
interactive_mode_help = """
Interactive mode commands:

One diff = one ID_num = one testcase = one .expected-vs-.actual result file pair.

c         : Copy .actual file to .expected file for the current focus diff.  Next diff becomes the new current focus diff.  Else no more diffs so set current focus ID_num = -1.
c ID_num  : Copy .actual file to .expected file for the ID_num diff.
c ID_num,ID_num,...  : Copy .actual file to .expected file for ID_num diffs listed.
c a       : Copy .actual file to .expected file for all diffs.

d         : Display lines for the current focus diff.
d ID_num  : Display lines for the ID_num diff.
d ID_num,ID_num,...  : Display lines for the ID_num diffs listed.
d a       : Display lines for all ID_num diffs.

de        : Use the diff_edit.py tool to edit the .expected file of your current focus diff.
de ID_num : Use the diff_edit.py tool to edit the .expected file of your ID_num diff.
de ID_num,ID_num,... : Use the diff_edit.py tool to edit the .expected file of ID_num diffs listed.
de a      : Use the diff_edit.py tool to edit the .expected files for all diffs.

e         : Use $EDITOR to edit the .expected file of your current focus diff.
e ID_num  : Use $EDITOR to edit the .expected file of your ID_num diff.
e ID_num,ID_num,...  : Use $EDITOR to edit the .expected files of the ID_num diffs listed.
e a       : Use $EDITOR to edit the .expected files for all diffs.

h         : Display this help screen.

l         : Display line counts for current focus diff = one .expected-vs-.actual result file pair.
l a       : Display line counts for all diffs = all .expected-vs-.actual result file pairs.
l ID_num  : Display line counts for one diff = one .expected-vs-.actual result file pair.
l ID_num,ID_num,...  : Display line counts for the diffs listed.  diff/ID_num = one .expected-vs-.actual result file pair.

ID_num    : Same as "l ID_num".
o         : Display orphan table = a list of diffs that have either .expected or .actual files but not both.
q         : Quit.
s         : Display summary.
"""

#=============================================================

import os, sys, re
from subprocess import call
from pprint import pprint
import getopt

scriptName = os.path.basename(__file__).replace('.pyc', '.py')
scriptDir  = os.path.dirname(os.path.realpath(__file__))

sys.path.append(scriptDir + '/lib')
sys.path.append(scriptDir + '/bin')

from logging_wrappers import reportError, reportWarning, logging_setup, debug_run_status, user_input

import command_list

from run_command import run_command

import logging

import trace_mi

from diff_edit import diff_edit

#=============================================================

if sys.version_info[0] == 3:
    xrange = range

processing_message = ''

global options
options = {}


#=============================================================

scriptName = os.path.basename(sys.argv[0])

def get_docstring():
    return __doc__ % {'scriptName': scriptName }


def usage(exit_or_return='exit'):
    print(get_docstring())
    print(interactive_mode_help)
    if exit_or_return == 'exit':
        sys.exit(1)
    else:
        return

# def get_test_runstrings():
#     test_runstrings = []
#     for line in get_docstring().split('\n'):
#         found = re.search('^ *(' + scriptName + ' +-.+)$', line)
#         if found:
#             test_runstrings.append(found.group(1))
#     return test_runstrings


#====================================================

def num_diffs_remaining():
    diff_list_active = 0
    for entry in diff_list:
        if entry != -1:
            diff_list_active += 1
    return diff_list_active

#====================================================

def show_stats():
    global curr_ID_num

    stats_dict = { 
        'trf_list_len': len(test_result_file_list) ,
        'trf_list_expected_len': len(trf_list_expected) ,
        'trf_list_actual_len': len(trf_list_actual) ,
        'diff_list': -1 ,
        'orphan_list_len': len(orphan_list) }

    print("--------------------------")
    print("Stats--")
    print("Test result entry per expected/actual pair (trf_list_len):", stats_dict['trf_list_len'])
    print("Total .expected files (trf_list_expected_len):", stats_dict['trf_list_expected_len'])
    print("Total .actual files (trf_list_actual_len):", stats_dict['trf_list_actual_len'])
    num_diffs_active = num_diffs_remaining()
    print("diff_list_active:", num_diffs_active)
    print("orphan_list_len:", stats_dict['orphan_list_len'])
    print("curr_ID_num:", curr_ID_num)
    if num_diffs_active == 0:
        print("NO DIFFS TO MANAGE.")

#====================================================

def parse_command(command):
    global curr_ID_num
    command_parts = re.sub('  ', ' ', command.strip()).split(' ')
    ID_num_list = []
    if len(command_parts) == 1:
        if curr_ID_num != -1:
            ID_num_list.append(curr_ID_num)
        else:
            print("Need to specify ID number.")
            return 1, ID_num_list
    else:
        if command_parts[1] == 'a':
            for diff_entry in diff_list:
                if diff_entry != -1:
                    ID_num_list.append(diff_entry['ID_num'])
        else:
            ID_num_list = list(map(lambda x:int(x), command_parts[1].split(',')))
            if len(ID_num_list) == 1:
                curr_ID_num = ID_num_list[0]
    # print(159, ID_num_list)
    return 0, ID_num_list

#====================================================

def list_command(command):
    global ID_num_dict
    rc, ID_num_list = parse_command(command)
    if rc != 0:
        return

    for ID_num in ID_num_list:
        index = ID_num_dict.get(ID_num, -1)
        # print(172, ID_num, len(diff_list))
        if index != -1:
            print("--------------------------")
            print('ID_num:'+str(ID_num))
            print('file:'+diff_list[index]['expected_file'])
            print('num_diff_lines:'+str(len(diff_list[index]['diff_results'].split('\n'))))
            # for entry in diff_list[index]['diff_results']:
            #     print('expected:'+entry['file1'])
            #     print('actual:  '+entry['file2'])


#====================================================


if __name__ == '__main__':

    command_list.command_list(argv=sys.argv, your_scripts_help_function=[usage, 'return'])

    if len(sys.argv) == 1:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["h", "trace="])
    except getopt.GetoptError as err:
        # reportError("Unrecognized runstring " + str(err))
        usage()

    logging_setup(logMsgPrefix=scriptName, logfilename=scriptName + '.log', loglevel=logging.ERROR)

    trace_options = {}

    options_list = []

    for opt, arg in opts:
        if opt == "--h":
            usage()
        elif opt == "--debug":
            # setLoggingLevel(logging.DEBUG)
            options_list.append({'name':opt, 'value':arg})
            debug = True
        elif opt == "--trace":
            trace_options['trace_logfile_type'] = 'single_file'
            trace_options['tracePythonLogfileBasename'] = "tracelog"
            trace_options['watch_var_name'] = ''
            trace_options['watch_var_action'] = ''
            for suboption in arg.split(','):
                if 'wa:' in suboption:
                    trace_options['watch_var_name'] = suboption.split(':')[1]
                    trace_options['watch_var_action'] = 'report_all'
                elif 'wc:' in suboption:
                    trace_options['watch_var_name'] = suboption.split(':')[1]
                    trace_options['watch_var_action'] = 'report_changed'
                elif 'f:' in suboption:
                    trace_options['tracePythonLogfileBasename'] = suboption.split(':')[1]
                else:
                    print("ERROR: Unrecognized suboption = " + suboption)
                    sys.exit(1)
            trace_mi.enableTrace(trace_options)
        else:
            reportError("Unrecognized runstring option: " + opt)
            usage()

    stats_dict = {}
    orphan_list = []
    test_result_file_list = []
    trf_list_expected = []
    trf_list_actual = []

    ID_num = -1
    search_dir = sys.argv[1]
    for entry in os.listdir(search_dir):
        entry_full_path = search_dir + '/' + entry
        # print(150, entry_full_path)
        # if len(test_result_file_list) > 0:
        #     pprint(test_result_file_list[-1])  # debug
        # pprint(entry_full_path)  # debug
        if not os.path.isfile(entry_full_path):
            # test_result_file_list.append({'type': 'not_a_file', 'name': entry_full_path})
            continue

        found_actual = re.search('^(.+)\.actual$', entry_full_path)
        # print(158)
        # pprint(found_actual)  # debug
        if found_actual:
            basename = found_actual.group(1)
            match = False
            for index in xrange(len(test_result_file_list)):
                if test_result_file_list[index]['type'] != 'result_file':
                    # print(166, test_result_file_list[index]['type'], 'result_file')
                    continue
                if test_result_file_list[index]['basename'] == basename:
                    # print(169, test_result_file_list[index]['basename'], basename)
                    test_result_file_list[index]['actual_file'] = entry_full_path
                    trf_list_actual.append(test_result_file_list[index])
                    match = True
                    break
            if match == False:
                ID_num += 1
                test_result_file_list.append({'ID_num': ID_num, 'type': 'result_file', 'expected_file': '', 'actual_file': entry_full_path, 'basename': basename })
                trf_list_actual.append(test_result_file_list[-1])
            continue

        found_expected = re.search('^(.+)\.expected$', entry_full_path)
        # print(177)
        # pprint(found_expected)   # debug
        if found_expected:
            basename = found_expected.group(1)
            match = False
            for index in xrange(len(test_result_file_list)):
                if test_result_file_list[index]['type'] != 'result_file':
                   continue
                # print(189, test_result_file_list[index]['basename'], basename)
                if test_result_file_list[index]['basename'] == basename:
                    test_result_file_list[index]['expected_file'] = entry_full_path
                    trf_list_expected.append(test_result_file_list[index])
                    match = True
                    break
            if match == False:
                ID_num += 1
                test_result_file_list.append({'ID_num': ID_num, 'type': 'result_file', 'expected_file': entry_full_path, 'actual_file': '', 'basename': basename })
                trf_list_expected.append(test_result_file_list[-1])
            continue

        # test_result_file_list.append({'ID_num': ID_num, 'type': 'not_result_file', 'expected_file': '', 'actual_file': entry_full_path, 'basename': '' })

    ID_num_dict = {}  # use ID_num to find a diff_list index faster.
    curr_ID_num = -1
    diff_list = []
    for index in xrange(len(test_result_file_list)):
        if test_result_file_list[index]['type'] == 'result_file':
            if test_result_file_list[index]['expected_file'] != '' and test_result_file_list[index]['actual_file'] != '':
                cmd = 'diff ' + test_result_file_list[index]['expected_file'] + ' ' + test_result_file_list[index]['actual_file']
                rc, diff_results, error = run_command(cmd)
                if rc != 0:
                    reportError("Problem running cmd: " + cmd)
                    sys.exit(1)
                if diff_results == '':
                    test_result_file_list[index]['diff_results'] = []
                    continue
                test_result_file_list[index]['diff_results'] = diff_results
                diff_list.append(test_result_file_list[index])
                ID_num_dict[test_result_file_list[index]['ID_num']] = len(diff_list) - 1
                # print(280, ID_num_dict)
                if curr_ID_num == -1 or test_result_file_list[index]['ID_num'] < curr_ID_num:
                    curr_ID_num = test_result_file_list[index]['ID_num']

            else: orphan_list.append(test_result_file_list[index])

    # print(319, ID_num_dict)
    command = 's'
    prev_command = ''
    show_curr_entry = False

    while True:

        if command == prev_command:
            print("-----------------------------------------")
            if show_curr_entry == True:
                print("Current entry--")
                list_command("l "+str(curr_ID_num))
                print("-----------------------------------------")
                show_curr_entry = False
            command = user_input("Enter command or ID_num or h=help or q=quit: ")

        prev_command = command  # execute initial command before going interactive

        if command == '':
            # show_curr_entry = True
            continue

        found = re.search('^([0-9]+)$', command)
        if found:
            list_command('l ' + found.group(1))
            continue

        if re.search('^c', command):
            rc, ID_num_list = parse_command(command)
            if rc != 0:
                continue

            print("--------------------------")
            for ID_num in ID_num_list:
                # answer = user_input("Copying ID_num " + str(ID_num) + ".  Continue? (y/n) ")
                # if answer == 'n': break
                index = ID_num_dict.get(ID_num, -1)
                if index == -1:
                    print("ID_num value " + str(ID_num) + " does not exist.")
                    continue
                if diff_list[index] == -1:
                    print("ID_num value " + str(ID_num) + " already copied.")
                    continue
                # print(172, ID_num, len(diff_list))
                curr_ID_num = ID_num
                print("ID_num value " + str(ID_num) + " copied.")
                cmd = 'cp ' + diff_list[index]['expected_file'] + ' ' + diff_list[index]['expected_file'] + '.prev'
                # print("line ", 225, index, cmd)
                rc, output, error = run_command(cmd)
                # print('output: '+output)
                if error != '':
                    print('error: '+error)
                cmd = 'cp ' + diff_list[index]['actual_file'] + ' ' + diff_list[index]['expected_file']
                # print("line ", 231, index, cmd)
                rc, output, error = run_command(cmd)
                # print('output: '+output)
                if error != '':
                    print('error: '+error)
    
                # del diff_list[index]
                diff_list[index] = -1
                ID_num_dict[ID_num] = -1

                # Look for next curr item.
                curr_ID_num = -1
                curr_index = index
                while True:
                    index += 1
                    if index == curr_index:
                        break
                    if index >= len(diff_list):
                        index = 0
                    if diff_list[index] == -1:
                        continue
                    curr_ID_num = diff_list[index]['ID_num'] 
                    break
    
                show_curr_entry = True
            continue


        if re.search('^d ', command) or re.search('^d$', command):
            rc, ID_num_list = parse_command(command)
            if rc != 0:
                continue

            for ID_num in ID_num_list:
                answer = user_input("Continue? (y/n) ")
                if answer == 'n': break

                index = ID_num_dict.get(ID_num, -1)
                if index == -1:
                    print("ID_num value " + str(ID_num) + " does not exist.")
                    continue

                curr_ID_num = ID_num
                print("--------------------------")
                # output = call(['diff', diff_list[index]['expected_file'], diff_list[index]['actual_file'], ' | less'])
                rc = call(['diff ' + diff_list[index]['expected_file'] + ' ' + diff_list[index]['actual_file'] + ' | less'], shell=True)
                # print('rc: '+str(rc))
                show_curr_entry = True
            continue 


        if re.search('^de', command):
            rc, ID_num_list = parse_command(command)
            if rc != 0:
                continue

            for ID_num in ID_num_list:
                answer = user_input("Continue? (y/n) ")
                if answer == 'n': break

                index = ID_num_dict.get(ID_num, -1)
                if index == -1:
                    print("ID_num value " + str(ID_num) + " does not exist.")
                    continue

                # print(172, ID_num, len(diff_list))
                curr_ID_num = ID_num
                print("--------------------------")
                diff_edit(diff_list[match_index]['expected_file'], diff_list[match_index]['actual_file'])
                show_curr_entry = True
            continue 

        if re.search('^e', command):
            rc, ID_num_list = parse_command(command)
            if rc != 0:
                continue

            for ID_num in ID_num_list:
                answer = user_input("Continue? (y/n) ")
                if answer == 'n': break

                index = ID_num_dict.get(ID_num, -1)
                if index == -1:
                    print("ID_num value " + str(ID_num) + " does not exist.")
                    continue

                curr_ID_num = ID_num
                EDITOR = os.environ.get('EDITOR','vim')
                if EDITOR == '':
                    EDITOR = 'vi'
                file_choice = ''
                while True:
                    file_choice = user_input("Edit which file for diff " + str(ID_num) + "?\n1 " + diff_list[index]['expected_file'] + "\n2 " + diff_list[index]['actual_file'] + "\nType in a number or 'c' to cancel: " )
                    if file_choice == 'c':
                        break
                    if file_choice == '':
                        continue
                    if file_choice == '1':
                        which_file = diff_list[index]['expected_file']
                        break
                    if file_choice == '2':
                        which_file = diff_list[index]['actual_file']
                        break
                if file_choice == 'c':
                    continue
                call([EDITOR, which_file])
                show_curr_entry = True
            continue 

        if re.search('^h', command):
            print(interactive_mode_help)
            continue

        if re.search('^l', command):
            list_command(command)
            continue

        if re.search('^o', command):
            if len(orphan_list) == 0:
                print("No orphans detected.")
                continue
            for entry in orphan_list:
                print("--------------------------")
                print('expected_file:'+entry['expected_file'])
                print('actual_file:'+entry['actual_file'])
            continue

        if command == 'q':
            break

        if re.search('^s', command):
            show_stats()
            continue



        print("ERROR: Unrecognized command: " + command)





    if len(trace_options) > 0:
        print()
        print("TRACE: You enabled trace for this test run.  Refer to logfiles " + trace_options['tracePythonLogfileBasename']+"*.log for the trace events captured.")
        print()










