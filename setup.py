# -*- coding: utf-8 -*-
"""
$Id: setup.py 87 2015-12-11 09:30:30Z aokada $
$Rev: 87 $
"""

from setuptools import setup, find_packages

version = '0.1'

setup(name='genomon_post_analysis',
      version=version,
      description="parser result files created by genomon",
      long_description="""\n
parser result files created by genomon (SV, mutaion-call and so on)""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='genomon post analysis',
      author='aokada',
      author_email='genomon_team@gamil.com',
      url='https://github.com/Genomon-Project/Genomon.git',
      license='GPL-3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      scripts=['genomon_pa_run', 'genomon_pa_hello'],
      data_files=[('config', ['genomon_post_analysis.cfg'])],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
