from setuptools import setup

setup(
    name='src',
    version='2.0',
    packages=['src'],
    url='https://github.com/evandrosouza89/dods-match-stats',
    license='MIT',
    author='Evandro Souza',
    author_email='evandro.souza89@gmail.com',
    description='A HL Log Standard parser and competitive match stats generator for Day of Defeat Source game.',
    install_requires=[
        'setuptools',
        'certifi'
        'charset-normalizer'
        'greenlet'
        'idna'
        'requests'
        'SQLAlchemy'
        'typing_extensions'
        'urllib3'
        'yattag'
    ],
)
