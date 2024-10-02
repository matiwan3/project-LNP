import subprocess
import sqlite3
from datetime import datetime
import os
import time
import argparse

# Function to create or connect to the database
def connect_to_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    return sqlite3.connect('data/ping_data.db')

# Function to create a table if it does not exist for the current date
def create_table_if_not_exists(db_conn):
    today_str = datetime.now().strftime("%d%m%Y")  # Format: DDMMYYYY
    cursor = db_conn.cursor()
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS ping_{today_str} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        latency TEXT
    )
    '''
    cursor.execute(create_table_query)
    db_conn.commit()
    
# Function to retrieve all dates (table names) from the database
def get_all_dates(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Filter out tables that are not following the ping_date format
    date_tables = [table[0] for table in tables if table[0].startswith("ping_")]
    return date_tables

# Function to insert batch of pings into the database
def insert_pings_to_db(db_conn, ping_data):
    today_str = datetime.now().strftime("%d%m%Y")  # Format: DDMMYYYY
    cursor = db_conn.cursor()
    insert_query = f"INSERT INTO ping_{today_str} (timestamp, latency) VALUES (?, ?)"
    cursor.executemany(insert_query, ping_data)
    db_conn.commit()

# Function to log the terminal output to a log file
def log_to_file(log_data):
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_filename = f"{log_dir}/ping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_filename, 'w') as log_file:
        log_file.writelines(log_data)

# Function to ping and retrieve the results
def ping_google():
    command = ['ping', 'google.com', '-t']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return process

# Function to handle the ping data queries based on --ping flag
# Function to handle the ping data queries based on --ping flag
def handle_ping_queries(db_conn, date_str, ping_option):
    cursor = db_conn.cursor()

    if date_str == "all":
        # Get all tables (dates)
        date_tables = get_all_dates(db_conn)

        if not date_tables:
            print("No data available in the database.")
            return

        for table_name in date_tables:
            print(f"\nData for date: {table_name[5:]}")  # Strip 'ping_' from table name to show date

            if ping_option == "all":
                print(f"Fetching min, max, avg, and timeout for date: {table_name[5:]}")

                # Fetch min, max, avg and timeout
                handle_single_date_queries(db_conn, table_name, "min")
                handle_single_date_queries(db_conn, table_name, "max")
                handle_single_date_queries(db_conn, table_name, "avg")
                handle_single_date_queries(db_conn, table_name, "timeout")

            else:
                # Fetch specific ping data for all dates (e.g., min, max, avg, timeout)
                handle_single_date_queries(db_conn, table_name, ping_option)

    else:
        # If a specific date is provided
        table_name = f"ping_{date_str}"
        handle_single_date_queries(db_conn, table_name, ping_option)

# Function to query and print ping data for a single date (table)
def handle_single_date_queries(db_conn, table_name, ping_option):
    cursor = db_conn.cursor()

    if ping_option == "getAll":
        # Query to get all records, including timeouts
        select_query = f"SELECT timestamp, latency FROM {table_name}"
        cursor.execute(select_query)
        rows = cursor.fetchall()

        if not rows:
            print(f"No data found in table {table_name}.")
            return

        print(f"All ping records for {table_name[5:]}:")
        for row in rows:
            print(f"Timestamp: {row[0]}, Latency: {row[1]}")
    else:
        # Handle other ping options (max, min, avg, timeout)
        select_query = f"SELECT latency FROM {table_name} WHERE latency != 'Request timeout'"
        cursor.execute(select_query)
        rows = cursor.fetchall()

        if not rows:
            print(f"No data found in table {table_name}.")
            return

        pings = [int(row[0].replace('ms', '')) for row in rows]  # Convert to integer list

        if ping_option == "max":
            print(f"Max ping: {max(pings)}ms")
        elif ping_option == "min":
            print(f"Min ping: {min(pings)}ms")
        elif ping_option == "avg":
            average = sum(pings) / len(pings) if pings else 0
            print(f"Average ping: {average:.2f}ms")
        elif ping_option == "timeout":
            # Query for timeouts count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE latency = 'Request timeout'")
            timeout_count = cursor.fetchone()[0]
            print(f"Total timeouts: {timeout_count}")
        else:
            print("Invalid ping option.")
            
# Function to print usage information
def print_usage():
    usage_info = """
    Available options for the script:
    --date="DDMMYYYY"      : Specify the date for querying the ping data from the corresponding table (e.g., --date=30092024).
    --ping=[option]        : Choose the ping data to retrieve from the selected date:
                            - max: Returns the highest ping value.
                            - min: Returns the min ping value.
                            - avg: Returns the average ping value.
                            - timeout: Returns the total count of timeouts.
                            - getAll: Returns all the ping records, including timeouts (for debugging purposes).
    --usage                : Display this usage guide.
    """
    print(usage_info)

# Updated main function to handle "all" flag for --date and --ping
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Ping Google and store the data.")
    parser.add_argument('--date', type=str, help="Specify the date in DDMMYYYY format to look for in the database, or 'all' to query all dates.")
    parser.add_argument('--ping', type=str, help="Specify what type of ping data to retrieve: [max, min, avg, timeout, getAll, all].")
    parser.add_argument('--usage', action='store_true', help="Display usage information.")

    args = parser.parse_args()

    db_conn = connect_to_db()

    # If --usage flag is passed, print the usage information and exit
    if args.usage:
        print_usage()
        return

    # If --date and --ping options are passed, handle the queries
    if args.date and args.ping:
        handle_ping_queries(db_conn, args.date, args.ping)
    else:
        # No flags provided, run the ping process and store the data
        print("Starting ping process...")
        # Set up database and log data storage
        db_conn = connect_to_db()
        create_table_if_not_exists(db_conn)
        
        ping_data = []  # Store pings temporarily to be inserted in batches
        log_data = []   # Store logs to be written on exit
        ping_count = 0  # Counter for batching the database inserts
        
        # Start the pinging process
        process = ping_google()

        try:
            for line in process.stdout:
                current_time = datetime.now().strftime("%H:%M:%S")  # [HH:MM:SS]
                if "Reply from" in line:
                    latency = line.split('time=')[1].split('ms')[0] + "ms"
                    output = f"[{current_time}] {latency}"
                elif "Request timed out" in line:
                    output = f"[{current_time}] Request timeout."
                    latency = "Request timeout"
                else:
                    continue  # Skip lines that are not needed
                
                print(output)  # Display in terminal
                log_data.append(output + '\n')  # Store the output to log

                # Store the timestamp and latency in ping_data for batch insert
                ping_data.append((current_time, latency))
                ping_count += 1

                # Insert pings in batches of 10
                if ping_count >= 10:
                    insert_pings_to_db(db_conn, ping_data)
                    ping_data.clear()  # Clear the list after batch insert
                    ping_count = 0

        except KeyboardInterrupt:
            # On script exit, save the remaining data and log
            if ping_data:
                insert_pings_to_db(db_conn, ping_data)
            log_to_file(log_data)
            print("\nScript terminated, data saved.")
        
        finally:
            db_conn.close()
            process.terminate()

if __name__ == '__main__':
    main()
