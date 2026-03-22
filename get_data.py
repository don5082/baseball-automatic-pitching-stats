import numpy as np
from pybaseball import statcast
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv
import pitches as pitch
import sqlalchemy as sqla
from sqlalchemy.dialects.mysql import insert
import logging


"""
    This function drops unnecessary columns of data
    
    It is part of the Transform step

    :returns the updated dataframe
"""
def cleanup_df(df):
    stats_df = df
    #################################### Only keep the stats that we want to track ####################################
    stats_df = stats_df.loc[:, ['game_date', 'pitcher', 'pitch_type', 'release_speed', 'release_spin_rate', 'pfx_x',
                                'pfx_z', 'zone', 'pitch_number', 'batter', 'events', 'launch_speed', 'bb_type',
                                'hit_distance_sc', 'game_pk']]

    ########## Get rid of rows where a pitch was not actually thrown including intentional walks (NaN values) ##########
    stats_df = stats_df.query('not pitch_type.isna()')

    ############################################### Handle Unknown Speed ###############################################
    # convert this column to object so it can handle changing from float to str
    stats_df['release_speed'] = stats_df['release_speed'].astype(object)

    # If there is an error reading the speed, change the column to say unknown speed
    stats_df.loc[stats_df['release_speed'].isna(), 'release_speed'] = 'Unknown Speed'

    return stats_df


"""
    This function calculates whether or not a pitch is above average, below average, or average in terms
    of pitch breakage. It takes both vertical and horizontal breakage into consideration 
    
    It is part of the Transform step

    :returns the updated dataframe
"""
def add_calc_cols(df):
    stats_df = df

    # Add a column for intensity of the movement of a pitch, based on the pitch type

    # pfx_x = Horizontal Break
    # pfx_z = Vertical Break

    conditions = [
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.FF.avg_hb[1])) & (stats_df['pitch_type'] == "FF")) |  # above avg
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.FF.avg_vb[1])) & (stats_df['pitch_type'] == "FF")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.SI.avg_hb[1])) & (stats_df['pitch_type'] == "SI")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.SI.avg_vb[1])) & (stats_df['pitch_type'] == "SI")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.FC.avg_hb[1])) & (stats_df['pitch_type'] == "FC")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.FC.avg_vb[1])) & (stats_df['pitch_type'] == "FC")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.SL.avg_hb[1])) & (stats_df['pitch_type'] == "SL")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.SL.avg_vb[1])) & (stats_df['pitch_type'] == "SL")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.ST.avg_hb[1])) & (stats_df['pitch_type'] == "ST")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.ST.avg_vb[1])) & (stats_df['pitch_type'] == "ST")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.CU.avg_hb[1])) & (stats_df['pitch_type'] == "CU")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.CU.avg_vb[1])) & (stats_df['pitch_type'] == "CU")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.KC.avg_hb[1])) & (stats_df['pitch_type'] == "KC")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.KC.avg_vb[1])) & (stats_df['pitch_type'] == "KC")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.SV.avg_hb[1])) & (stats_df['pitch_type'] == "SV")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.SV.avg_vb[1])) & (stats_df['pitch_type'] == "SV")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.CH.avg_hb[1])) & (stats_df['pitch_type'] == "CH")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.CH.avg_vb[1])) & (stats_df['pitch_type'] == "CH")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.FS.avg_hb[1])) & (stats_df['pitch_type'] == "FS")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.FS.avg_vb[1])) & (stats_df['pitch_type'] == "FS")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.KN.avg_hb[1])) & (stats_df['pitch_type'] == "KN")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.KN.avg_vb[1])) & (stats_df['pitch_type'] == "KN")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.FO.avg_hb[1])) & (stats_df['pitch_type'] == "FO")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.FO.avg_vb[1])) & (stats_df['pitch_type'] == "FO")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.SC.avg_hb[1])) & (stats_df['pitch_type'] == "SC")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.SC.avg_vb[1])) & (stats_df['pitch_type'] == "SC")) |
        ((np.abs(stats_df['pfx_x']) > np.abs(pitch.EP.avg_hb[1])) & (stats_df['pitch_type'] == "EP")) |
        ((np.abs(stats_df['pfx_z']) > np.abs(pitch.EP.avg_vb[1])) & (stats_df['pitch_type'] == "EP")),

        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.FF.avg_hb[0])) & (stats_df['pitch_type'] == "FF")) |  # below avg
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.FF.avg_vb[0])) & (stats_df['pitch_type'] == "FF")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.SI.avg_hb[0])) & (stats_df['pitch_type'] == "SI")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.SI.avg_vb[0])) & (stats_df['pitch_type'] == "SI")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.FC.avg_hb[0])) & (stats_df['pitch_type'] == "FC")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.FC.avg_vb[0])) & (stats_df['pitch_type'] == "FC")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.SL.avg_hb[0])) & (stats_df['pitch_type'] == "SL")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.SL.avg_vb[0])) & (stats_df['pitch_type'] == "SL")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.ST.avg_hb[0])) & (stats_df['pitch_type'] == "ST")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.ST.avg_vb[0])) & (stats_df['pitch_type'] == "ST")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.CU.avg_hb[0])) & (stats_df['pitch_type'] == "CU")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.CU.avg_vb[0])) & (stats_df['pitch_type'] == "CU")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.KC.avg_hb[0])) & (stats_df['pitch_type'] == "KC")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.KC.avg_vb[0])) & (stats_df['pitch_type'] == "KC")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.SV.avg_hb[0])) & (stats_df['pitch_type'] == "SV")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.SV.avg_vb[0])) & (stats_df['pitch_type'] == "SV")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.CH.avg_hb[0])) & (stats_df['pitch_type'] == "CH")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.CH.avg_vb[0])) & (stats_df['pitch_type'] == "CH")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.FS.avg_hb[0])) & (stats_df['pitch_type'] == "FS")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.FS.avg_vb[0])) & (stats_df['pitch_type'] == "FS")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.KN.avg_hb[0])) & (stats_df['pitch_type'] == "KN")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.KN.avg_vb[0])) & (stats_df['pitch_type'] == "KN")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.FO.avg_hb[0])) & (stats_df['pitch_type'] == "FO")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.FO.avg_vb[0])) & (stats_df['pitch_type'] == "FO")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.SC.avg_hb[0])) & (stats_df['pitch_type'] == "SC")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.SC.avg_vb[0])) & (stats_df['pitch_type'] == "SC")) |
        ((np.abs(stats_df['pfx_x']) < np.abs(pitch.EP.avg_hb[0])) & (stats_df['pitch_type'] == "EP")) |
        ((np.abs(stats_df['pfx_z']) < np.abs(pitch.EP.avg_vb[0])) & (stats_df['pitch_type'] == "EP"))]

    choices = ['Above Avg.', 'Below Avg.']

    # print(f"conditions: {conditions}")

    stats_df['break_amount'] = np.select(conditions, choices, default='Average')

    return stats_df


