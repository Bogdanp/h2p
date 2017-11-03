import os

from setuptools import setup


def rel(*xs):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("h2p", "__init__.py"), "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


setup(
    name="h2p",
    version=version,
    description="Convert HTML files to PDFs.",
    long_description="Visit https://github.com/Bogdanp/h2p for more information.",
    packages=["h2p"],
    include_package_data=True,
)
