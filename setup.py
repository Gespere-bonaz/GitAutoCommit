from setuptools import setup, find_packages

setup(
    name="gitobserver",  # Nom du package sur PyPI
    version="0.2.0",  # Version initiale
    author="K2pme",
    author_email="cmantsila0@gmail.com",
    description="Automotic Git tool for file commiting",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/k2pme/gitobserver",
    packages=find_packages(),  # Trouve automatiquement les modules
    install_requires=[
        "watchdog",
        "colorama",
        "win10toast"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "git_observer=git_observer.main:start_watcher",
        ],
    },
)
