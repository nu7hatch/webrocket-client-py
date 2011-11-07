from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md')).read()
news = open(os.path.join(here, 'NEWS.md')).read()

version = '0.0.1'

requirements = [
    'websocket-client >= 0.4.1'
]

setup(
    name='WebRocket',
    version=version,
    description='',
    long_description=(readme + '\n\n' + news),
    keywords='',
    author='Chris Kowalik (nu7hatch)',
    author_email='chris@nu7hat.ch',
    url='http://github.com/nu7hatch/webrocket-client-py',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)
