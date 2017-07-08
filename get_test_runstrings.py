#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
%(scriptName)s Script Description:

Extract example runstrings from a docstring help into a list to create pytest testcases.

Runstring help:

   %(scriptName)s
      With no options, displays this help screen.

   %(scriptName)s  --stdin  scriptName
      Get input from stdin.  Specify the scriptName that will show up in the docstring help.

"""

#=============================================================

import os, sys, re

scriptName = os.path.basename(__file__).replace('.pyc', '.py')
scriptDir  = os.path.dirname(os.path.realpath(__file__))

sys.path.append(scriptDir + '/lib')
sys.path.append(scriptDir + '/bin')

import getopt

if sys.version_info[0] == 3:
    xrange = range


#====================================================

scriptName = os.path.basename(sys.argv[0])

def get_docstring():
    return __doc__ % {'scriptName': scriptName}


def usage(exit_or_return='exit'):
    print(get_docstring())
    if exit_or_return == 'exit':
        sys.exit(1)
    else:
        return

#====================================================

def get_test_runstrings(docstring_scriptName, docstring):
    test_runstrings = []
    for line in docstring.split('\n'):
        # print(55, line)
        found = re.search('^ *(' + docstring_scriptName + ' +-.+)$', line)
        if found:
            test_runstrings.append(found.group(1))
    return test_runstrings



#====================================================



if __name__ == '__main__':

    if len(sys.argv) == 1:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["stdin="])
    except getopt.GetoptError as err:
        reportError("Unrecognized runstring " + str(err))
        usage()

    docstring_scriptName = 'docstring_scriptName_not_set'
    for opt, arg in opts:
        if opt == "--stdin":
            docstring_scriptName = arg
        else:
            print("Unrecognized runstring option: " + opt)
            usage()

    docstring = sys.stdin.read().strip()
    # print(88, docstring)

    test_runstrings = get_test_runstrings(docstring_scriptName, docstring)
    # for row in test_runstrings:
    #     print(row)


    # print("Testcases:")
    for row in test_runstrings:
        # print(96, row)
        row = re.sub('Portfolio_xml_file', 'demo_data_file.xml', row)
        row_minus_pfiles = re.sub('demo_data_file.xml', '', row)
        row_minus_pfiles = re.sub('--pfile', '', row_minus_pfiles)
        # print(100, row_minus_pfiles)

        # Does not work.  Misses consecutive same patterns, e.g.,  --param1  --param2  , --param2 will not get captured.
        # option_list = re.findall("--([^ ]+) +--|--([^ ]+) +([^:\- ]+)($)|--([^ ]+)(?:[ ]|$)", row_minus_pfiles)
        option_list_no_empty_strings = []
        for match in re.finditer("--([^ ]+) +([^%:\- ]+)(?:[%:\- ]|$)|--([^ ]+)(?: |$)", row_minus_pfiles):
            # print("new match")
            try:
               for index in range(1,5):
                   # print(104, match.group(index))
                   if match.group(index) is not None:
                       option_list_no_empty_strings.append(match.group(index))
            except:
               pass
        # option_list_no_empty_strings = [ element for group_match in option_list for element in group_match if element != '' ]
        # print(103, option_list_no_empty_strings)
        if option_list_no_empty_strings is not None:
            tc_name = '_'.join(option_list_no_empty_strings)
        else:
            tc_name = "???"
        print('')
        print('    def test_runstring_' + tc_name + '(self):')
        print('        do_test_runstring("' + row + '")')



