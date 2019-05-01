from setuptools import setup

setup(
    name="completion_utils",
    version="0.0.1",
    author="Carvell Scott",
    author_email="carvell.scott@gmail.com",
    keywords=["bash completion", "complete", "autocomplete", "auto-complete"],
    py_modules=["completion_utils"],
    url="https://github.com/CarvellScott/completion_utils",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    description=(
        "A set of functions intended to make writing shell completion "
        "functions lot easier by letting you write them via python."
    ),
    include_package_data=True,
    long_description=open("long_description.md").read(),
    long_description_content_type="text/markdown"
)
