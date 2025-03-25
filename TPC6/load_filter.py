"""
Code for filtering IMDB non-commercial datasets.

Datasets From:
https://developer.imdb.com/non-commercial-datasets/
"""

import pandas as pd
from datetime import datetime
import os
import tempfile

def filter_and_write(input_file, sep, usecols, dtype, na_values, chunksize,
                     filter_func, dedup_cols, key_col):

    key_set = set()
    # Create a temporary file which will persist until manually removed
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_filename = temp.name
    temp.close()  # We'll open it via pandas.to_csv

    for chunk in pd.read_csv(input_file, sep=sep, usecols=usecols, dtype=dtype,
                             na_values=na_values, chunksize=chunksize, encoding="utf-8"):
        # Apply filtering logic specific to the file
        filtered = filter_func(chunk)
        # Remove duplicates and rows with missing data
        filtered = filtered.drop_duplicates(subset=dedup_cols, keep='first').dropna()
        # Update the key set from the specified column
        key_set.update(filtered[key_col].unique())
        # Append to temporary CSV file, writing header only once
        filtered.to_csv(temp_filename, mode='a', index=False,
                        header=not os.path.exists(temp_filename) or os.path.getsize(temp_filename)==0)
    return key_set, temp_filename

def load_filter_TSVs(file_tBasics, file_tAkas, file_tPrincipals, file_nBasics, chunksize=100000):
    temp_files = []

    # Phase 1: Process title.basics.tsv for movies
    movies_filter = lambda df: df[df["titleType"] == "movie"]
    movies_dedup = ["tconst", "primaryTitle", "originalTitle"]
    movies_dtype = {"tconst": "str", "titleType": "str", "primaryTitle": "str", 
                    "originalTitle": "str", "startYear": "str", "runtimeMinutes": "str", "genres": "str"}
    movies_set, tmp_movies = filter_and_write(
        input_file=file_tBasics,
        sep="\t",
        usecols=["tconst", "titleType", "primaryTitle", "originalTitle", "startYear", "runtimeMinutes", "genres"],
        dtype=movies_dtype,
        na_values="\\N",
        chunksize=chunksize,
        filter_func=movies_filter,
        dedup_cols=movies_dedup,
        key_col="tconst"
    )
    temp_files.append(tmp_movies)
    print("Movies first filter done.")

    # Phase 1: Process title.akas.tsv using movies_set
    akas_filter = lambda df: df[df["titleId"].isin(movies_set)]
    akas_dedup = ["titleId", "language", "region"]
    akas_dtype = {"titleId": "str", "language": "str", "region": "str"}
    akas_set, tmp_akas = filter_and_write(
        input_file=file_tAkas,
        sep="\t",
        usecols=["titleId", "language", "region"],
        dtype=akas_dtype,
        na_values="\\N",
        chunksize=chunksize,
        filter_func=akas_filter,
        dedup_cols=akas_dedup,
        key_col="titleId"
    )
    temp_files.append(tmp_akas)
    print("Akas first filter done.")

    # Phase 1: Process title.principals.tsv using akas_set
    principals_filter = lambda df: df[df["tconst"].isin(akas_set)]
    principals_dedup = ["tconst", "nconst", "characters"]
    principals_dtype = {"tconst": "str", "nconst": "str", "characters": "str"}
    principals_set, tmp_principals = filter_and_write(
        input_file=file_tPrincipals,
        sep="\t",
        usecols=["tconst", "nconst", "characters"],
        dtype=principals_dtype,
        na_values="\\N",
        chunksize=chunksize,
        filter_func=principals_filter,
        dedup_cols=principals_dedup,
        key_col="nconst"
    )
    temp_files.append(tmp_principals)
    print("Principals first filter done.")

    # Phase 1: Process name.basics.tsv using principals_set
    actors_filter = lambda df: df[df["nconst"].isin(principals_set)]
    actors_dedup = ["nconst", "primaryName"]
    actors_dtype = {"nconst": "str", "primaryName": "str"}
    actors_set, tmp_actors = filter_and_write(
        input_file=file_nBasics,
        sep="\t",
        usecols=["nconst", "primaryName"],
        dtype=actors_dtype,
        na_values="\\N",
        chunksize=chunksize,
        filter_func=actors_filter,
        dedup_cols=actors_dedup,
        key_col="nconst"
    )
    temp_files.append(tmp_actors)
    print("Actors first filter done.")
    print("First phase of reading and filtering is completed.")

    # Phase 2: Load temporary files into dataframes for further filtering and merging
    print("Starting second phase of filtering...")
    print("Loading temporary files...")
    movies_df = pd.read_csv(tmp_movies, dtype=movies_dtype)
    akas_df = pd.read_csv(tmp_akas, dtype=akas_dtype)
    principals_df = pd.read_csv(tmp_principals, dtype=principals_dtype)
    actors_df = pd.read_csv(tmp_actors, dtype=actors_dtype)
    print("Temporary files loaded successfully.")

    print("Applying second phase filters...")
    # Ensure consistency between movies and akas
    movies_df = movies_df[movies_df["tconst"].isin(akas_df["titleId"])]
    akas_df = akas_df[akas_df["titleId"].isin(movies_df["tconst"])]

    # Merge akas into movies (rename for merge consistency)
    akas_df = akas_df.rename(columns={"titleId": "tconst"})
    movies_df = pd.merge(movies_df, akas_df, on="tconst", how="inner")
    movies_df.dropna(inplace=True)

    # Filter principals and actors based on movies
    principals_df = principals_df[principals_df["tconst"].isin(movies_df["tconst"])]
    principals_df = principals_df[principals_df["nconst"].isin(actors_df["nconst"])]
    movies_df = movies_df[movies_df["tconst"].isin(principals_df["tconst"])]
    actors_df = actors_df[actors_df["nconst"].isin(principals_df["nconst"])]
    print("Second filtering completed.")

    # Save final results
    print("Saving results...")
    movies_df.to_csv("movies.csv", index=False)
    actors_df.to_csv("actors.csv", index=False)
    principals_df.to_csv("principals.csv", index=False)
    print("Results saved to movies.csv, actors.csv, and principals.csv.")

    # Clean up temporary files
    for tmp_file in temp_files:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
    print("Temporary files removed.")

if __name__ == "__main__":
    load_filter_TSVs("title.basics.tsv", "title.akas.tsv", "title.principals.tsv", "name.basics.tsv")
