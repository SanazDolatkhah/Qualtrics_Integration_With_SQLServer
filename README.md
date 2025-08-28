# Qualtrics to SQL Server Integration
## Introduction

As a **Data Analyst**, part of my work involves building Power BI dashboards using data coming from Qualtrics surveys. However, Power BI has no direct connector to Qualtrics. The only options provided by Qualtrics are manual exports (CSV, Excel, or SPSS).
This meant that every time I needed to build or update a dashboard, I had to:

- Export the survey results manually from Qualtrics.
- Convert SPSS exports into SQL Server or link Power BI directly to Excel.
- Refresh the dashboards manually, without having access to live and dynamic survey data.

This manual process was time-consuming, repetitive, and prevented me from delivering real-time insights.

## The Challenge

- Dashboards were always outdated, limited to the latest manual export.
- The workflow required multiple manual transformations.
- No automation was in place, so scaling dashboards across multiple surveys was inefficient.

## The Solution

After researching possible integrations, I discovered that Qualtrics provides REST APIs to fetch survey data, questions, translations, and even display logic. Using Python and libraries like requests, pandas, and database connectors (pyodbc / sqlalchemy), I developed an integration that:
Connects to the Qualtrics API.

- Extracts survey responses and questions.
- Handles Matrix questions by fetching sub-questions.
- Extracts answer choices (multi-language support: English & French).
- Retrieves survey display logic.
- Inserts the structured data directly into SQL Server.
  
Now, Power BI can be connected directly to SQL Server, resulting in dynamic, always up-to-date dashboards without any manual intervention.

## Tech Stack

- Python: ETL scripts and API integration
- Libraries:
  - requests (Qualtrics API calls)
  - pandas (data transformation)
  - pyodbc / sqlalchemy (SQL Server integration)
    
- Database: Microsoft SQL Server
- Visualization: Power BI

## Architecture & Data Flow

<pre> Qualtrics API → Python ETL → SQL Server → Power BI </pre>

## Features

- Fetch survey responses in real time.
- Extract survey questions, including matrix sub-questions.
- Support for multi-language surveys (English & French translations).
- Retrieve survey display logic for more accurate reporting.
- Load data into SQL Server for direct Power BI integration.
- Modular structure for easy customization and extension.

## Benefits

- Near real-time dashboards in Power BI without manual exports.
- Reusable template for all future Qualtrics-based dashboards.
- Scalable solution that can handle multiple surveys and languages.
- Eliminates repetitive manual work.

## Example (Simplified Version)

For confidentiality reasons, the version here on GitHub is a simplified demo that focuses on:

- Fetching survey responses
- Fetching survey questions

This allows you to understand the integration logic without exposing sensitive company data.

## Getting Started


### Prerequisites
- Python 3.9+
- Qualtrics API Token
- SQL Server instance

## Setup
<pre>
git clone https://github.com/your-repo/qualtrics-sql-integration.git
cd qualtrics-sql-integration
pip install -r requirements.txt
</pre>

## Run
<pre>
python main.py
</pre>

## Future Improvements
- Unpivot survey responses into a FactSurvey table for better reporting.
- Automated refresh pipelines.
- Power BI template dashboards.

## Contact
If you need more details about the advanced features (translations, matrix handling, display logic, etc.), feel free to reach out.

- Email: sanaz.dolatkhah@Sgmail.com
- LinkedIn: *https://www.linkedin.com/in/sanaz-dolatkhah*

## License
MIT License

