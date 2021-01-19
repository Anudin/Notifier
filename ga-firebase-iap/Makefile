# Parameters for "gcloud function deploy ..."
# ATTENTION Don't surround values with quotes! GOOD: DEPLOY_NAME = my_function_name - BAD: DEPLOY_NAME = "my_function_name"
# DEPLOY_ARGS can be adjusted as fits, potentially even be empty
DEPLOY_NAME = on_in_app_purchase
DEPLOY_REGION =
DEPLOY_PROJECT_ID =
DEPLOY_ARGS = --trigger-event providers/google.firebase.analytics/eventTypes/event.log \
							--trigger-resource projects/$(DEPLOY_PROJECT_ID)/events/in_app_purchase \
							--runtime python38 --memory 128 --timeout 15 --max-instances 1

# See https://tech.davis-hansson.com/p/make/
# === PREAMBLE START
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >
# === PREAMBLE END

# This script uses empty targets, define a folder which can be conveniently ignored in version control / deployment
# See https://www.gnu.org/software/make/manual/html_node/Empty-Targets.html
EMPTY := .empty-targets

# Default - top level rule is what gets executed when you run just `make`
.PHONY: prepare
prepare: $(EMPTY)/prepare

$(EMPTY)/prepare: shared $(EMPTY)/pypi-deps
> touch $@

# TODO Find a better name. Used for private (non PyPI) and / or local dependencies. Adjust imports & ignore files.
shared: $(shell find ../shared -type f)
> cp -r $(?D) .
> touch $@

# Why "pip install wheel"?
# See https://stackoverflow.com/questions/34819221/why-is-python-setup-py-saying-invalid-command-bdist-wheel-on-travis-ci
$(EMPTY)/pypi-deps: requirements.txt | .venv $(EMPTY)
> source .venv/bin/activate
> pip install --no-cache-dir wheel
> pip install --no-cache-dir -r requirements.txt
> touch $@

.venv: 
> python3 -m venv .venv

# TODO Execute tests
# .PHONY: test
# test: $(EMPTY)/prepare

# TODO Add test to prerequisites
.PHONY: deploy
deploy: shared
> gcloud functions deploy $(DEPLOY_NAME) \
>   --region $(DEPLOY_REGION) \
>   --project $(DEPLOY_PROJECT_ID) \
>   $(DEPLOY_ARGS)

$(EMPTY):
> mkdir $(EMPTY)
