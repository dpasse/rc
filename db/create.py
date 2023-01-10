import os
import sqlite3


DB_PATH = '../app/rc.sqlite'

if __name__ == '__main__':
    migration_scripts = []
    migration_script_names = [
        'seasons',
        'leagues',
        'conferences',
        'divisions',
        'teams',
    ]

    for migration in migration_script_names:
        script_name = f'create_{migration}.sql'
        script_path = os.path.join('sql', f'create_{migration}.sql')
        with open(script_path, 'r', encoding='utf8') as sql_script:
            migration_scripts.append((script_name, sql_script.read()))

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with sqlite3.connect(DB_PATH) as conn:
        for name, sql in migration_scripts:
            print(f'running - {name}')

            cursor = conn.cursor()
            cursor.execute(sql)

            print('    * complete')
