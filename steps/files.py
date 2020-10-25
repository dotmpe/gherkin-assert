import os

from behave import given, then
from behave import use_step_matcher
use_step_matcher("re")

from matches import *


@given( u"a file {nq}(?P<name>.+){nq} containing {nq}(?P<contents>.+){nq}".format(**sv) )
def aFileContaining(context, name, contents):
    """
    Store line into file.
    """
    open(name).write(contents)

@given( u"a file {nq}(?P<name>.+){nq} containing:".format(**sv) )
def aFileContainingLines(context, name):
    """
    Store multiline into file.
    """
    open(name).write(context.text)


@then( u"file {nq}(?P<filename>.+){nq} lines equal".format(**sv) )
def fileLinesEqualMultiline(context, filename):
    """
    """
    value = open(filename).read()
    expected = context.text
    cmpMultiline(value, expected)


def cmpMultiline(value, expected):
    """
    Compare line by line, ignore file terminator EOL and trailing empty line.
    Give per-line match feedback: unexpected and/or missing.
    """
    valuelines = value.split(os.linesep)
    flc = len(valuelines)
    if not valuelines[flc-1]:
        valuelines.pop()

    strlines = expected.split(os.linesep)
    slc = len(strlines)
    if not strlines[slc-1]:
        strlines.pop()

    extra = [item for item in valuelines if item not in strlines]
    missing = [item for item in strlines if item not in valuelines]
    if not len(extra) and not len(missing):
        return

    err_msg = ''
    if len(extra):
        err_msg += "%s +'%s'" % (os.linesep, ("'%s +'"%os.linesep).join(extra))
    if len(missing):
        err_msg += "%s +'%s'" % (os.linesep, ("'%s -'"%os.linesep).join(missing))

    raise Exception("Mismatched lines: %s" % err_msg)


@then( "file '(?P<fn>.*)' should have" )
def fileShouldHaveMultiline(ctx, fn):
    if open(fn).read().strip() != ctx.text.strip():
        raise Exception("Mismatch")


@then( "`([^`]+)` has( not)? (exactly|more|less)(?: than)?( or equal to)? ([0-9]+) lines" )
def countFilelines(context, attr, invert, mode, or_equal, linecount):
    pass


#
