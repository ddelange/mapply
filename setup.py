# ruff: noqa: D100
from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.absolute()

requirements_path = here / "requirements" / "prod.txt"

readme_path = here / "README.md"


def read_requirements(path: Path) -> list[str]:
    """Parse a requirements file much like pip does."""
    try:
        with path.open() as fp:
            return list(filter(None, (line.split("#")[0].strip() for line in fp)))
    except IndexError as exc:
        msg = f"{path} is broken"
        raise RuntimeError(msg) from exc


setup(
    name="mapply",
    description="Sensible multi-core apply function for Pandas",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    setup_requires=["setuptools_scm<7"],
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
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="pandas parallel apply multicore multiprocessing multiprocess dill",
    license="MIT",
)
