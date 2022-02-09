"""Setup script for the Tauk package"""

from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def main():
    """Executes setup when this script is the top-level"""
    import tauk as app

    setup(
        name=app.__project__,
        version=app.__version__,
        description=app.__doc__,
        long_description=read('README.md'),
        classifiers=app.__classifiers__,
        author=app.__author__,
        url=app.__url__,
        license=[
            c.rsplit('::', 1)[1].strip()
            for c in app.__classifiers__
            if c.startswith('License ::')
        ][0],
        packages=find_packages(),
        include_package_data=True,
        platforms=app.__platforms__,
        install_requires=app.__requires__,
        extras_require=app.__extra_requires__,
    )


if __name__ == '__main__':
    main()
