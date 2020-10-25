import os, shutil
from subprocess import Popen, PIPE

from behave import use_step_matcher
use_step_matcher("re")

from matches import *
from files import *
from context_property import *



def bashCommand(ctx, cmd, err=None, tplshell='/bin/sh'):
    """
    Helper for subprocess.Popen shell invocation. The subprocess starts a shell
    interpreter, which runs the following script to start another shell intended
    to run a cmdline. This is the psuedo-code template script:

        tpl_var1;
        tpl_preamble var1=bar shell -flags -c "interpolated cmdline"

    Its is assembled from ctx.vars and ctx.tpl_vars, and the arguments to this
    function.
    """
    cmdline = 'bash -c "%s"' % cmd
    vars = getattr(ctx, 'vars', {})
    for k in vars:
        cmdline = "%s=\"%s\" " % ( k, vars[k] ) + cmdline
    preamble = getattr(ctx, 'tpl_preamble', {})
    if preamble:
        cmdline = preamble+' '+cmdline
    tvars = getattr(ctx, 'tpl_vars', {})
    for k in tvars:
        cmdline = "%s() { printf -- \"%s\"; }\n" % ( k, tvars[k] ) + cmdline
    p = Popen(cmdline, shell=True, executable=tplshell,
            stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    p.wait()
    ctx.status = p.returncode
    if ctx.status is None: ctx.status = 0
    ctx.output = ctx.stdout = p.stdout.read()
    ctx.stderr = p.stderr.read()
    if not err and p.returncode:
        print(cmdline)
        print(ctx.output)
        print(ctx.stderr)
        raise Exception("User run returned %i" % p.returncode)

@when( 'the user runs {nq}(?P<sh>.*){nq}{cl}'.format(**sv) )
def theUserRuns(ctx, sh, err):
    """
    Given shell command `sh`. Use '...' or '?' to allow non-zero exit.
    """
    if hasattr(ctx, 'env'):
        cmdline = "{env} {sh}".format(env=ctx.env, sh=sh)
    else:
        cmdline = sh
    vars = getattr(ctx, 'local_vars', {})
    for k in vars:
        cmdline = "%s='%s' " % ( k, vars[k] ) + cmdline
    bashCommand(ctx, cmdline, err, tplshell='/bin/bash')

@when( 'the user runs{cl}'.format(**sv) )
def theUserRunsMultiline(ctx, err):
    """
    Read shell command from subsequent multiline. See the-user-runs.
    """
    theUserRuns(ctx, ctx.text, err)


@given( "temp dir {nq}(?P<path>.+){nq}".format(**sv) )
def tempDir(context, path):
    contextMapStrVar(context, 'vars', 'PWD_old', os.getcwd())
    if not os.path.isdir("/tmp/"+path):
        os.mkdir("/tmp/"+path)
    os.chdir("/tmp/"+path)

@then( "drop temp\. dir {nq}(?P<path>.+){nq}".format(**sv) )
@then( "clean temp\. dir {nq}(?P<path>.+){nq}".format(**sv) )
def cleanTempDir(context, path):
    os.chdir(context.vars['PWD_old'])
    shutil.rmtree("/tmp/"+path)


def envDefaults(context):
    if 'env' not in getattr(context, 'tpl_vars', {}):
        contextMapStrVar(context, 'tpl_vars', 'env', '. \$CWD/.env.sh && . \$CWD/.meta/package/main.sh')
    if 'env_lib_load' not in getattr(context, 'tpl_vars', {}):
        contextMapStrVar(context, 'tpl_vars', 'env_lib_load', '. \$U_S/tools/sh/init.sh && lib_load')
    if 'env_setup' not in getattr(context, 'tpl_vars', {}):
        contextMapStrVar(context, 'tpl_vars', 'env_setup', '$(env) && $(env_lib_load) log std setup-sh-tpl')

@given( "{nq}([^']*){nq} setup from {nq}([^']*){nq}".format(**sv) )
@when( "{nq}([^']*){nq} is setup from {nq}([^']*){nq}".format(**sv) )
@given( "{nq}([^']*){nq} setup from {nq}([^']*){nq} with (?P<args>.+)".format(**sv) )
@when( "{nq}([^']*){nq} is setup from {nq}([^']*){nq} with (?P<args>.+)".format(**sv) )
def workingDirFromTpl(context, dirname, tplname, args=None):
    rtplname = os.path.realpath(tplname)
    tempDir(context, dirname)
    envDefaults(context)
    theUserRuns(context, '$(env_setup) && setup_sh_tpl \"%s\" %s' % (rtplname, args), None)

@given( "a clean {nq}(?P<lib>.*){nq} user-lib env".format(**sv) )
@given( "a clean {nq}(?P<lib>.*){nq} user-lib env with {nq}?(?P<vars>.+){nq}?".format(**sv) )
def cleanUserLibEnv(context, lib=None, vars=None):
    """
    """
    cleanEnv(context)
    d = getattr(context, 'vars', {})
    d['lib_utils'] = d.get('lib_utils', 'build setup-sh-tpl')
    if lib: d['lib_utils'] += ' '+lib
    d['CWD'] = d.get('CWD', '$PWD')
    for s in vars.split(' '):
        k, v  = s.split('=')
        d[k] = v
    setattr(context, 'vars', d)
    theUserRuns(context, '$(env_lib_load) \$lib_utils && lib_init', None)

@given( "a clean {nq}?(?P<name>.*){nq}? env".format(**sv) )
@given( "a clean {nq}?(?P<name>.*){nq}? env with {nq}?(?P<vars>.+){nq}?".format(**sv) )
def cleanEnv(context, name=None, vars=None):
    if vars:
        d = getattr(context, 'vars', {})
        for s in vars.split(' '):
            k, v  = s.split('=')
            d[k] = v
        setattr(context, 'vars', d)
    envDefaults(context)


@given( "project target {nq}(?P<target>.*){nq} is done".format(**sv) )
def projectTarget(context, target):
    theUserRuns(context, 'build-ifchange {target}'.format(target=target))

@given( "the current (?P<name>.*),?" )
def theCurrent(ctx, name):
    if ',' in name or ' and ' in name:
        names = name.split(', ')
        names[-1], n = names[-1].split(' and ')
        names.append(n)
    else: names = [name]
    for name in names:
        # Current dir, whatever checked-out version
        if name == "project":
            contextMapStrVar(ctx, 'vars', 'version', os.system('git describe --always'))
        elif name == "scriptpath":
            contextMapStrVar(ctx, 'vars', 'scriptpath', os.getcwd())
        elif name == "commandpath":
            contextMapStrVar(ctx, 'vars', 'CWD', os.getcwd())
            envDefaults(ctx)

        else:
            raise Exception("No such current %r" % name)



# Catch numbered steps; possibly do lookup

@given( r'(?P<Id>[0-9\.]+)\s(?P<step>.*)(?P<Refs>\[[0-9\.\ -]+\])?')
@when(  r'(?P<Id>[0-9\.]+)\s(?P<step>.*)(?P<Refs>\[[0-9\.\ -]+\])?')
@then(  r'(?P<Id>[0-9\.]+)\s(?P<step>.*)(?P<Refs>\[[0-9\.\ -]+\])?')
def step_impl(ctx, Id, step, Refs):
    raise NotImplementedError(u'TODO: DEF: %s"' % step)


# Catch all other steps
@given( r'(?P<step>.*)' )
@when(  r'(?P<step>.*)' )
@then(  r'(?P<step>.*)' )
def step_impl(ctx, step):
    raise NotImplementedError(u'TODO: STEP: %s"' % step)


# Sync: SCROW:
