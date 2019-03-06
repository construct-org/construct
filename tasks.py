from invoke import task


@task
def tests(ctx):
    ctx.run('nosetests -v -s --logging-clear-handlers --with-doctest')


@task
def build_docs(ctx):
    ctx.run('docs\make html')
