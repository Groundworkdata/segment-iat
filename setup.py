from setuptools import setup, find_packages

setup(
    name="segment-iat",
    version="0.0.0",
    description="Segment intervention analysis tool",
    author="Conor Lyman",
    author_email="conor@groundworkdata.org",
    packages=find_packages(exclude=["tests*"]),
    install_requires=["pandas~=1.4.0"]
)
