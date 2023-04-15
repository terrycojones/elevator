XARGS := xargs $(shell test $$(uname) = Linux && echo -r)

pytest:
	env PYTHONPATH=. pytest --capture=no

wc:
	wc -l test/*.py elevated/*.py *.py

clean:
	find . -type d -name __pycache__ | $(XARGS) rm -r
	find . -type d -name .mypy_cache | $(XARGS) rm -r
