from setuptools import setup, find_packages

setup(
    name="ttt",
    version="0.0.0",
    description="Tactical thermal transition tool",
    author="Conor Lyman",
    author_email="conor@groundworkdata.org",
    packages=find_packages(exclude=["tests*"]),
    install_requires=["pandas~=1.4.0"]
)
