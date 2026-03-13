UNIT_IGNORE = --ignore=tests/test_docker_integration.py \
              --ignore=tests/test_FAIL_demo_scoring.py \
              --ignore=tests/test_FAIL_demo_services.py \
              --ignore=tests/test_FAIL_demo_api.py

.PHONY: test cov watch fail status

# Run all unit tests
test:
	python -m pytest tests/ $(UNIT_IGNORE) -v

# Run with coverage report
cov:
	python -m pytest tests/ $(UNIT_IGNORE) --cov=app --cov-report=term-missing

# TDD watch mode — re-runs on file change (requires pytest-watch: pip install pytest-watch)
watch:
	ptw -- tests/ $(UNIT_IGNORE) --tb=short -q

# Run just a specific test file: make run F=tests/test_news_api.py
run:
	python -m pytest $(F) -v

# Show intentional failures (demonstrates tests are failable)
fail:
	python -m pytest tests/test_FAIL_demo_scoring.py tests/test_FAIL_demo_services.py tests/test_FAIL_demo_api.py -v

# Check which external APIs are up right now
status:
	curl -s http://localhost:8000/api/v1/status | python3 -m json.tool
