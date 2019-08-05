from invoke import task


@task
def tests(ctx, level='WARNING', module=None):
    nose_cmd = (
        'nosetests '
        '--verbosity=2 '
        '--nocapture '
        '--logging-level=%s ' % level
    )
    if module:
            nose_cmd += module

    ctx.run(nose_cmd)


@task
def build_docs(ctx):
    ctx.run('docs\\make html')
