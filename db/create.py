import os
import sqlite3


if __name__ == '__main__':
    migration_scripts = []
    migration_script_names = [
        'leagues',
        'seasons',
        'teams',
    ]

    for migration in migration_script_names:
        script_name = f'create_{migration}.sql'
        script_path = os.path.join('sql', f'create_{migration}.sql')
        with open(script_path, 'r') as sql_script:
            migration_scripts.append((script_name, sql_script.read()))

    db_path = './rc.sqlite'
    if os.path.exists('./rc.sqlite'):
        os.remove('./rc.sqlite')

    with sqlite3.connect('./rc.sqlite') as conn:
        for name, sql in migration_scripts:
            print(f'running - {name}')

            cursor = conn.cursor()
            cursor.execute(sql)

            print(f'    * complete')
