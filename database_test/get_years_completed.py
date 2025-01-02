import create_tables
import data_pipeline

def get_is_year_complete(year):
    year_tag = str(year) + "%"
    create_tables.cursor.execute("""
        SELECT count(distinct(gameid))
        FROM Player_Game pg
        WHERE gameid like ?;
    """, (year_tag, ))
    num_games_tracked = create_tables.cursor.fetchone()
    create_tables.cursor.execute("""
        SELECT count(distinct(gameid))
        FROM Games g
        WHERE gameid like ?;
    """, (year_tag, ))
    num_games = create_tables.cursor.fetchone()
    return num_games_tracked[0] == num_games[0]

def run():
    dbpath = "testdb.db"
    create_tables.connect(dbpath)

    years = data_pipeline.get_all_years()

    for year in years:
        year_complete = get_is_year_complete(int(str(year)[0:4]))
        if not year_complete:
            print(year)



if __name__ == "__main__":
    run()