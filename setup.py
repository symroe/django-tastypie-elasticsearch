#!/usr/bin/env python

import os
from setuptools import setup, find_packages

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_project.settings")
# 
# import tastypie_elasticsearch

setup(
    name = 'django-tastypie-elasticsearch',
    # version = tastypie_elasticsearch.__version__,
    description = "ElasticSearch support for django-tastypie.",
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author = 'Jordi Llonch',
    author_email = 'llonchj@gmail.com',
    url = 'https://github.com/llonchj/django-tastypie-elasticsearch',
    keywords = "REST RESTful tastypie pyes elasticsearch django",
    license = 'AGPLv3',
    packages = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests')),
    classifiers = (
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ),
    # zip_safe = True,
    requires = [
        'Django',
        'tastypie',
        'pyes',
    ],
)
