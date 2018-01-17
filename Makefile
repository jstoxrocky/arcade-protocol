clean-pycache:
	rm -rf tests/__pycache__
	rm -rf __pycache__

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .cache

clean: clean-pycache clean-build