"""
    This function will be passed into the to_sql function in order to be used as an insert function.
    This function will detect if there are duplicated keys, and where there are, it will update 
    with the new information (which will likely always be the same)
    
    :returns None
"""
def upsert(stats_df, conn, keys, data_iter):
    data = [dict(zip(keys, col)) for col in data_iter]
    insert_statement = insert(stats_df.table).values(data)
    upsert_statement = insert_statement.on_duplicate_key_update(**{c.name: c for c in insert_statement.inserted})

    conn.execute(upsert_statement)


"""
    This function is the heart of the ETL Pipeline. It runs the Extract using the statcast() function to get
    the stats from yesterday's games.
    It then runs the Transform using the cleanup_df() and calculate_cols() functions.
    Finally, it runs the Load portion of the pipeline by using the dataframe.to_sql() function,
    in tandem with the upsert() function in order to handle putting the data into the AWS DataBase 
    
    :exits code 0 if successful
"""
def main():
    load_dotenv()

    db_password = os.getenv("DB_PASSWORD")
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST")

    try:
        db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/mlb_pitching_stats"
        engine = sqla.create_engine(db_url)
        conn = engine.connect()
    except OperationalError as err:
        logging.error("Cannot connect to DB %s", err)
        print("There was an error connecting with the DB")
        raise err

    stats_df = statcast()  # get yesterday's stats

    if stats_df.empty:
        print("No games yesterday. Defaulting to 2025 world series")
        stats_df = statcast(start_dt="2025-10-24", end_dt="2025-11-01")  # default to last year's world series (2025)

    stats_df = cleanup_df(stats_df)
    stats_df = add_calc_cols(stats_df)

    stats_df.to_sql(name="mlb_pitching_stats", con=conn, if_exists='append', index=False, method=upsert)

    exit(0)


if __name__ == '__main__':
    main()
