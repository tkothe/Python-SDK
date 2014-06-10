from setuptools import setup
# from pip.req import parse_requirements

import os

import aboutyou


BASE = os.path.dirname(__file__)


def readme():
  return open(os.path.join(BASE, 'README.rst')).read()

# # parse_requirements() returns generator of pip.req.InstallRequirement objects
# install_reqs = parse_requirements(os.path.join(BASE, 'requirements.txt'))

# # reqs is a list of requirement
# # e.g. ['django==1.5.1', 'mezzanine==1.4.6']
# reqs = [str(ir.req) for ir in install_reqs]


setup(
  name='aboutyou',
  packages=['aboutyou'],
  version=aboutyou.VERSION,
  install_requires=['pylibmc>=1.3.0', 'PyYAML'],
  description='A connection to the aboutyou.de shop.',
  long_description=readme(),
  author='Arne Simon',
  author_email='arne.simon@slice-dice.de',
  license='MIT',
  url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/overview',
  download_url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/downloads',
  keywords=['aboutyou', 'shop', 'collins', 'api'],
  classifiers=[
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet',
    'Topic :: Office/Business',
  ]
)
