VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ENV := .env

.PHONY: venv install topic producer alerts stats

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

topic:
	./scripts/create_topic.sh

producer:
	$(PY) app/producer.py

alerts:
	$(PY) app/consumer_alerts.py

stats:
	$(PY) app/consumer_stats.py
