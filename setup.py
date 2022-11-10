#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
from hm3u8dl_cli import version

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

VERSION = version

setup(
    name="hm3u8dl_cli",
    version=VERSION,
    description='m3u8视频解析，下载，解密，合并的python程序，支持全平台',
    keywords='m3u8 AES decrypt download parse',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='hecoter',
    author_email='hecoter12138@gmail.com',
    maintainer='hecoter',
    maintainer_email='hecoter12138@gmail.com',
    license='MulanPSL2',
    packages=["hm3u8dl_cli"],

    install_requires=[
        "m3u8","pycryptodome","tqdm","retry","tornado","rich","requests","multiprocess"
    ],
    platforms=["all"],
    url='https://github.com/hecoter/hm3u8dl_cli',
    include_package_data=True,
    package_data = {
        'hm3u8dl_cli': ['*/*'],
    },
    scripts=[],
    entry_points={
    'console_scripts': ['hm3u8dl_cli=hm3u8dl_cli.cli:main'] # ['hm3u8dl_cli=hm3u8dl_cli.__init__:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries'
    ]
)