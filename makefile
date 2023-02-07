run:
	flask run

freeze:
	pip freeze > requirements.txt

webpack-build:
	npx webpack build --config webpack.config.js --mode production

webpack-watch-prod:
	npx webpack watch --config webpack.config.js --mode production

webpack-watch-dev:
	npx webpack watch --config webpack.config.js

mypy:
	cd ./pipelines && mypy ./ --ignore-missing-imports
	cd ./db && mypy ./ --ignore-missing-imports
	cd ./app && mypy ./ --ignore-missing-imports
	cd ./mushbeard && mypy ./ --ignore-missing-imports

test:
	cd ./mushbeard && pytest -v -s

pylint:
	find . -type f -not -path "./rc/*" -name "*.py" | xargs pylint

lint:
	make pylint
