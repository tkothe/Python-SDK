from setuptools import setup

import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

import aboutyou

setup(
  name='aboutyou',
  packages=['aboutyou'],
  version=aboutyou.VERSION,
  description='A connection to the aboutyou.de shop.',
  long_description=read('README.rst'),
  author='Arne Simon',
  author_email='arne.simon@slice-dice.de',
  license='MIT',
  url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/overview',
  download_url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/downloads',
  keywords=['aboutyou', 'shop', 'collins'],
  classifiers=[
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet',
    'Topic :: Office/Business',
  ],
)
