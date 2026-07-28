import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *
from create_tables import create_database, drop_tables, create_tables 


def process_song_file(cur, filepath):
    """
    Row-wise insertion of song-file data into songs and artists tables.
        
    Parameters:
        cur: psycopg2 connect.cursor instance
        filepath: file path, string
        
    """
    
    # open song file
    df = pd.read_json(filepath, lines=True)
    
    for i, row in df.iterrows():
        
        # insert song records
        song_data = [
            row.song_id,
            row.title,
            row.artist_id,
            row.year,
            row.duration
            ]
        
        cur.execute(song_table_insert, song_data)
        
        # insert artist records
        artist_data = [
            row.artist_id, 
            row.artist_name, 
            row.artist_location, 
            row.artist_latitude, 
            row.artist_longitude
            ]

        cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    Insertion of log-file data into time, users and songplays tables.
    Dataset for time and songplays is filtered by page like 'NextSong'.
    
    Parameters:
        cur: psycopg2 connect.cursor instance
        filepath: file path, string
        
    """
    
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    ns_df =  df.query('page == "NextSong"').copy()

    # convert timestamp column to datetime
    ns_df['ts'] = pd.to_datetime(ns_df['ts'], unit='ms')
    
    # insert time data records
    time_data = [
        ns_df['ts'],
        ns_df['ts'].dt.hour,
        ns_df['ts'].dt.day,
        ns_df['ts'].dt.week,
        ns_df['ts'].dt.month,
        ns_df['ts'].dt.year,
        ns_df['ts'].dt.weekday
        ]
    
    column_labels = [
        'timestamp', 
        'hour', 
        'day', 
        'week of year', 
        'month', 
        'year', 
        'weekday'
        ]
    
    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[[
        'userId', 
        'firstName', 
        'lastName', 
        'gender', 
        'level'
        ]].copy()
    user_df.drop_duplicates(inplace=True)
    user_df.dropna(inplace=True)
    user_df.reset_index(inplace=True, drop=True)

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in ns_df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
                    row.ts, #start_time
                    row.userId, #user_id
                    row.level, #level
                    songid, #song_id
                    artistid, #artist_id
                    str(row.sessionId), #session_id
                    row.location, #location
                    row.userAgent #user_agent
                    )

        cur.execute(songplay_table_insert, songplay_data)

def process_data(cur, conn, filepath, func):
    """
    Applies func to all .json files in filepath dir. three and 
    commits SQL queries to the DB.
    
    Parameters:
        cur: psycopg2 connect.cursor instance
        conn: psycopg2 connect instance
        filepath: file path, string
        func: python function with cur.execute instace and dataframe 
    """

    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))
        
def initDB():
    """
    Database schema initialization with drop and table creation.
    
    Returns:
        cur: psycopg2 connect.cursor instance
        conn: psycopg2 connect instance
    """
    
    cur, conn = create_database()
    drop_tables(cur, conn)
    create_tables(cur, conn)
    return cur, conn

def main():
    """
    Logic execution-flow functions call and DB connection handling.
    """
    
    cur, conn= initDB()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)
    
    conn.close()


if __name__ == "__main__":
    main()