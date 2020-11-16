from behave import given, then
from behave import use_step_matcher
use_step_matcher("re")

from matches import *


@given( u"{nq}(?P<key>.*){nq}[:=]? {nq}?(?P<val>[^ $]*){nq}?".format(**sv) )
def contextStrVar(ctx, key, val):
    setattr(ctx, key, val)


@given( u"{nq}(?P<mapping>.+){nq} key {nq}(?P<key>.+){nq} {nq}(?P<val>.*){nq}".format(**sv) )
def contextMapStrVar(ctx, mapping, key, val):
    d = getattr(ctx, mapping, {})
    d[key] = val
    setattr(ctx, mapping, d)


@then( u'{nq}(?P<attr>.+){nq} (?P<mode>contains|matches) the pattern {nq}(?P<rx>.*){nq}'.format(**sv) )
def contextStringAttrRegex(ctx, attr, mode, rx):
    v = getattr( ctx, attr )
    if mode == 'contains':
        if not re.search( rx, v, re.M | re.S ):
            raise Exception("Missing pattern %r: %s" % ( rx, v ))
    elif mode == 'matches':
        if not re.match( rx, v, re.M | re.S ):
            raise Exception("Missing pattern %r: %s" % ( rx, v ))
    else:
        raise Exception("Unknown mode %s" % mode)


@then( u'{nq}(?P<a>.+){nq} (?P<m>contains|matches) the patterns'.format(**sv) )
def contextStringAttrEveryRegexMultiline(ctx, a, m):
    v = getattr( ctx, a )
    lines = [ l.strip() for l in ctx.text.split('\n') ]
    for l in lines:
        contextStringAttrRegex(ctx, a, m, l)


@then( u'{nq}(?P<attr>.+){nq} should be {nq}(?P<s>.*){nq}'.format(**sv) )
@then( u'{nq}(?P<attr>.+){nq} equals {nq}(?P<s>.*){nq}'.format(**sv) )
def contextStringAttrShouldBe(ctx, attr, s, inverse=False):
    s = s.encode('utf-8')
    v = str(getattr( ctx, attr ))
    if not inverse:
        if not ( v == s ):
            raise Exception("Unexpected %r != %r" % ( v, s ))
    else:
        if v == s:
            raise Exception("Unexpected %r == %r" % ( v, s ))

@then( u'{nq}(?P<attr>.+){nq} should be'.format(**sv) )
@then( u'{nq}(?P<attr>.+){nq} equals'.format(**sv) )
def contextStringAttrShouldBeMultiline(ctx, attr):
    contextStringAttrShouldBe(ctx, attr, ctx.text)

@then( u'{nq}(?P<attr>.+){nq} should not be {nq}(?P<s>.*){nq}'.format(**sv) )
def contextStringAttrShouldNotBe(ctx, attr, s):
    contextStringAttrShouldBe(ctx, attr, s, inverse=True)

@then( u'{nq}(?P<attr>.+){nq} should not be'.format(**sv) )
def contextStringAttrShouldNotBeMultiline(ctx, attr, s):
    contextStringAttrShouldBe(ctx, attr, s, inverse=True)


@then( u'{nq}(?P<attr>.+){nq} should be (?P<l>[0-9]+) line\(s\) long'.format(**sv) )
def contextStringAttrShouldBeLength(ctx, attr, l):
    v = str(getattr( ctx, attr ))
    c = v.count('\n')
    if int(l) != c:
        raise Exception("Expected %s but got %i lines" % (l, c))

@then( u'{nq}(?P<attr>.+){nq} should be empty'.format(**sv) )
@then( u'{nq}(?P<attr>.+){nq} is empty'.format(**sv) )
def contextStringAttrShouldBeEmpty(ctx, attr):
    v = str(getattr( ctx, attr ))
    if v:
        raise Exception("Expected none at %s but got %i chars" % (attr, len(c)))

@then( u'{nq}(?P<attr>.+){nq} should not be empty'.format(**sv) )
@then( u'{nq}(?P<attr>.+){nq} is not empty'.format(**sv) )
def contextStringAttrShouldNotBeEmpty(ctx, attr):
    v = str(getattr( ctx, attr ))
    if not v:
        raise Exception("Expected something at %s but got empty" % attr)


#
