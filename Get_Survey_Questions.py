import requests
import pyodbc
import re

def get_db_connection(server, database, username, password):
    conn_str = (
        "DRIVER={SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    return pyodbc.connect(conn_str)

_HTML_TAG_RE = re.compile(r"<.*?>")
def remove_html_tags(text):
    return re.sub(_HTML_TAG_RE, "", text or "")


def get_survey_questions(server, database, username, password, survey_id, api_token, data_center):
    
    base_url = f"https://{data_center}.qualtrics.com/API/v3/survey-definitions/{survey_id}/questions"
    headers = {"X-API-TOKEN": api_token, "Content-Type": "application/json"}
    conn = get_db_connection(server, database, username, password)
    try:
        with conn.cursor() as cur:
            exists_sql = f"SELECT COUNT(1) FROM DimQuestion WHERE SurveyId = ?"
            cur.execute(exists_sql, survey_id)
            if (cur.fetchone() or [0])[0] > 0:
                print(f"SurveyId {survey_id} already exists in DimQuestion. No new records inserted.")
                return

            resp = requests.get(base_url, headers=headers, timeout=60)
            resp.raise_for_status()
            payload = resp.json()
            elements = payload.get("result", {}).get("elements", [])
            if not elements:
                print("No questions found in Qualtrics response.")
                return

            to_insert = []
            for q in elements:
                q_text_raw = q.get("QuestionText", "") or ""
                q_type = q.get("QuestionType", "") or ""
                q_export = q.get("DataExportTag", "") or ""
                q_id = q.get("QuestionID", "") or ""
                if not q_export.lower().startswith("q"):
                    continue
                if q_type == "DB":
                    continue
                clean_text = remove_html_tags(q_text_raw)
                final_text = clean_text.strip().splitlines()[-1].strip() if clean_text.strip() else ""
                final_text = (
                    final_text.replace("&nbsp;", "")
                              .replace("a&rsquo;", "'")
                              .replace("&rsquo;", "'")
                              .replace("&quot;", '"')
                              .replace("&amp;", "&")
                )
                to_insert.append(
                    (survey_id, q_export, q_id, final_text, q_type)
                )

            if not to_insert:
                print("No eligible Q*/q* questions to insert.")
                return

            insert_sql = f"""
                INSERT INTO DimQuestion (SurveyId, QuestionNumber, QuestionId, Question, QuestionType)
                VALUES (?, ?, ?, ?, ?)
            """
            cur.executemany(insert_sql, to_insert)
            conn.commit()
            print(f"Inserted {len(to_insert)} records into DimQuestion.")
    except requests.exceptions.RequestException as e:
        print(f"HTTP/Network error: {e}")
    except pyodbc.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


