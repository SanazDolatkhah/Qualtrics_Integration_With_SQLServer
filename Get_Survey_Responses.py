import requests
import zipfile
import io
import time
import pandas as pd
import pyodbc
import re

def get_db_connection(server, database, username, password):
    return pyodbc.connect(f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}")

def quote_ident(s):
    return f"[{str(s).replace(']', ']]')}]"

def quote_table_name(name: str) -> str:
    parts = [p for p in re.split(r"\.", str(name).strip()) if p]
    parts = [re.sub(r"[^A-Za-z0-9_\]\[]", "_", p) for p in parts]
    return ".".join(quote_ident(p) for p in parts)

def split_schema_table(name: str):
    parts = [p for p in re.split(r"\.", str(name).strip()) if p]
    if len(parts) == 1:
        return ("dbo", parts[0])
    return (parts[-2], parts[-1])

def recreate_table(conn, table_name: str, columns: list[str]):
    schema, table = split_schema_table(table_name)
    table_ident = f"{quote_ident(schema)}.{quote_ident(table)}"
    cur = conn.cursor()
    cur.execute(f"IF OBJECT_ID(N'{schema}.{table}', 'U') IS NOT NULL DROP TABLE {table_ident};")
    conn.commit()
    cur.execute(f"CREATE TABLE {table_ident} ({', '.join(f'{quote_ident(c)} NVARCHAR(MAX)' for c in columns)})")
    conn.commit()
    cur.close()
    return table_ident

def clean_response_rows(df: pd.DataFrame):
    if "ResponseID" in df.columns:
        df["ResponseID"] = df["ResponseID"].astype(str)
        bad_ids = {"{'ImportId': 'responseId'}", "ResponseID", ""}
        df = df[df["ResponseID"].notna()]
        df = df[~df["ResponseID"].isin(bad_ids)]
        df.drop_duplicates(subset=["ResponseID"], keep="first", inplace=True)
    def to_null(v):
        s = str(v)
        if s in ("nan", "None", "NaN"):
            return None
        return None if pd.isna(v) else v
    for col in df.columns:
        df[col] = df[col].apply(to_null)
    return df

def download_survey_csv(api_token: str, data_center: str, survey_id: str, use_labels: bool = True) -> pd.DataFrame:
    base_url = f"https://{data_center}.qualtrics.com/API/v3/responseexports/"
    headers = {"content-type": "application/json", "x-api-token": api_token}
    r = requests.post(base_url, json={"format":"csv","surveyId":survey_id,"useLabels":bool(use_labels)}, headers=headers)
    r.raise_for_status()
    job_id = r.json()["result"]["id"]
    while True:
        pr = requests.get(f"{base_url}{job_id}", headers=headers)
        pr.raise_for_status()
        if pr.json()["result"]["percentComplete"] >= 100:
            break
        time.sleep(1)
    dr = requests.get(f"{base_url}{job_id}/file", headers=headers, stream=True)
    dr.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(dr.content)) as zf:
        csv_name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def get_survey_responses(server, database, username, password, survey_id, destination_table, api_token, data_center):
    conn = get_db_connection(server, database, username, password)
    try:
        if not api_token or not data_center:
            raise RuntimeError("API credentials not found.")
        df = download_survey_csv(api_token, data_center, survey_id, use_labels=True)
        df = clean_response_rows(df)
        if df.empty:
            print("No valid rows after cleaning.")
            return
        table_ident = recreate_table(conn, destination_table, list(df.columns))
        print("Inserting rows into SQL...")
        cols = list(df.columns)
        sql = f"INSERT INTO {table_ident} ({', '.join(quote_ident(c) for c in cols)}) VALUES ({', '.join('?' for _ in cols)})"
        cur = conn.cursor()
        inserted = 0
        for row in df.itertuples(index=False, name=None):
            cur.execute(sql, tuple(row))
            inserted += 1
        conn.commit()
        cur.close()
        print(f"Finished. Inserted {inserted} rows into {destination_table}")
    finally:
        conn.close()
