from setuptools import setup

setup(
    name='dods_match_stats',
    version='1.0',
    packages=['dods_match_stats'],
    url='https://github.com/evandrosouza89/dods-match-stats',
    license='MIT',
    author='Evandro Souza',
    author_email='evandro.souza89@gmail.com',
    description='A HL Log Standard parser and competitive match stats generator for Day of Defeat Source game.',
    install_requires=[
        'setuptools',
        'configparser',
        'SQLAlchemy'
    ],
)
