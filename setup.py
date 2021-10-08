from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

requirements_path = path.join(here, "requirements", "prod.txt")

readme_path = path.join(here, "README.md")


def read_requirements(path):
    try:
        with open(path, mode="rt", encoding="utf-8") as fp:
            return list(
                filter(None, [line.split("#")[0].strip() for line in fp])  # noqa:C407
            )
    except IndexError:
        raise RuntimeError("{} is broken".format(path))


def read_readme(path):
    with open(path, mode="rt", encoding="utf-8") as fp:
        return fp.read()


setup(
    name="mapply",
    description="Sensible multi-core apply/map/applymap functions for Pandas",
    long_description=read_readme(readme_path),
    long_description_content_type="text/markdown",
    setup_requires=["setuptools_scm"],
    install_requires=read_requirements(requirements_path),
    use_scm_version={"write_to": "src/mapply/_version.py"},
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author="ddelange",
    author_email="ddelange@delange.dev",
    url="https://github.com/ddelange/mapply",
    project_urls={
        "Documentation": "https://mapply.readthedocs.io",
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="pandas parallel apply map applymap multicore multiprocessing",
    license="MIT",
)
