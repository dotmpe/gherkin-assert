from behave import given, then
from behave import use_step_matcher
use_step_matcher("re")

from matches import *


@given( "{nq}(?P<key>.*){nq}[:=]? {nq}?(?P<val>[^ $]*){nq}?".format(**sv) )
def contextStrVar(ctx, key, val):
    setattr(ctx, key, val)


@given( "{nq}(?P<mapping>.+){nq} key {nq}(?P<key>.+){nq} {nq}(?P<val>.*){nq}".format(**sv) )
def contextMapStrVar(ctx, mapping, key, val):
    d = getattr(ctx, mapping, {})
    d[key] = val
    setattr(ctx, mapping, d)


@then( u'`(?P<attr>.*)` (?P<mode>contains|matches) the pattern "(?P<rx>.*)"' )
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


@then( u'`(?P<a>.*)` (?P<m>contains|matches) the patterns' )
def contextStringAttrEveryRegex(ctx, a, m):
    v = getattr( ctx, a )
    lines = [ l.strip() for l in ctx.text.split('\n') ]
    for l in lines:
        contextStringAttrRegex(ctx, a, m, l)


@then( '{nq}(?P<attr>.*){nq} should be {nq}(?P<s>.*){nq}'.format(**sv) )
@then( '{nq}(?P<attr>.*){nq} equals {nq}(?P<s>.*){nq}'.format(**sv) )
def contextStringAttrShouldBe(ctx, attr, s, inverse=False):
    s = s.encode('utf-8')
    v = str(getattr( ctx, attr ))
    if not inverse:
        if not ( v == s ):
            raise Exception("Unexpected %r != %r" % ( v, s ))
    else:
        if v == s:
            raise Exception("Unexpected %r == %r" % ( v, s ))

@then( u'{nq}(?P<attr>.*){nq} should be'.format(**sv) )
@then( u'{nq}(?P<attr>.*){nq} equals'.format(**sv) )
def contextStringAttrShouldBeMultiline(ctx, attr):
    contextStringAttrShouldBe(ctx, attr, ctx.text)


@then( u'`(?P<attr>.*)` should not be \'(?P<s>.*)\'' )
def contextStringAttrShouldNotBe(ctx, attr, s):
    contextStringAttrShouldBe(ctx, attr, s, inverse=True)


#
