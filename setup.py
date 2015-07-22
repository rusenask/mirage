import os

from setuptools import setup, find_packages
from stubo import version_info

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='stubo',
      version=".".join(map(str, version_info)),
      description='Stubo',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
      ],
      url='stubomatic.net',
      license='LICENSE.txt',
      keywords='Stub-O-Matic stubo tester testing service virtualisation',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="stubo",
      entry_points="""\
      [console_scripts]
      stubo = stubo.scripts.service:run_stubo_app
      export_stubs = stubo.scripts.scenario:export_stubs
      list_stubs = stubo.scripts.scenario:list_stubs 
      stub_count =  stubo.scripts.scenario:stub_count 
      latency_pcent =  stubo.scripts.stats:latency_pcent
      delete_test_dbs = stubo.scripts.admin:delete_test_dbs  
      create_tracker_collection = stubo.scripts.admin:create_tracker_collection  
      purge_stubs = stubo.scripts.admin:purge_stubs  
      """
      )
