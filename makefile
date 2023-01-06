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
	cd ./pipelines && make mypy
	cd ./db && make mypy
	cd ./app && make mypy