# Local Network Performance Logger

This project is a simple command-line tool that pings Google's servers, logs the results to a database, and allows you to query the logged data. It uses SQLite for data storage and provides various options to retrieve ping statistics.

## Features

- **Pinging Google:** Continuously pings Google and records latency.
- **Database Storage:** Saves ping results in an SQLite database with a separate table for each day.
- **Batch Insertion:** Collects ping data in batches to optimize database writes.
- **Logging:** Outputs ping results to the terminal and saves them in log files.
- **Data Retrieval:** Allows querying of ping data based on specific dates and options.

## Installation

Make sure you have Python installed (Python 3.6 or later). You also need to have the SQLite library available, which is included with the standard Python installation.

Clone this repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```

## Usage 

To run the script, use the following command:

```bash
python ping_logger.py [OPTIONS]
```

### Options
- --date="DDMMYYYY": Specify the date to query the ping data from the corresponding table (e.g., --date=30092024).
- --ping=[option]: Choose the type of ping data to retrieve from the selected date:
max: Returns the highest ping value.  
low: Returns the lowest ping value.  
medium: Returns the average ping value.  
timeout: Returns the total count of timeouts.  
getAll: Returns all the ping records, including timeouts (for debugging purposes).  
- --usage: Display usage information.

## Example Commands 
1. Start Ping Process and Log Data
```bash
python ping_logger.py
```  
This command starts the pinging process and logs the data into the database.
2. Retrieve Ping Data for a Specific Date
```bash
python ping_logger.py --date="30092024" --ping="max"
```
This command retrieves the maximum ping value from the logs for the specified date.
3. Get All Logs for a Specific Date
```bash
python ping_logger.py --date="30092024" --ping="getAll"
```
This command retrieves all ping records for the specified date, including timeouts.
4. Display Usage Information
```bash
python ping_logger.py --usage
```
This command displays the usage instructions.

## Logging and Data Storage
- The script creates a folder named data to store the SQLite database (ping_data.db).
- Log files are stored in a logs directory, named with the current timestamp.

## Code Structure
- connect_to_db: Creates or connects to the SQLite database.
- create_table_if_not_exists: Creates a new table for the current date if it doesn't exist.
- insert_pings_to_db: Inserts collected ping data into the database.
- log_to_file: Saves terminal output to a log file.
- ping_google: Executes the ping command to Google.
- handle_ping_queries: Processes the user queries based on provided flags.
- print_usage: Displays usage instructions.

## Example Log
- running the script  
![image](https://github.com/user-attachments/assets/7a00c7ef-d42f-4145-8c4e-4298d9bf971f)  


- getting the min | max | avg | timeout ping values for specific date  
![image](https://github.com/user-attachments/assets/522629cd-983d-40c4-96b4-126a52eefbdc)  
![image](https://github.com/user-attachments/assets/40d74c5e-d984-472d-9717-32c67c241e1e)

