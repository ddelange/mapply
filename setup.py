from os import path
from setuptools import setup

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
    long_description=read_readme(readme_path),
    long_description_content_type="text/markdown",
    setup_requires=["setuptools_scm"],
    install_requires=read_requirements(requirements_path),
    use_scm_version={"write_to": "src/mapply/_version.py"},
    package_dir={"": "src"},
    author="ddelange",
    author_email="david@delange.dev",
    url="https://github.com/ddelange/mapply",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="pandas parallel apply map applymap multicore multiprocessing",
)
