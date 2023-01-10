mlb-season-batter-aggregates:
	python ./tasks/mlb/season_aggregates.py batting 2020 2021 2022

mlb-season-pitcher-aggregates:
	python ./tasks/mlb/season_aggregates.py pitching 2020 2021 2022

mlb-standings:
	python ./tasks/mlb/standings.py 2020 2021 2022

mlb-schedule:
	python ./tasks/mlb/schedules.py 2022 ari

mlb-pbp:
	python ./tasks/mlb/pbp.py 401356045

mlb-batter-aggregates:
	python ./tasks/mlb/player_aggregates.py batting correca01

mlb-pitcher-aggregates:
	python ./tasks/mlb/player_aggregates.py pitching verlaju01

prefect:
	prefect orion start

mypy:
	mypy ./ --ignore-missing-imports