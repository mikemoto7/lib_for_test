

import sys, re
sys.path.append("../lib")
from run_command import run_command

product_dir_path = 'not_set'

def do_test_runstring(runstring):
    import inspect
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                  # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # print info.filename                       # __FILE__     -> Test.py
    # print info.function                       # __FUNCTION__ -> Main
    # print info.lineno                         # __LINE__     -> 13
    output_file_basename = info.filename + '_' + info.function
    output_file_expected = output_file_basename + '.expected'
    output_file_actual   = output_file_basename + '.actual'

    if not re.search('^cd ', runstring):
        if product_dir_path == 'not_set':
            assert False, "File %s, line %d: product_dir_path is not set." % (info.filename, info.lineno)
        runstring = "cd " + product_dir_path + "; " + runstring
    rc, output, error = run_command(runstring)
    assert rc == 0, "File %s, line %d: run_command rc != 0.  output: %s.  error: %s" % (info.filename, info.lineno, output, error)
    fd = open(output_file_actual, 'w')
    for line in output.split('\n'):
         fd.write(line + '\n')
    fd.close()
    rc, diff_results, error = run_command("diff " + output_file_expected + " " + output_file_actual)
    msg1 = "File %s, line %d: " % (info.filename, info.lineno)
    msg2 = "diff rc != 0.\n----- output:\n%s\n----- error:\n%s" % (diff_results, error)
    assert rc == 0, msg1 + msg2
    msg2 = "diff error != ''.\n----- output:\n%s\n----- error:\n%s" % (diff_results, error)
    assert error == '', msg1 + msg2
    msg2 = "diff output != expected.  len(diff_results_list): %d\n----- diff_results:\n%s\n" % (len(diff_results.split('\n')), str(diff_results))
    assert diff_results == '', msg1 + msg2
    # diff_results_list = diff_results.split('\n')
    # msg3 = "File %s, line %d: output != expected.  len(diff_results_list): %d\n----- diff_results:\n%s\n----- output:\n%s\n----- expected:\n%s\n----- diff_results_list:\n%s\n----- error:\n%s" % (info.filename, info.lineno, len(diff_results_list), str(diff_results), output, expected_lines, '\n'.join(diff_results_list), error)
    # expected_lines = ''
    # for line in open(output_file_expected, 'r').read().splitlines():
    #     expected_lines += line + '\n'









