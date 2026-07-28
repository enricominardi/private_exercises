#import configparser


# CONFIG
#config = configparser.ConfigParser()
#config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS stage_events CASCADE;"
staging_songs_table_drop = "DROP TABLE IF EXISTS stage_songs CASCADE;"
songplay_table_drop = "DROP TABLE IF EXISTS songplays CASCADE;"
user_table_drop = "DROP TABLE IF EXISTS users CASCADE;"
song_table_drop = "DROP TABLE IF EXISTS songs CASCADE;"
artist_table_drop = "DROP TABLE IF EXISTS artists CASCADE;"
time_table_drop = "DROP TABLE IF EXISTS time CASCADE;"

# CREATE SCHEMA
schema_create = """
CREATE SCHEMA IF NOT EXISTS {}; \
""".format(config['DWH_CONN']['NAME'])
# SET PATH
schema_set_path = """
SET search_path TO {}; \
""".format(config['DWH_CONN']['NAME'])

# CREATE TABLES
staging_events_table_create= """
# CREATE TABLE stage_events ( \
    artist
    auth
    firstName
    gender
    itemInSession
    lastName
    length
    level
    location
    method
    page
    registration
    sessionId
    song
    status
    ts
    userAgent
    userId
)
""")

# {"num_songs": 1,
# "artist_id": "ARJIE2Y1187B994AB7",
# "artist_latitude": null,
# "artist_longitude": null,
# "artist_location": "",
# "artist_name": # "Line Renaud",
# "song_id": "SOUPIRU12A6D4FA1E1",
# "title": "Der Kleine Dompfaff",
# "duration": 152.92036,
# "year": 0}


staging_songs_table_create = (
"""
CREATE TABLE stage_songs ( \
    artist_id
    artist_latitude
    artist_longitude
    artist_location
    artist_name
    song_id
    title
    duration
    year
"""
)

songplay_table_create = """
CREATE TABLE IF NOT EXISTS songplays ( \
    songplay_id SERIAL, \
    start_time timestamp NOT NULL, \
    user_id numeric NOT NULL, \
    level varchar, \
    song_id varchar, \
    artist_id varchar, \
    session_id varchar, \
    location varchar, \
    user_agent varchar, \
    PRIMARY KEY(start_time, user_id) \
    ); \
"""

user_table_create = """
CREATE TABLE IF NOT EXISTS users ( \
    user_id numeric PRIMARY KEY, \
    first_name varchar NOT NULL, \
    last_name varchar NOT NULL, \
    gender varchar, \
    level varchar \
    ); \
"""

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs ( \
    song_id varchar PRIMARY KEY, \
    title varchar NOT NULL, \
    artist_id varchar, \
    year int, \
    duration numeric \
    ); \
""")

artist_table_create = """
CREATE TABLE IF NOT EXISTS artists ( \
    artist_id varchar PRIMARY KEY, \
    name varchar NOT NULL, \
    location varchar, \
    latitude numeric, \
    longitude numeric \
    ); \
"""

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time ( \
    start_time timestamp PRIMARY KEY, \
    hour numeric NOT NULL, \
    day numeric NOT NULL, \
    week numeric NOT NULL, \
    month numeric NOT NULL, \
    year numeric NOT NULL, \
    weekday numeric NOT NULL \
    ); \
""")

# STAGING TABLES

staging_events_copy = ("""
COPY stage_events from '{}'' \
    credentials 'aws_iam_role={}' \
    gzip delimiter ';' \
    compupdate off region '{}';
""").format(
            config['S3']['LOG_DATA'],
            config['IAM_ROLE']['ROLE_ARN'],
            config['AWS']['REGION']
            )

staging_songs_copy = ("""
COPY stage_songs from '{}' \
    credentials 'aws_iam_role={}' \
    gzip delimiter ';' \
    compupdate off region '{}'; \
""").format(
            config['S3']['SONG_DATA'],
            config['IAM_ROLE']['ROLE_ARN'],
            config['AWS']['REGION']
            )

# FINAL TABLES

songplay_table_insert = """
INSERT INTO songplays ( \
    start_time, \
    user_id, \
    level, \
    song_id, \
    artist_id, \
    session_id, \
    location, \
    user_agent \
    ) \
VALUES ( \
    %s, %s, %s, \
    %s, %s, %s, \
    %s, %s \
    ) \
ON CONFLICT (start_time, user_id) DO UPDATE \
SET level  = EXCLUDED.level; \
"""

user_table_insert = """
INSERT INTO users ( \
    user_id, \
    first_name, \
    last_name, \
    gender, \
    level \
    ) \
VALUES ( \
    %s, %s, %s, \
    %s, %s \
    ) \
ON CONFLICT (user_id) DO UPDATE \
SET level  = EXCLUDED.level; \
"""

song_table_insert = """
INSERT INTO songs ( \
    song_id, \
    title, \
    artist_id, \
    year, \
    duration \
    ) \
VALUES ( \
    %s, %s, %s, \
    %s, %s \
    ) \
ON CONFLICT DO NOTHING; \
"""

artist_table_insert = ("""
INSERT INTO artists ( \
    artist_id, \
    name, \
    location, \
    latitude, \
    longitude \
    ) \
VALUES ( \
    %s, %s, %s, \
    %s, %s \
    ) \
ON CONFLICT DO NOTHING; \
""")

time_table_insert = """
INSERT INTO time ( \
    start_time, \
    hour, \
    day, \
    week, \
    month, \
    year, \
    weekday \
    ) \
VALUES ( \
    %s, %s, %s, \
    %s, %s, %s, \
    %s \
    ) \
ON CONFLICT DO NOTHING; \
"""

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create,
songplay_table_create, user_table_create, song_table_create,
artist_table_create, time_table_create]
drop_table_queries =
[staging_events_table_drop, staging_songs_table_drop, songplay_table_drop,
user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert,
song_table_insert, artist_table_insert, time_table_insert]
