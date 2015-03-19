from setuptools import setup, find_packages


setup(
    name="onyx",
    version="1.3.7",
    description="Link server and engagement metrics " +
                "aggregator for Firefox Directory Links",
    author="Mozilla",
    packages=find_packages(),
    package_data={"": ["*.mmdb"]},
    include_package_data=True,
    scripts=["scripts/manage.py"],
)
