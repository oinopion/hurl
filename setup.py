from distutils.core import setup
from os import path

ROOT = path.dirname(__file__)
README = path.join(ROOT, 'README.rst')
REQUIREMENTS = path.join(ROOT, 'requirements.txt')

setup(
    name='hurl',
    py_modules = ['hurl'],
    url='https://github.com/oinopion/hurl',
    author='Tomek Paczkowski & Aleksandra Sendecka',
    author_email='tomek@hauru.eu',
    version='1.1.dev',
    license='New BSD license',
    long_description=open(README).read(),
    install_requires=open(REQUIREMENTS).read(),
)
