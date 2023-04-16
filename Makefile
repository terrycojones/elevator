XARGS := xargs $(shell test $$(uname) = Linux && echo -r)

test: pytest

pytest:
	env PYTHONPATH=. pytest

pytest-verbose:
	env PYTHONPATH=. pytest --capture=no

flake8:
	find . -name '*.py' | $(XARGS) flake8

wc:
	find . -name '*.py' | $(XARGS) wc -l

clean:
	find . -type d -name __pycache__ | $(XARGS) rm -r
	find . -type d -name .mypy_cache | $(XARGS) rm -r
