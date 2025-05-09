#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Reporter System - Main module
# Date: May 2025

import os
import sys
import argparse
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Internal modules
from modules.config import load_configs
from modules.database.sql_connection import SQLConnection
from modules.database.queries import get_ops_between_dates
from modules.excel import generate_excel_report
from modules.mail import send_email_with_attachment


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('reporter')


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Reporter - Generate and distribute reports based on SQL data"
    )
    
    # Define mutually exclusive group for date range options
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "-last_month",
        action="store_true",
        help="Generate report for the previous month"
    )
    
    # Add option for specific date range
    date_group.add_argument(
        "-between",
        type=str,
        metavar="START_DATE",
        help="Start date for report (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "-and",
        type=str,
        metavar="END_DATE",
        help="End date for report - required if -between is specified (format: YYYY-MM-DD)"
    )
    
    # Add optional config file location
    parser.add_argument(
        "-config",
        type=str,
        default="reporter.conf",
        help="Path to configuration file (default: reporter.conf)"
    )

    args = parser.parse_args()
    
    # Validate that if -between is specified, -and is also specified
    if args.between and not getattr(args, 'and'):
        parser.error('The -and argument is required when -between is specified')
    
    return args


def get_date_range(args: argparse.Namespace) -> Tuple[datetime.date, datetime.date]:
    """
    Determine the date range based on command line arguments.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments
    
    Returns:
        Tuple[datetime.date, datetime.date]: Start and end dates for the report
    
    Raises:
        ValueError: If dates are invalid
    """
    if args.last_month:
        today = datetime.date.today()
        # Get first day of current month
        first_day_current = datetime.date(today.year, today.month, 1)
        # Get last day of previous month by subtracting one day from first day of current month
        last_day_previous = first_day_current - datetime.timedelta(days=1)
        # Get first day of previous month
        first_day_previous = datetime.date(last_day_previous.year, last_day_previous.month, 1)
        
        return first_day_previous, last_day_previous
    else:
        try:
            start_date = datetime.datetime.strptime(args.between, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(getattr(args, 'and'), "%Y-%m-%d").date()
            
            # Validate that start date is not after end date
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
                
            return start_date, end_date
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")


def fetch_data(db_config: Dict[str, Any], start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
    """
    Fetch data from the database based on the date range.
    
    Args:
        db_config (Dict[str, Any]): Database connection configuration
        start_date (datetime.date): Start date for the query
        end_date (datetime.date): End date for the query
        
    Returns:
        List[Dict[str, Any]]: Query results as a list of dictionaries
        
    Raises:
        ConnectionError: If database connection fails
        Exception: For other database-related errors
    """
    try:
        # Create SQL connection
        connection = SQLConnection(
            server=db_config["connection_data"]["host"],
            database=db_config["connection_data"]["database"],
            username=db_config["connection_data"]["user"],
            password=db_config["connection_data"]["password"]
        )
        
        # Execute query with parameters
        params = (start_date, end_date)
        results = connection.exec(get_ops_between_dates, params)
        
        connection.close()
        
        return results
    except ConnectionError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise


def main():
    """
    Main function for Reporter application.
    """
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Set working directory to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        logger.info("Starting Reporter application")
        
        # Load configuration
        config_path = Path(args.config)
        if not config_path.is_absolute():
            config_path = Path(script_dir) / config_path
            
        logger.info(f"Loading configuration from {config_path}")
        config = load_configs(str(config_path))
        
        # Get date range for report
        start_date, end_date = get_date_range(args)
        logger.info(f"Generating report for period: {start_date} to {end_date}")
        
        # Fetch data from database
        logger.info("Fetching data from database")
        data = fetch_data(config["db"], start_date, end_date)
        logger.info(f"Retrieved {len(data)} records from database")
        
        if not data:
            logger.warning("No data to report for the specified period")
            print("No data found for the specified period")
            return 0
        
        # Generate Excel report
        logger.info("Generating Excel report")
        excel_data = generate_excel_report(data)
        logger.info(f"Excel report generated, size: {len(excel_data)} bytes")
        
        # Check if mail configuration exists and is complete
        if "mail" in config and all(key in config["mail"] for key in ["api_url", "api_key", "from_email", "from_name", "subject", "recipients"]):
            # Send email with attachment
            logger.info(f"Sending email to {len(config['mail']['recipients'])} recipients")
            email_sent = send_email_with_attachment(
                recipients=config["mail"]["recipients"],
                excel_attachment=excel_data,
                config=config["mail"]
            )
            
            if email_sent:
                logger.info("Email sent successfully")
                print("Report generated and sent via email successfully")
            else:
                logger.error("Failed to send email")
                print("Report generated but email sending failed")
        else:
            # Save Excel file locally if mail configuration is not complete
            report_filename = f"Report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
            with open(report_filename, "wb") as f:
                f.write(excel_data)
            logger.info(f"Email configuration incomplete - Report saved locally as {report_filename}")
            print(f"Report generated and saved as {report_filename} (Email configuration incomplete)")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())