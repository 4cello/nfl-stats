import nfl_data_py as nfl

from prettytable import PrettyTable, MARKDOWN

import helpers


class CrossoverNFLSolver:
    df_pbp = None
    df_pt = None

    def on_team(self, team):
        if isinstance(team, str):
            team = [team]
        if isinstance(team, list):
            return lambda dfentry: len([t in dfentry for t in team if t in dfentry]) > 0
        raise TypeError("Team must be list or str")

    def td_from(self, qbid):
        passing_td_plays = self.df_pbp[
            (self.df_pbp.touchdown == 1) & (self.df_pbp.play_type == "pass")
        ]
        tds_from_qb = passing_td_plays[passing_td_plays.passer_player_id == qbid]
        td_players = tds_from_qb.drop_duplicates("td_player_id")[
            ["td_player_id"]
        ].rename(columns={"td_player_id": "player_id"})
        return td_players

    def filter_str(self, entry):
        if team := entry.get("team", None):
            if isinstance(team, list):
                team = team[0]
            return f"team={team}"
        if college := entry.get("college", None):
            return f"col={college}"
        if td_pid := entry.get("td_player_id", None):
            return f"rtdfrom={td_pid}"
        return str(entry)

    def filter_players(self, entry):
        if team := entry.get("team", None):
            return self.df_pt[self.df_pt.team.apply(self.on_team(team))]
        if college := entry.get("college", None):
            return self.df_pt[self.df_pt.college.apply(lambda x: college in x)]
        if td_qb := entry.get("td_from", None):
            return self.td_from(td_qb)
        raise ValueError("Filter not implemented")

    def find_candidates(
        self,
        rows: list[dict[str, str | int]],
        cols: list[dict[str, str | int]],
        years: list[int],
    ):
        self.df_pbp = helpers.import_pbp_data(
            years=years,
            columns=[
                "play_id",
                "game_id",
                "touchdown",
                "play_type",
                "passer_player_id",
                "td_player_id",
            ],
        )
        df_players = nfl.import_rosters(years=years)
        unique_players = df_players[["player_id", "player_name"]].drop_duplicates(
            subset=["player_id"]
        )

        def collect_list(x):
            return list(set(x))

        self.df_pt = df_players.groupby("player_id").agg(
            {
                "team": collect_list,
                "college": collect_list,
                "years_exp": "max",
                # "rookie_year": "max",
                # "draft_number": "max",
                "draft_club": collect_list,
            }
        )

        grid_rows = [self.filter_players(entry) for entry in rows]
        grid_cols = [self.filter_players(entry) for entry in cols]

        grid = {}
        for row, prow in zip(rows, grid_rows):
            for col, pcol in zip(cols, grid_cols):
                intersect = prow.merge(
                    pcol, how="inner", on=["player_id"], suffixes=[None, "_right"]
                )
                squarename = f"{self.filter_str(row)}/{self.filter_str(col)}"
                grid[squarename] = intersect.merge(unique_players, on=["player_id"])[
                    "player_name"
                ].to_list()

        return grid


if __name__ == "__main__":
    rows = [{"team": ["LA", "STL"]}, {"team": "JAX"}, {"college": "Alabama"}]
    cols = [{"team": "ATL"}, {"team": "ARI"}, {"team": "DAL"}]
    years = range(2015, 2023)

    grid = CrossoverNFLSolver().find_candidates(rows, cols, years)

    max_list_len = max([len(players) for players in grid.values()])

    table = PrettyTable()
    for square, players in grid.items():
        table.add_column(square, sorted(players) + [""] * (max_list_len - len(players)))
    table.align = "l"
    table.set_style(MARKDOWN)

    print(table)