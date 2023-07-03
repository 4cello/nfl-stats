import nfl_data_py as nfl
import pandas as pd
import plotly.express as px

def filter_3long(pbp):
    down = pbp["down"] == 3
    dist = pbp["ydstogo"] > 5
    season = pbp["season_type"] == "REG"
    pbp = pbp[down & dist & season]

    pass_agg = (
        pbp.groupby(["passer_player_id"], as_index=False)
        .agg({"third_down_converted": "sum", "third_down_failed": "sum"})
    )

    pass_agg["attempts"] = pass_agg.third_down_failed + pass_agg.third_down_converted
    pass_agg["conv_pct"] = pass_agg.third_down_converted / pass_agg.attempts

    pass_agg = pass_agg[pass_agg.third_down_failed + pass_agg.third_down_converted >= 0]

    run_agg = (
        pbp.groupby(["rusher_player_id"], as_index=False)
        .agg({"third_down_converted": "sum", "third_down_failed": "sum"})
    )

    run_agg["attempts"] = run_agg.third_down_failed + run_agg.third_down_converted
    run_agg["conv_pct"] = run_agg.third_down_converted / run_agg.attempts

    pass_run = pass_agg.merge(run_agg, left_on="passer_player_id", right_on="rusher_player_id", suffixes=["_pass", "_run"])
    pass_run.drop(columns=["rusher_player_id"], inplace=True)
    pass_run["total_success"] = pass_run.third_down_converted_pass + pass_run.third_down_converted_run
    pass_run["total_fail"] = pass_run.third_down_failed_pass + pass_run.third_down_failed_run
    pass_run["total_attempts"] = pass_run.attempts_pass + pass_run.attempts_run
    pass_run["total_conv_pct"] = pass_run.total_success / pass_run.total_attempts * 100

    pass_run["rank_pass"] = pass_run.conv_pct_pass.rank(ascending=False)
    pass_run["rank_run"] = pass_run.conv_pct_run.rank(ascending=False)
    pass_run["rank_total"] = pass_run.total_conv_pct.rank(ascending=False)
    pass_run["rank_diff_pass_total"] = pass_run.rank_total - pass_run.rank_pass

    pass_run.rename(columns={"passer_player_id": "player_id", "possession_team_pass": "team_abbr"}, inplace=True)

    return pass_run

def main():
    pbpcolumns = ["play_id", "game_id", "down", "ydstogo", "play_type", "third_down_converted", "third_down_failed", "passer_player_id", "rusher_player_id", "passer_player_name", "rusher_player_name", "qb_dropback", "qb_scramble", "desc", "season_type"]
    playercolumns = []
    pbp_2021 = nfl.import_pbp_data(years=[2021], columns=pbpcolumns)
    pbp_2022 = nfl.import_pbp_data(years=[2022], columns=pbpcolumns)
    df_players = nfl.import_rosters(years=[2022])
    df_teams = nfl.import_team_desc()

    pbp_2021 = filter_3long(pbp_2021)
    pbp_2022 = filter_3long(pbp_2022)

    merge_cols = ["player_id", "attempts_pass", "conv_pct_pass"]

    comparison = pd.merge(pbp_2022[merge_cols], pbp_2021[merge_cols], how="left", on=["player_id"], suffixes=["_2022", "_2021"])
    comparison["total_attempts"] = comparison.attempts_pass_2021 + comparison.attempts_pass_2022
    comparison.dropna(inplace=True)
    comparison = comparison[comparison.total_attempts > 50]
    comparison = comparison.merge(df_players[["player_id", "player_name", "team"]])


    color_dict = {k:v["team_color"] for k,v in df_teams.set_index("team_abbr").T.to_dict().items()}

    #fig = px.scatter(pbp_2022, x="conv_pct_pass", y="conv_pct_run", color="team_abbr", color_discrete_map=color_dict, text="player_name", size="total_attempts", hover_data=["player_name", "attempts_pass", "attempts_run"])
    fig = px.scatter(comparison, x="conv_pct_pass_2022", y="conv_pct_pass_2021", color="team", color_discrete_map=color_dict, text="player_name", size="total_attempts", hover_data=["player_name"], trendline="ols", trendline_scope="overall")
    fig.update_traces(textposition="bottom center")
    fig.show()

    cols = nfl.see_pbp_cols()
    for col in cols:
        print(col)

if __name__ == "__main__":
    main()