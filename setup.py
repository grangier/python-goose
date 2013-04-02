import os
from setuptools import setup, find_packages
from imp import load_source

version = load_source("version", os.path.join("goose", "version.py"))

setup(name='goose',
    version=version.__version__,
    description="Html Content / Article Extractor",
    long_description="",
    keywords='',
    author='Xavier Grangier',
    author_email='grangier@gmail.com',
    url='https://github.com/xgdlm/python-goose',
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PIL', 'lxml', 'cssselect', 'jieba']
)
