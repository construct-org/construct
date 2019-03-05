from invoke import task


@task
def tests(c):
    c.run('nosetests -v -s --logging-clear-handlers --with-doctest')
