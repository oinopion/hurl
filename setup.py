from distutils.core import setup
from os import path

ROOT = path.dirname(__file__)
README = path.join(ROOT, 'README.rst')

setup(
    name='hurl',
    py_modules = ['hurl'],
    url='https://github.com/oinopion/hurl',
    author='Tomek Paczkowski & Aleksandra Sendecka',
    author_email='tomek@hauru.eu',
    version='2.0',
    license='New BSD license',
    long_description=open(README).read(),
)
