import os, glob

from behave import given, then
from behave import use_step_matcher
use_step_matcher("re")

from matches import *


@given( u"a file {nq}(?P<name>.+){nq} containing {nq}(?P<contents>.+){nq}".format(**sv) )
def aFileContaining(context, name, contents):
    """
    Store line into file.
    """
    open(name, 'w+').write(contents)

@given( u"file {nq}(?P<name>.+){nq} contains".format(**sv) )
@given( u"a file {nq}(?P<name>.+){nq} containing".format(**sv) )
def aFileContainingLines(context, name):
    """
    Store multiline into file.
    """
    open(name, 'w+').write(context.text)


@then( u'file {nq}(?P<fn>.*){nq} should be (?P<l>[0-9]+) line\(s\) long'.format(**sv) )
def fileShouldBeLinesLong(ctx, fn, l):
    v = open(fn).read()
    c = v.count('\n')
    if v[-1] != '\n':
        # newline is used as separator, not as line terminator?
        if int(l) != c-1:
            raise Exception("Expected %s but got %i lines" % (l, c-1))
    else: # last line must be empty but we check anyway
        if int(l) != c:
            raise Exception("Expected %s but got %i lines" % (l, c))


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


@given( 'a (\w*) {nq}(.+){nq} exists\.?'.format(**sv) )
@given( '(\w*) {nq}(.+){nq} exists\.?'.format(**sv) )
@given( '(\w*) path {nq}(.+){nq} exists\.?'.format(**sv) )
@given( 'that (\w*) paths {nq}(.+){nq} exists\(.?\)'.format(**sv) )
def pathExists(context, spec, type='file', trail=None):
   """
   Fail if path does not exists, or on failing match in glob spec.
   """
   globals()['pathname_type_' + type](spec, True)

@given( 'no (\w*) {nq}(.+){nq} exists\.?'.format(**sv) )
@given( '(\w*) {nq}(.+){nq} doesn\'t exist\.?'.format(**sv) )
@given( '(\w*) path {nq}(.+){nq} doesn\'t exist\.?'.format(**sv) )
@given( 'that (\w*) paths {nq}(.+){nq} doesn\'t exist\(.?\)'.format(**sv) )
def noPathExists(context, type='file', spec=None, trail=None):
   """
   Fail if path exists, or on existing match in glob spec.
   """
   globals()['pathname_type_' + type](spec, False)


def pathname_type_directory(spec, exists=True):
    for match in glob.glob(spec):
        if exists:
            if not os.path.isdir(match):
                raise Exception("Directory '%s' does not exist, it should" %
                        match)
        else:
            if os.path.isdir(match):
                raise Exception("Directory '%s' exists, it shouldn't" % match)

def pathname_type_file(spec, exists=True):
    for match in glob.glob(spec):
        if exists:
            if not os.path.isfile(match):
                raise Exception("File '%s' does not exist, it should" % match)
        else:
            if os.path.isfile(match):
                raise Exception("File '%s' exists, it shouldn't" % match)


#
