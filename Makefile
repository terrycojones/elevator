XARGS := xargs $(shell test $$(uname) = Linux && echo -r)

test: pytest

pytest:
	env PYTHONPATH=. pytest

pytest-verbose:
	env PYTHONPATH=. pytest --capture=no

flake8:
	flake8 *.py */*.py test/*.py test/automated/*.py

wc:
	wc -l test/*.py elevator/*.py *.py

clean:
	find . -type d -name __pycache__ | $(XARGS) rm -r
	find . -type d -name .mypy_cache | $(XARGS) rm -r
