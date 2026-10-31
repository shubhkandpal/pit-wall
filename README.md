# Pit Wall

An F1 strategy platform built on OpenF1 timing data (2023 onwards): a Bayesian
tyre-degradation model, a lap-by-lap race simulator for the whole field, an exact
dynamic-programming + Monte-Carlo strategy search, an incident engine for what-if
scenarios (safety cars, red flags, failures), and a live pit-wall app that follows
a race as it happens.

## Status
- [ ] v0.1 — Data foundation (OpenF1 → DuckDB, clean laps, baseline)
- [ ] v0.2 — Degradation model
- [ ] v0.3 — Strategy core (simulator, optimiser# Pit Wall

An F1 strategy platform built on OpenF1 timing data (2023 onwards): a Bayesian
tyre-degradation model, a lap-by-lap race simulator for the whole field, an exact
dynamic-programming + Monte-Carlo strategy search, an incident engine for what-if
scenarios (safety cars, red flags, failures), and a live pit-wall app that follows
a race as it happens.

## Status
- [ ] v0.1 — Data foundation (OpenF1 → DuckDB, clean laps, baseline)
- [ ] v0.2 — Degradation model
- [ ] v0.3 — Strategy core (simulator, optimiser, safety-car re-planning)
- [ ] v0.4 — Research results (model vs the pit wall, 2026 rule change)
- [ ] v0.5 — Multi-car simulator
- [ ] v0.6 — Scenario engine
- [ ] v0.7 — Live engine
- [ ] v1.0 — Pit-wall app

## Setup
    uv venv --python 3.12 && source .venv/bin/activate
    uv pip install -e ".[dev]"
    pre-commit install
    pytest

Data: [OpenF1](https://openf1.org). Not affiliated with Formula 1, the FIA or any team.
