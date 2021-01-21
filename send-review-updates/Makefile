include ../Makefile.common

# Parameters for "gcloud function deploy ..."
# ATTENTION Don't surround values with quotes! GOOD: DEPLOY_NAME = my_function_name - BAD: DEPLOY_NAME = "my_function_name"
# DEPLOY_ARGS can be adjusted as fits, potentially even be empty
DEPLOY_NAME =
DEPLOY_REGION =
DEPLOY_PROJECT_ID =
DEPLOY_ARGS = --trigger-topic example-topic --runtime python38 --memory 128 --timeout 15 --max-instances 1

.DEFAULT_GOAL := 
.PHONY: prepare
prepare: $(DIR_EMPTY)/pypi-deps $(DIR_LOCAL_DEPS)

# TODO Execute tests
# .PHONY: test
# test: $(DIR_EMPTY)/prepare
