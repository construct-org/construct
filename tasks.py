from invoke import task


@task
def tests(ctx, level='WARNING'):
    ctx.run(
        'nosetests '
        '--verbosity=2 '
        '--nocapture '
        '--logging-level=' + level)


@task
def build_docs(ctx):
    ctx.run('docs\\make html')
