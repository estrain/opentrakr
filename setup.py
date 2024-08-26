from setuptools import setup, find_packages

setup(
    name="opentrakr",
    version="0.1.0",
    author="Errol Strain",
    author_email="estrain@gmail.com",
    description="A package for downloading TSV files from the NCBI FTP site.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/estrain/opentrakr",  # Update this with your actual repository URL
    packages=find_packages(),
    py_modules=["ncbi_tsv_download"],
    entry_points={
        'console_scripts': [
            'ncbi_tsv_download=ncbi_tsv_download:main',
        ],
    },
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        # If you have additional files, specify them here
    },
)

