from setuptools import setup

setup(name="horriblesubsdl",
      version='0.1',
      description='Download the animes',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      author='flare561',
      license='MIT',
      packages=['anime'],
      install_requires=[
          'cfscrape',
          'npyscreen',
          'lxml',
          'transmissionrpc',
          'dill'
      ],
      entry_points={
          'console_scripts': ['anime=anime:main'],
      })
