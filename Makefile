.PHONY: clean clean-pyc clean-test help

help:
	@echo "clean - remove all test and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test artifacts"
	
clean: clean-pyc clean-test

clean-pyc:
	find . -name '*~' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.eggs' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf .pytest_cache
