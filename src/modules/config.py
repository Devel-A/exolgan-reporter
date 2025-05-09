import os
import json
import logging


def load_configs(config_file="reporter.conf") -> dict:
    """
    Loads configurations from the specified file in JSON format.
    
    Args:
        config_file (str): Path to the configuration file. Default 'reporter.conf'
        
    Returns:
        dict: Dictionary with loaded configurations
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file doesn't contain valid JSON
        Exception: For other errors during loading
    """
    try:
        # Check if the file exists
        if not os.path.isfile(config_file):
            error_msg = f"Configuration file not found: {config_file}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # Read the configuration file
        with open(config_file, 'r') as file:
            content = file.read()
            
            # Remove comments of type // at the beginning of lines
            lines = content.split('\n')
            cleaned_content = '\n'.join([line for line in lines if not line.strip().startswith('//')])
            
            # Try to load the JSON
            try:
                config_data = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                error_msg = f"Error in JSON structure of file {config_file}: {str(e)}"
                logging.error(error_msg)
                raise ValueError(error_msg)
                
            # Verify that the result is a dictionary
            if not isinstance(config_data, dict):
                error_msg = f"The configuration file must contain a valid JSON object"
                logging.error(error_msg)
                raise ValueError(error_msg)
                
            return config_data
            
    except (FileNotFoundError, ValueError) as e:
        # Re-raise these specific errors
        raise
    except Exception as e:
        error_msg = f"Error loading configuration file {config_file}: {str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)
