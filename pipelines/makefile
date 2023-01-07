mlb-season-aggregates:
	python ./tasks/mlb/season_aggregates.py 2020 2021 2022

mlb-player-aggregates:
	python ./tasks/mlb/player_aggregates.py correca01

mlb-standings:
	python ./tasks/mlb/standings.py 2020 2021 2022

prefect:
	prefect orion start

mypy:
	mypy ./ --ignore-missing-imports