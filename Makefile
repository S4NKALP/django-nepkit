test:
	DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/

coverage:
	DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/ --cov=django_nepkit --cov-report=term --cov-report=xml

coverage-html:
	DJANGO_SETTINGS_MODULE=django_nepkit.tests.settings uv run pytest django_nepkit/tests/ --cov=django_nepkit --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	rm -rf .pytest_cache .coverage htmlcov coverage.xml
