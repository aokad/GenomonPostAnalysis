# -*- coding: utf-8 -*-
"""
$Id: setup.py 135 2016-04-04 09:16:57Z aokada $
$Rev: 135 $
"""

from setuptools import setup, find_packages

version = '1.1.0'

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
      scripts=['genomon_pa'],
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
