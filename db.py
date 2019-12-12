import sqlite3

class Database:
    conn = None

    def __init__(self, db_location):
        self.conn = sqlite3.connect(db_location, check_same_thread=False)

    def create(self, table, column, data):
        # Create new entry on a table
        cur = self.conn.cursor()
        sql_comm = 'INSERT INTO {} ({}) VALUES ('.format(table, ','.join(column))
        for col in column[1:]:
            sql_comm += '?,'
        sql_comm += '?)'
        cur.execute(sql_comm, data)
        self.conn.commit()
        cur.close()

    def read(self, table, column='*', where=()):
        # Default is to take all rows in the table
        # Default is to have no conditions
        # Returns entries from the table
        cur = self.conn.cursor()
        sql_comm = 'SELECT '
        if column == '*':
            sql_comm += column
        else:
            sql_comm += (','.join(column))
        sql_comm += (' FROM ' + table)
        if where != ():
            sql_comm += ' WHERE '
            for col, val in where[1:]:
                sql_comm += (col + ' = ? AND ')
            sql_comm += (where[0][0] + ' = ?')
            cur.execute(sql_comm, tuple(w[1] for w in where))
        else:
            cur.execute(sql_comm)
        results = cur.fetchall()
        cur.close()
        return results

    def update(self, table, edit_id, column, new_data):
        # Update row/s where edit_id = id
        cur = self.conn.cursor()
        sql_comm = 'UPDATE ' + table + ' SET '
        for col in column[1:]:
            sql_comm += (col + ' = ?,')
        sql_comm += (column[0] + ' = ? WHERE id = ?')
        cur.execute(sql_comm, (*(*new_data[1:], new_data[0]), edit_id))
        self.conn.commit()
        cur.close()

    def delete(self, table, edit_id='-1'):
        # Default is to delete all records in the table (-1)
        # Delete row where edit_id = id
        cur = self.conn.cursor()
        if edit_id == '-1':
            cur.execute('DELETE FROM ' + table)
        else:
            cur.execute('DELETE FROM ' + table + ' WHERE id = ' + edit_id)
        self.conn.commit()
        cur.close()