from setuptools import setup, find_packages

setup(
    name='justin_utils',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
    ],
    url='',
    license='MIT',
    author='Harry Djachenko',
    author_email='i.s.djachenko@gmail.com',
    description='',
    entry_points={
        "console_scripts": [
            "parts = justin_utils.parts:__run",
            "sf = justin_utils.subfolder:__run",
        ]
    }
)
