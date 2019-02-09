from setuptools import setup

setup(
    name='faa_tpp',
    version='0.1.1',
    packages=['faa_tpp'],
    url='https://github.com/jgillmanjr/faa_tpp',
    install_requires=[
        'untangle',
        'requests',
        'pendulum'
    ],
    license='',
    author='Jason Gillman Jr.',
    author_email='jason@rrfaae.com',
    description='Get FAA dTPP data'
)
