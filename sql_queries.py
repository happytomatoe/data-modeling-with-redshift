import configparser


class TableNames:
    TIME = "time"
    ARTISTS = "artists"
    SONGS = "songs"
    USERS = "users"
    SONGPLAYS = "songplays"
    staging_events = "staging_events"
    staging_songs = "staging_songs"
    ALL_TABLES = [TIME, ARTISTS, SONGPLAYS, SONGS, USERS, staging_events, staging_songs]


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES


# CREATE TABLES

staging_events_table_create = (f"""
CREATE TABLE {TableNames.staging_events}(
    -- filtering 
    page varchar,
    -- time data
    ts bigint,
    -- user data
    userAgent varchar,
    userId varchar distkey,
    firstName varchar,
    lastName varchar,
    gender char,
    level varchar,
    -- songplay data
    artist varchar,  
    song varchar,
    length varchar
)
""")
#     log_df = log_df[log_df.page == "NextSong"]
#
#     # remove quotes in User Agent field
#     log_df['userAgent'] = log_df['userAgent'].str.replace('"', '')
#
#     # convert timestamp column to datetime
#     log_df['start_time'] = pd.to_datetime(log_df["ts"], unit='ms')
#
#     time_data_df = log_df[['start_time']].copy()
#     datetime = time_data_df.start_time.dt
#     time_data_df['hour'] = datetime.hour
#     time_data_df['day'] = datetime.day
#     time_data_df['week_of_year'] = datetime.week
#     time_data_df['month'] = datetime.month
#     time_data_df['year'] = datetime.year
#     time_data_df['weekday'] = datetime.weekday
#     time_data_df = time_data_df.drop_duplicates(subset=['start_time'])
#     load_into_db(cur, time_data_df, TableNames.TIME)
#
#     user_df = log_df[["userId", "firstName", "lastName", "gender", "level"]].copy()
#     user_df = user_df.drop_duplicates(subset=['userId'])
#     load_into_db(cur, user_df, TableNames.USERS, "user_id", ["level"])
#
#     common_columns = ['song', 'artist', 'length']
#     tuples = [tuple(x) for x in log_df[common_columns].values]
#     df2 = select_song_and_artist_ids(cur, tuples)
#     if not df2.empty:
#         log_df = log_df.merge(df2, how='left', on=common_columns)
#     else:
#         log_df["artist_id"] = np.nan
#         log_df["song_id"] = np.nan
#     log_df['id'] = [str(uuid4()) for _ in range(len(log_df.index))]
#     songplay_data = log_df[
#         ['id', 'start_time', 'userId', 'level', 'song_id', 'artist_id',
#          'sessionId', 'location', 'userAgent']]
#     load_into_db(cur, songplay_data, TableNames.SONGPLAYS)

staging_songs_table_create = (f"""
CREATE TABLE {TableNames.staging_songs}(
--     id bigint not null,
    artist_id varchar,
    artist_name varchar,
    artist_latitude real,
    artist_longitude real,
    artist_location varchar,
    duration real,
    song_id varchar,
    title varchar,
    year smallint
)
""")
# # open song file
# df = pd.read_json(path_or_buf=filepath, lines=True)

#
# # insert artist records
# artist_df = df[["artist_id", "artist_name", "artist_location", "artist_latitude",
#                 "artist_longitude"]]
# load_into_db(cur, artist_df, TableNames.ARTISTS)
#
# # insert song records
# song_df = df[['song_id', "title", "artist_id", "year", "duration"]]
# load_into_db(cur, song_df, TableNames.SONGS)


# TODO:
# add constraint songplays__time_fk references time
songplays_table_create = (f"""
CREATE TABLE {TableNames.SONGPLAYS}(
    id varchar not null constraint songplays_pk primary key distkey,
    start_time timestamp not null,
    user_id bigint constraint songplays__user_fk references users,
    level varchar,
    song_id varchar constraint songplays__songs_fk references songs,
    artist_id varchar constraint songplays__artist_fk references artists,
    session_id bigint,
    location varchar,
    user_agent varchar
    );
""")

user_table_create = (f"""
CREATE TABLE {TableNames.USERS} (
    user_id bigint not null constraint users_pk primary key distkey,
    first_name varchar,
    last_name varchar,
    gender varchar(1),
    level varchar
    )
""")

# CHECK (duration >0)
song_table_create = (f"""
CREATE TABLE {TableNames.SONGS} (
    song_id varchar not null constraint songs_pk primary key distkey,
    title varchar not null unique,
    artist_id varchar constraint songs__artist_fk references artists,
    year integer,
    duration numeric not null 
    )

""")

# TODO:
#  CHECK (latitude >= -90 AND latitude <= 90)
# CHECK (latitude >= -180 AND latitude <= 180)
artist_table_create = (f"""
CREATE TABLE {TableNames.ARTISTS}(
    artist_id varchar not null constraint artists_pk primary key distkey,
    name varchar not null unique,
    location varchar,
    latitude numeric,
    longitude numeric 
    )
""")

time_table_create = (f"""
CREATE TABLE {TableNames.TIME}(
    start_time timestamp not null constraint time_pk primary key distkey,
    hour integer not null,
    day integer not null,
    week integer not null,
    month integer not null,
    year integer not null,
    weekday integer not null 
)
""")

