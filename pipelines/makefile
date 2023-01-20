mlb-season-batter-aggregates:
	python ./tasks/mlb/season_aggregates.py batting 2020 2021 2022

mlb-season-pitcher-aggregates:
	python ./tasks/mlb/season_aggregates.py pitching 2020 2021 2022

mlb-standings:
	python ./tasks/mlb/standings.py 2020 2021 2022

mlb-schedule:
	python ./tasks/mlb/schedules.py -l "../data/mlb/inputs/schedules.csv"

mlb-pbp-download:
	python ./tasks/mlb/pbp_download.py -l "../data/mlb/inputs/games.csv"

mlb-pbp-parse:
	python ./tasks/mlb/pbp_parse.py

mlb-batter-aggregates:
	python ./tasks/mlb/player_aggregates.py batting correca01

mlb-pitcher-aggregates:
	python ./tasks/mlb/player_aggregates.py pitching verlaju01

mlb-dump-entities:
	python ./tasks/mlb/dump_entities.py

mlb-compute-states:
	python ./tasks/mlb/compute_states.py

prefect:
	prefect orion start

mypy:
	mypy ./ --ignore-missing-imports