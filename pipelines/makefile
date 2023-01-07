mlb-season-aggregates:
	python ./tasks/mlb/season_aggregates.py 2020 2021 2022

mlb-batter-aggregates:
	python ./tasks/mlb/battter_aggregates.py correca01

mlb-pitcher-aggregates:
	python ./tasks/mlb/pitcher_aggregates.py verlaju01

mlb-standings:
	python ./tasks/mlb/standings.py 2020 2021 2022

prefect:
	prefect orion start

mypy:
	mypy ./ --ignore-missing-imports