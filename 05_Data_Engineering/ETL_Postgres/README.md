# Sparkify - Analyze Song Data

## Description 

### Aim

Sparkify wants to analyze data concerning user activity on their music streaming app.

Focus should be placed on understanding what songs users are listening to. 

### Data 

(Taken from Project Description)

The data concerns songs and website logs - both saved in JSON format.

* Songs: Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset. Data are partitioned by the first three letters of each song's track ID.

* Logs: activity logs from a music streaming app based on specified configurations, partitioned by year/month.

### Files

1. `create_tables.py`: DB initialization (schema instantiation, table rop and creation);
2. `etl.ipynb`: develpment notebook for the ETL pipeline;
3. `etl.py`: ETL pipeline script;
4. `sql_queries.py`: collection of SQL queries used in the files mentioned above;
5. `test-etl-py.ipynb`: this notebook runs `etl.py` and assesses the results;
6. `test.ipynb`: test notebook for file no. 2. 

## Steps

### Step 1

In order to takle this issue, we have created a Postgres database schema and defined the related dimension and fact tables - ref.: `initDB` function in `etl.py` and paragraphs `#DROP TABLES` and `#CREATE TABLES` in `sql_queries.py`.

### Step 2

Then, we have defined an ETL process (`etl.ipynb`, for deveopment purpose) and an ETL pipeline (`etl.py`), in order to upload logs and song data to our DB.

Note: the ETL pipeline has been adapted in order to process all files within the `data` directory - ref.: lines 131, 38, 9, 104.

### Step 3

Finally, we queried the data and provided results for song play analysis - please see **Check:** and **Validation:** in `test-etl-py.ipynb`.

## How to run the Python scripts

Restart the kernel and execute all cells of `test-etl-py.ipynb`.
Alternatively, run `etl.py` from terminal and then run all cells but the first one in `test-etl-py.ipynb`.