from pybaseball import statcast
import pandas as pd

def cleanup_df(df):
    stats_df = df
    #################################### Only keep the stats that we want to track ####################################
    stats_df = stats_df.loc[:, ['game_date', 'pitcher', 'pitch_type', 'release_speed', 'release_spin_rate', 'pfx_x',
                                'pfx_z', 'zone', 'batter', 'events', 'launch_speed', 'bb_type', 'hit_distance_sc']]

    ########## Get rid of rows where a pitch was not actually thrown including intentional walks (NaN values) ##########
    stats_df = stats_df.query('not pitch_type.isna()')

    ############################################### Handle Unknown Speed ###############################################
    # convert this column to object so it can handle changing from float to str
    stats_df['release_speed'] = stats_df['release_speed'].astype(object)

    # If there is an error reading the speed, change the column to say unknown speed
    stats_df.loc[stats_df['release_speed'].isna(), 'release_speed'] = 'Unknown Speed'

    return stats_df

def add_calc_cols(df):
    stats_df = df

    # stats_df.
    # TODO

    return stats_df

def main():

    stats_df = statcast()      # get yesterday's stats

    if stats_df.empty:
        print("No games yesterday. Defaulting to 2025 world series")
        stats_df = statcast(start_dt="2025-10-24", end_dt="2025-11-01")     # default to last year's world series (2025)


    stats_df = cleanup_df(stats_df)
    stats_df = add_calc_cols(stats_df)

    print(f"info: {stats_df.info()}")
    print(f"shape: {stats_df.shape}")
    print(f"columns: {stats_df.columns.tolist()}")
    print(f"DF: {stats_df.to_string()}")

    pass

if __name__ == '__main__':
    main()