# STAGING TABLES

staging_events_copy = (f"""
copy {TableNames.staging_events} 
from {{}} 
iam_role {{}}
COMPUPDATE OFF STATUPDATE OFF
format as json 'auto';
;
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'])

staging_songs_copy = (f"""
copy {TableNames.staging_songs} 
from {{}}
iam_role {{}}
-- from https://stackoverflow.com/questions/57196733/best-methods-for-staging-tables-you-updated-in-redshift
COMPUPDATE OFF STATUPDATE OFF
format as json 'auto';
;
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'])

# FINAL TABLES


#     log_df = log_df[log_df.page == "NextSong"]
#
#     # remove quotes in User Agent field
#     log_df['userAgent'] = log_df['userAgent'].str.replace('"', '')
#
#     # convert timestamp column to datetime
#     log_df['start_time'] = pd.to_datetime(log_df["ts"], unit='ms')
#
#
#     common_columns = ['song', 'artist', 'length']
#     tuples = [tuple(x) for x in log_df[common_columns].values]
#     df2 = select_song_and_artist_ids(cur, tuples)
#     if not df2.empty:
#         log_df = log_df.merge(df2, how='left', on=common_columns)
#     else:
#         log_df["artist_id"] = np.nan
#         log_df["song_id"] = np.nan
#     log_df['id'] = [str(uuid4()) for _ in range(len(log_df.index))]
#     songplay_data = log_df[
#         ['id', 'start_time', 'userId', 'level', 'song_id', 'artist_id',
#          'sessionId', 'location', 'userAgent']]
#     load_into_db(cur, songplay_data, TableNames.SONGPLAYS)
songplay_table_insert = (f"""

""")
#     log_df = log_df[log_df.page == "NextSong"]
#
#     # remove quotes in User Agent field
#     log_df['userAgent'] = log_df['userAgent'].str.replace('"', '')
#
#
#     user_df = log_df[["userId", "firstName", "lastName", "gender", "level"]].copy()
#     user_df = user_df.drop_duplicates(subset=['userId'])
#     load_into_db(cur, user_df, TableNames.USERS, "user_id", ["level"])
user_table_insert = (f"""
""")

#     df = df.replace({'year': {0: np.nan}})
# song_df = df[['song_id', "title", "artist_id", "year", "duration"]]
song_table_insert = (f"""
  -- INSERT NEW ROWS ONLY
    INSERT INTO {TableNames.SONGS}(song_id, title,artist_id,year,duration)  
    SELECT  st.song_id, st.title, st.artist_id, st.year, st.duration  FROM
     {TableNames.staging_songs} st
    LEFT OUTER JOIN {TableNames.SONGS} b USING(song_id)
    WHERE b.song_id is null;
""")

# artist table
# "artist_id", "artist_name", "artist_location", "artist_latitude",
#                     "artist_longitude"
artist_table_insert = (f"""
    -- INSERT NEW ROWS ONLY
    INSERT INTO {TableNames.ARTISTS}(artist_id,name,location,latitude,longitude)  
    SELECT  artist_id, artist_name, artist_location, artist_latitude,
                     artist_longitude FROM {TableNames.staging_songs}
    LEFT OUTER JOIN {TableNames.ARTISTS} b USING(artist_id)
    WHERE b.artist_id is null;
""")

#     log_df = log_df[log_df.page == "NextSong"]
#
#     # convert timestamp column to datetime
#     log_df['start_time'] = pd.to_datetime(log_df["ts"], unit='ms')
#
#     time_data_df = log_df[['start_time']].copy()
#     datetime = time_data_df.start_time.dt
#     time_data_df['hour'] = datetime.hour
#     time_data_df['day'] = datetime.day
#     time_data_df['week_of_year'] = datetime.week
#     time_data_df['month'] = datetime.month
#     time_data_df['year'] = datetime.year
#     time_data_df['weekday'] = datetime.weekday
#     time_data_df = time_data_df.drop_duplicates(subset=['start_time'])
#     load_into_db(cur, time_data_df, TableNames.TIME)

# Idea on how convert to timestamp from https://stackoverflow.com/questions/39815425/how-to-convert-epoch-to-datetime-redshift
time_table_insert = (f"""
    INSERT INTO {TableNames.TIME}(start_time,hour,day,week,month,year,weekday)  
    SELECT st.* FROM (SELECT timestamp 'epoch' + ts/1000 * interval '1 second' AS start_time, 
    extract(hour from start_time) as hour,
    extract(day from start_time) as day,
    extract(week from start_time) as week,
    extract(month from start_time) as month,
    extract(year from start_time) as year,
    extract(weekday from start_time) as weekday
    FROM {TableNames.staging_events}) st  
    LEFT OUTER JOIN {TableNames.TIME} b USING(start_time)
    WHERE b.start_time is null;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create,
                        user_table_create, artist_table_create, song_table_create,
                        time_table_create, songplays_table_create]

DROP_TABLE_QUERY_TEMPLATE = "DROP TABLE IF EXISTS {} CASCADE;"

drop_table_queries = [DROP_TABLE_QUERY_TEMPLATE.format(x) for x in TableNames.ALL_TABLES]

copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [artist_table_insert, song_table_insert, time_table_insert]
# ,
# user_table_insert , , songplay_table_insert]
