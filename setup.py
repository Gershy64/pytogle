from setuptools import setup, find_packages
import re


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open("pytogle/__init__.py", encoding="utf-8") as f:
    version = re.findall("__version__ = '(.+)'", f.read())[0]


with open("requirements.txt", encoding="utf-8") as f:
    requirements = [r.strip() for r in f]




setup(
    name = 'Pytogle',
    version = version,
    packages = find_packages(),
    url = 'https://github.com/dermasmid/pytogle',
    license = 'MIT',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Cheskel Twersky',
    author_email= 'yoursn21@gmail.com',
    description = 'A Python wrapper for the google APIs',
    keywords = 'gmail gmail-api drive google-drive google-drive-api api-wrapper python3 python',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = requirements,
    python_requires='>=3.6'
)