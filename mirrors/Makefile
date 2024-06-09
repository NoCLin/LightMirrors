
.PHONY: check lint
check:
	black . --exclude .venv --check
	flake8 . --exclude=.venv
	mypy . --check-untyped-defs --exclude .venv
lint:
	black . --exclude .venv
