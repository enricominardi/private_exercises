# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays CASCADE"
user_table_drop = "DROP TABLE IF EXISTS users CASCADE"
song_table_drop = "DROP TABLE IF EXISTS songs CASCADE"
artist_table_drop = "DROP TABLE IF EXISTS artists CASCADE"
time_table_drop = "DROP TABLE IF EXISTS time CASCADE"

# CREATE TABLES


#Fact Table

#     songplays - records in log data associated with song plays i.e. records with page NextSong
#         songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

# Dimension Tables

#     users - users in the app
#         user_id, first_name, last_name, gender, level
#     songs - songs in music database
#         song_id, title, artist_id, year, duration
#     artists - artists in music database
#         artist_id, name, location, latitude, longitude
#     time - timestamps of records in songplays broken down into specific units
#         start_time, hour, day, week, month, year, weekday

songplay_table_create = """CREATE TABLE IF NOT EXISTS songplays ( \
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

user_table_create = """CREATE TABLE IF NOT EXISTS users ( \
                                user_id numeric PRIMARY KEY, \
                                first_name varchar NOT NULL, \
                                last_name varchar NOT NULL, \
                                gender varchar, \
                                level varchar \
                                ); \
"""

song_table_create = """CREATE TABLE IF NOT EXISTS songs ( \
                                song_id varchar PRIMARY KEY, \
                                title varchar NOT NULL, \
                                artist_id varchar, \
                                year int, \
                                duration numeric \
                                ); \
"""


artist_table_create = """CREATE TABLE IF NOT EXISTS artists ( \
                                artist_id varchar PRIMARY KEY, \
                                name varchar NOT NULL, \
                                location varchar, \
                                latitude numeric, \
                                longitude numeric \
                                ); \
"""


time_table_create = """CREATE TABLE IF NOT EXISTS time ( \
                                start_time timestamp PRIMARY KEY, \
                                hour numeric NOT NULL, \
                                day numeric NOT NULL, \
                                week numeric NOT NULL, \
                                month numeric NOT NULL, \
                                year numeric NOT NULL, \
                                weekday numeric NOT NULL \
                                ); \
"""


# INSERT RECORDS

songplay_table_insert = """INSERT INTO songplays ( \
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

user_table_insert = """INSERT INTO users ( \
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

song_table_insert = """INSERT INTO songs ( \
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

artist_table_insert = """INSERT INTO artists ( \
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
"""

time_table_insert = """INSERT INTO time ( \
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

#Ref.s: 
# 1 - https://www.postgresqltutorial.com/postgresql-upsert/
# 2 - https://stackoverflow.com/questions/35888012/use-multiple-conflict-target-in-on-conflict-clause

# FIND SONGS
# find the song ID and artist ID based on the title, artist name, and duration of a song

song_select = """SELECT \
                        s.song_id, \
                        a.artist_id \
                    FROM \
                        songs s,\
                        artists a \
                    WHERE \
                        a.artist_id = s.artist_id \
                    AND s.title = %s \
                    AND a.name = %s \
                    AND s.duration = %s; \
"""

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]