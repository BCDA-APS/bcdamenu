# Packaging Hints

## PyPI upload

Preceed the wildcard with tag text (with current version number `bcdamenu-2019.5.0*`)::

	python setup.py sdist bdist_wheel
	twine upload dist/bcdamenu-${CURRENT_RELEASE}*

## Conda upload

In the upload command below, use the text reported 
at (near) the end of a successful conda build.

	conda build ./conda-recipe/
	anaconda upload -u aps-anl-tag /home/mintadmin/Apps/anaconda/conda-bld/noarch/bcdamenu-${CURRENT_RELEASE}-py_0.tar.bz2

* `aps-anl-tag` production releases
* `aps-anl-dev` anything else, such as: pre-release, release candidates, or testing purposes
