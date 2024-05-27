import sqlite3

def export_table_to_sql(db_path, table_name, sql_file_path):
    conn = sqlite3.connect(db_path)
    with open(sql_file_path, 'w') as f:
        for line in conn.iterdump():
            if line.startswith('INSERT INTO "{}"'.format(table_name)):
                f.write('%s\n' % line)
    conn.close()

def import_sql_to_db(sql_file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(sql_file_path, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

# Example usage:
source_db = 'umsatz_bkup.db'
target_db = 'umsatz.db'

tables_to_migrate = ['kategorie_schlagwoerter', 'KATEGORIEN']

for table in tables_to_migrate:
    sql_file = f'{table}_backup.sql'
    export_table_to_sql(source_db, table, sql_file)
    import_sql_to_db(sql_file, target_db)