import mysql.connector


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
