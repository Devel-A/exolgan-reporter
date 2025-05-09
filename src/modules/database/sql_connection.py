import pyodbc
import logging
from typing import Dict, List, Any, Optional, Union


class SQLConnection:
    """
    A class for connecting to and executing operations on a Microsoft SQL Server database using pyodbc.
    """
    def __init__(self, server: str, database: str, username: str = None, password: str = None, 
                 trusted_connection: bool = False, driver: str = "ODBC Driver 17 for SQL Server"):
        """
        Initialize the SQL connection with the provided parameters.
        
        Args:
            server (str): The server name or IP address
            database (str): The database name
            username (str, optional): The username for authentication. Defaults to None.
            password (str, optional): The password for authentication. Defaults to None.
            trusted_connection (bool, optional): Whether to use Windows Authentication. Defaults to False.
            driver (str, optional): The ODBC driver to use. Defaults to "ODBC Driver 17 for SQL Server".
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.driver = driver
        self.conn = None
        self.cursor = None
        
        # Auto-connect when instance is created
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the database using the provided parameters.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            connection_string = f"DRIVER={{{self.driver}}};"
            connection_string += f"SERVER={self.server};"
            connection_string += f"DATABASE={self.database};"
            
            if self.trusted_connection:
                connection_string += "Trusted_Connection=yes;"
            else:
                if not self.username or not self.password:
                    raise ValueError("Username and password are required when not using trusted connection")
                connection_string += f"UID={self.username};"
                connection_string += f"PWD={self.password};"
            
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            logging.error(f"Failed to connect to database: {str(e)}")
            return False
            
    def is_connected(self) -> bool:
        """
        Check if the connection to the database is active.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        if not self.conn:
            return False
        
        try:
            # Simple query to test connection
            self.cursor.execute("SELECT 1")
            return True
        except:
            return False
            
    def reconnect_if_needed(self) -> bool:
        """
        Reconnect to the database if the connection is not active.
        
        Returns:
            bool: True if connected or reconnection successful, False otherwise.
        """
        if self.is_connected():
            return True
            
        return self.connect()
    
    def exec(self, script: str, params: Optional[Dict[str, Any]] = None) -> Union[List[Dict[str, Any]], int]:
        """
        Execute a SQL script, optionally with parameters.
        
        Args:
            script (str): The SQL script to execute
            params (Optional[Dict[str, Any]], optional): Parameters for the script. Defaults to None.
            
        Returns:
            Union[List[Dict[str, Any]], int]: 
                - If the script returns results: A list of dictionaries with the results
                - If the script modifies data: The number of affected rows
                
        Raises:
            ConnectionError: If unable to connect to the database
            Exception: For any other errors during execution
        """
        # Ensure connection is active
        if not self.reconnect_if_needed():
            error_msg = "Failed to connect to database"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
            
        try:
            # Execute the script with or without parameters
            if params:
                self.cursor.execute(script, params)
            else:
                self.cursor.execute(script)
                
            # Try to fetch results
            try:
                columns = [column[0] for column in self.cursor.description]
                results = []
                
                for row in self.cursor.fetchall():
                    results.append({columns[i]: value for i, value in enumerate(row)})
                
                self.conn.commit()
                return results
            except:
                # If no results returned (for INSERT, UPDATE, DELETE operations)
                affected_rows = self.cursor.rowcount
                self.conn.commit()
                return affected_rows
                
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error executing SQL script: {str(e)}")
            raise
            
    def close(self):
        """
        Close the database connection.
        """
        if self.cursor:
            self.cursor.close()
            
        if self.conn:
            self.conn.close()
            
        self.cursor = None
        self.conn = None
        
    def __del__(self):
        """
        Destructor to ensure connections are closed when object is destroyed.
        """
        self.close()
