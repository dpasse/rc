import sys
import sqlite3

# pylint: disable=C0413

from find import root
sys.path.append(root())

from mushbeard.db.loaders import seasons, leagues, conferences, divisions, teams


DATA_DIRECTORY = '../data/'
DATABASE_PATH = '../app/rc.sqlite'

if __name__ == '__main__':
    data_migrations = [
        ('insert_seasons', seasons.execute),
        ('insert_leagues', leagues.execute),
        ('insert_conferences', conferences.execute),
        ('insert_divisions', divisions.execute),
        ('insert_teams', teams.execute),
    ]

    for label, method in data_migrations:
        with sqlite3.connect(DATABASE_PATH) as conn:
            print(f'running - {label}')

            cursor = conn.cursor()
            for i, script in enumerate(method(DATA_DIRECTORY)):
                print(f'    * running {i + 1} script')

                cursor.execute(script)

            print('    * complete')
