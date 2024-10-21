import sqlite3


async def add_entry(timestamp: str, query: str, is_regen: bool):
    connection = sqlite3.connect("data/main.db")
    cursor = connection.cursor()

    values_dict = {'timestamp': timestamp,
                   'query': query,
                   'is_regeneration': 1 if is_regen else 0
                   }

    values_str = ""

    for key in values_dict.keys():
        values_str += f":{key},"

    # Remove the last comma
    values_str = values_str[:-1]

    cursor.execute(
        f"""
        INSERT INTO stats(timestamp, query, is_regeneration)
        VALUES ({values_str})""",
        values_dict)

    connection.commit()
    connection.close()


async def get_data():
    connection = sqlite3.connect("data/main.db")
    connection.row_factory = sqlite3.Row
    rows: list[sqlite3.Row] = connection.execute("""SELECT *
                                    FROM stats
                                    """).fetchall()

    connection.close()

    # Convert list of sqlite3.Row objects to list of dictionaries
    dicts: list[dict] = [dict(row) for row in rows]

    return dicts




