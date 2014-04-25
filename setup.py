import os
from setuptools import setup, find_packages

requires = [
        "Flask==0.10.1",
        "Flask-Script==0.6.7",
        "gevent==1.0",
        "gunicorn==18.0",
        "pycrypto==2.6.1",
]

if os.environ.has_key('MOZ_ONYX_DEV'):
    requires.extend([
        "ipython==2.0.0",
        "nose==1.3.1",
        "Fabric==1.8.1",
        "Flask-Testing==0.4.1",
        "mock==1.0.1",
    ])

setup(
        name = "onyx",
        version = "0.1",
        description = "Link server and engagement metrics aggregator for Firefox Directory Links",
        author = "Mozilla",
        packages=find_packages(),
        package_data={"": ["*.lua"]},
        include_package_data=True,
        install_requires = requires,
        scripts=["scripts/manage.py"],
)
