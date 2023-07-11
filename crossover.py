import nfl_data_py as nfl

from prettytable import PrettyTable

df_pbp = None
df_pt = None

def on_team(team):
    if isinstance(team, str):
        team = [team]
    if isinstance(team, list):
        return lambda dfentry: len([t in dfentry for t in team if t in dfentry]) > 0
    raise TypeError("Team must be list or str")

def td_from(qbid):
    passing_td_plays = df_pbp[(df_pbp.touchdown == 1) & (df_pbp.play_type == "pass")]
    tds_from_qb = passing_td_plays[passing_td_plays.passer_player_id == qbid]
    td_players = tds_from_qb.drop_duplicates("td_player_id")[["td_player_id"]].rename(columns={"td_player_id": "player_id"})
    return td_players

def create_filter(entry):
    if team := entry.get("team", None):
        return on_team(team)
    if td_qb := entry.get("td_from", None):
        return td_from(td_qb)
    
def filter_str(entry):
    if team := entry.get("team", None):
        if isinstance(team, list):
            team = team[0]
        return f"team={team}"
    return str(entry)

def filter_players(entry):
    if team := entry.get("team", None):
        return df_pt[df_pt.team.apply(on_team(team))]
    if td_qb := entry.get("td_from", None):
        return td_from(td_qb)
    raise ValueError("Filter not implemented")

def main():
    global df_pbp, df_pt
    df_pbp = nfl.import_pbp_data(years=range(2017,2023), columns=["play_id", "game_id", "touchdown", "play_type", "passer_player_id", "td_player_id"])
    df_players = nfl.import_rosters(years=range(2015,2023))
    unique_players = df_players[["player_id", "player_name"]].drop_duplicates(subset=["player_id"])

    df_pt = df_players.groupby("player_id").agg({"team": lambda x: list(set(x))})

    #with_names = grouped.merge(unique_players, left_on="player_id", right_on="player_id")

    brees_id = "00-0020531"


    rows = [{"team": ["CLE", "CLV"]}, {"team": ["LV","OAK"]}, {"td_from": brees_id}]
    cols = [{"team": "MIA"}, {"team": "NE"}, {"team": "BAL"}]

    grid_rows = [filter_players(entry) for entry in rows]
    grid_cols = [filter_players(entry) for entry in cols]

    grid = {}
    for row,prow in zip(rows, grid_rows):
        for col,pcol in zip(cols, grid_cols):
            intersect = prow.merge(pcol, how="inner", on=["player_id"], suffixes=[None, "_right"])
            grid[f"{filter_str(row)}/{filter_str(col)}"] = intersect.merge(unique_players, on=["player_id"])["player_name"].to_list()

    max_list = max([len(players) for players in grid.values()])

    table = PrettyTable()
    for square,players in grid.items():
        table.add_column(square, players + [""] * (max_list - len(players)))
    print(table)

if __name__ == "__main__":
    main()