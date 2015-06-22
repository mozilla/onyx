from setuptools import setup, find_packages


setup(
    name="onyx",
    version="1.4.5",
    description="Link server and engagement metrics " +
                "aggregator for Firefox Directory Links",
    author="Mozilla",
    packages=find_packages(),
    package_data={"": ["*.mmdb"]},
    include_package_data=True,
    scripts=["scripts/manage.py", "scripts/external_api_test.py"],
)
