# Reporter - Automated Reporting System

## Description

**Reporter** is a tool designed for **Mundo Vending and Exolgan** that automates the generation and distribution of vending machines vends reports. The application extracts data from an SQL Server database, creates Excel reports, and distributes them via email to configured recipients.

## Project Status

⚠️ **NOTE:** This project is currently under active development.

## Features

* **Data Extraction**: Connects to SQL Server databases to retrieve specific information.
* **Report Generation**: Produces professionally formatted Excel reports.
* **Automated Distribution**: Sends reports automatically via email using ZeptoMail's robust and secure service (with IP-restricted API keys).
* **Flexible Configuration**: Easily customizable via JSON configuration files.

## Project Structure

```
reporter/
├── README.md             # Project documentation
├── requirements.txt      # Project dependencies
└── src/                  # Source code
    ├── reporter.conf     # Configuration file
    ├── reporter.py       # Main execution script
    └── modules/          # Functional modules
        ├── config.py     # Configuration management
        ├── excel.py      # Excel report generation
        ├── mail.py       # Email dispatch functionality
        └── database/     # Database interaction module
            ├── queries.py        # Predefined SQL queries
            └── sql_connection.py # Database connection handler
```

## Installation

1. Clone the repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Configure the connection details in `src/reporter.conf`.

## Usage

**Reporter** is designed to run from the command line using Python. The intended usage patterns are:

* Generate a report for the **previous month**:

```bash
python reporter.py -last_month
```

* Generate a report for a **specific date range**:

```bash
python reporter.py -between YYYY-MM-DD -and YYYY-MM-DD
```

Replace `YYYY-MM-DD` with your desired start and end dates.

### Recommended Setup for Automated Execution

For automated monthly reporting, it is recommended to configure a scheduled task on Windows (Task Scheduler) to execute the following command once at the beginning of each month:

```cmd
python reporter.py -last_month
```

Ensure the task is configured to execute in the correct directory, and that all dependencies are properly installed and accessible.

## Requirements

* Python 3.7+
* Access to an SQL Server instance
* ZeptoMail service account (for email sending)

## Honorary Mention

Special honorary mention goes to our AI copilots—without whom this repo would look significantly less polished (and significantly more broken). 🚀😉
