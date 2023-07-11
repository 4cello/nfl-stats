import nfl_data_py as nfl

def import_pbp_data(**kwargs):
    try:
        return nfl.import_pbp_data(cache=True, **kwargs)
    except ValueError:
        print("")
        return nfl.import_pbp_data(**kwargs)
