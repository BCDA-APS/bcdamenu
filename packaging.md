# Packaging Hints

## PyPI upload

Set the current release::

	CURRENT_RELEASE=2019.05.0

Build and upload to PyPI::
	
	python setup.py sdist bdist_wheel
	twine upload dist/BcdaMenu-${CURRENT_RELEASE}*

## Conda upload

Build and upload to anaconda.org.

	conda build ./conda-recipe/
	anaconda upload -u aps-anl-tag /home/mintadmin/Apps/anaconda/conda-bld/noarch/bcdamenu-${CURRENT_RELEASE}-py_0.tar.bz2

* `aps-anl-tag` production releases
* `aps-anl-dev` anything else, such as: pre-release, release candidates, or testing purposes
