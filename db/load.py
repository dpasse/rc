import sqlite3

# pylint: disable=C0413

from setup_module import append_path

append_path()
from mushbeard.db.loaders import get_loaders


DATA_DIRECTORY = '../data/'
DATABASE_PATH = '../app/rc.sqlite'

if __name__ == '__main__':
    for label, method in get_loaders():
        with sqlite3.connect(DATABASE_PATH) as conn:
            print(f'running - {label}')

            cursor = conn.cursor()
            for i, script in enumerate(method(DATA_DIRECTORY)):
                print(f'    * running {i + 1} script')

                cursor.execute(script)

            print('    * complete')
