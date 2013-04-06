from distutils.core import setup
from os import path

ROOT = path.dirname(__file__)
README = path.join(ROOT, 'README.rst')

setup(
    name='hurl',
    py_modules=['hurl'],
    url='https://github.com/oinopion/hurl',
    author='Tomek Paczkowski & Aleksandra Sendecka',
    author_email='tomek@hauru.eu',
    version='2.1',
    license='New BSD License',
    long_description=open(README).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
