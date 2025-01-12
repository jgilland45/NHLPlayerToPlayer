import create_tables
import db_getters

def run():
    dbpath = "testdb.db"
    create_tables.connect(dbpath)

    mcdavid_teammates = db_getters.get_reg_and_playoff_teammates_of_player(8478402)

    gretzky_teammates = db_getters.get_reg_and_playoff_teammates_of_player(8447400)

    # bedard_teammates = db_getters.get_reg_and_playoff_teammates_of_player(8484144)

    # howe_teammates = db_getters.get_reg_and_playoff_teammates_of_player(8448000)

    connected = False

    while not connected:
        common_teammates = set(mcdavid_teammates).intersection(gretzky_teammates)
        if len(common_teammates) > 0:
            print(common_teammates)
            connected = True
        else:
            # find teammates of teammates
            for teammate in mcdavid_teammates:
                teammates_of_teammate = db_getters.get_reg_and_playoff_teammates_of_player(teammate)
                mcdavid_teammates.extend(teammates_of_teammate)
                common_teammates = set(teammates_of_teammate).intersection(gretzky_teammates)
                if len(common_teammates) > 0:
                    print(f"From teammate {db_getters.get_name_from_playerid(teammate)}: {[db_getters.get_name_from_playerid(x) for x in common_teammates]}")
                    connected = True


if __name__ == "__main__":
    run()