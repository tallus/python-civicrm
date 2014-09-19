from setuptools import setup, find_packages

setup(
    name='python-civicrm',
    version='1.0',
    install_requires=[
        "requests",
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    url='https://github.com/tallus/python-civicrm',
    license='GPL',
    author='Paul Munday (tallus)',
    author_email='',
    description='Python package to access CiviCRM via the CiviCRM REST API v3.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
    ]
)
