from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='iol.gisweb.alghero',
      version=version,
      description="Application for Iol Project alghero",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone iol alghero',
      author='Marco Carbone',
      author_email='marco.carbone@gmx.com',
      url='https://github.com/mamogmx/iol.gisweb.alghero.git',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iol', 'iol.gisweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
          'Products.CMFPlomino',
          'iol.gisweb.utils'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
