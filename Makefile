VENV  := .venv
PY    := $(VENV)/bin/python
MK    := $(VENV)/bin/mkdocs
# Path to the docusketch-mobile worktree that holds the iOS 26 baselines.
MOBILE ?= $(HOME)/Developer/docusketch-mobile-help-screens

.PHONY: setup screens figures build serve deploy clean

setup:                ## create venv + install deps
	python3 -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt

screens:              ## copy the iOS 26 baselines this site needs into docs/assets/raw
	tools/pull-screens.sh $(MOBILE)

figures:              ## build every composite from figures/*.yml
	$(PY) tools/compose.py figures/*.yml

build:                ## render the static site into ./site
	$(MK) build

serve:                ## local preview at http://127.0.0.1:8000
	$(MK) serve

deploy:               ## publish to GitHub Pages (gh-pages branch) — run only when approved
	$(MK) gh-deploy --force

clean:
	rm -rf site
