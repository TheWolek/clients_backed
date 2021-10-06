import mysql.connector


def DB_clearTable(table):
    if table == "creds_backup":
        return False

    sql = "DELETE FROM " + table

    cnx = mysql.connector.connect(
        user='root', password='132', host='localhost', database='clients')
    cur = cnx.cursor(dictionary=True)

    print("clearing table", table)
    cur.execute(sql)
    cnx.commit()
    cnx.close()
    return True


def DB_backupTable(table):
    backupTable = table + "_backup"
    print("started backup of table", table, "into", backupTable)
    if DB_clearTable(backupTable):
        sql = "INSERT INTO " + backupTable + " SELECT * FROM " + table
        cnx = mysql.connector.connect(
            user='root', password='132', host='localhost', database='clients')
        cur = cnx.cursor(dictionary=True)

        cur.execute(sql)
        cnx.commit()
        cnx.close()
        return True
    else:
        return False


def DB_query(query: str, values=None):  # master function for DB interaction
    try:
        cnx = mysql.connector.connect(
            user='root', password='132', host='localhost', database='clients')
        cur = cnx.cursor(dictionary=True)

        if query[:6] == "SELECT":
            cur.execute(query, values)
            cnx.close()
            return {"status": 1, "data": cur.fetchall()}

        if query[:6] == "DELETE":
            # backup
            table = query[7:].split(" ")[1]
            if table == "creds":
                return {"status": 0}

            print("##### Started backup of table", table)
            cur.callproc('proc_backup')

            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            return {"status": cur.rowcount}

        if query[:6] == "INSERT":
            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            return {"status": cur.rowcount, "ID": cur.lastrowid}

        if query[:6] == "UPDATE":
            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            if cur.rowcount == 0:
                return {"status": 0}

            return {"status": 1}

        return {"status": 0}
    except mysql.connector.Error as err:
        print(err)
