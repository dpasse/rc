import sqlite3

from common.loaders import seasons, leagues, conferences, divisions, teams


if __name__ == '__main__':
    data_directory = '../data/'
    database_path = '../app/rc.sqlite'
    data_migrations = [
        ('insert_seasons', seasons.execute),
        ('insert_leagues', leagues.execute),
        ('insert_conferences', conferences.execute),
        ('insert_divisions', divisions.execute),
        ('insert_teams', teams.execute),
    ]

    for label, method in data_migrations:

        with sqlite3.connect(database_path) as conn:
            print(f'running - {label}')

            cursor = conn.cursor()
            for i, script in enumerate(method(data_directory)):
                print(f'    * running {i + 1} script')

                cursor.execute(script)

            print(f'    * complete')