
from Get_Survey_Responses import get_survey_responses
from Get_Survey_Questions import get_survey_questions

import traceback


server = "server" 
database = "database"
username = "username"
password = "password"
survey_id = "survey_id"
destination_table = "destination_table"  
api_token = "api_token"
data_center = "data_center"

def main():

    try:

        print("Processing survey responses ...")
        get_survey_responses(server, database, username, password, survey_id, destination_table, api_token, data_center)  

        print("Processing survey questions ...")
        get_survey_questions(server, database, username, password, survey_id, api_token, data_center)

    except Exception as e:
        error_message = traceback.format_exc() 

if __name__ == "__main__":

    main()
