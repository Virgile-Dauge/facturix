from setuptools import setup, find_packages

setup(
    name='facturix',
    version='0.1',
    packages=find_packages(),
    package_data={
        'facturix': ['validators/*.sch', 
                     'validators/*.xsd', 
                     'templates/*.xml',
                     'color_profiles/*.icc'],
    },
)