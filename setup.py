from setuptools import find_packages, setup

setup(
    name='digasm',
    version='0.0.1',
    author='lausek',
    description='headless interface for the Digital simulator',
    url='https://github.com/lausek/digital-asm-headless',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['digasm=src.__main__:main']
    }
)
