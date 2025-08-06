import os
import mysql.connector
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile
import re

def csv_table_import(folder, conn, conds, chars):
    # Establish connection to MySQL
    cursor = conn.cursor()

    # Loop through each CSV file in the folder
    for filename in os.listdir(folder):
        if filename.endswith('.csv'):
            print(f"File Name: {filename}")
            full_path = os.path.join(folder, filename)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(full_path, low_memory=False)
            df.replace(chars, "NULL", inplace=True)  # Replace '.' with NaN/nulls  
            print(f"Number of Rows: {len(df)}")
            
            # Table name based on CSV file name (without extension)
            raw_table_name = os.path.splitext(filename)[0]
            if conds[0]:
                table_name = format_table_name(raw_table_name)
            else:
                table_name = raw_table_name
                
            # Generate parameters for CREATE TABLE statement with detected data types
            columns = []
            for column in df.columns:
                series = df[column]
                for value in series:
                    if value not in [chars, "NULL", 0, "0"]:
                        dtype = detect_type(value)
                        break
                columns.append(f"`{column}` {dtype}")
                #print(column, ' = ', dtype)
            
            # save data frame into temporary csv file
            with NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as tmpfile:
                df.to_csv(tmpfile.name, index=False)
                temp_path = tmpfile.name
                safe_path = temp_path.replace("\\", "\\\\")  # Needed for MySQL on Windows

            # SQL queries
            drop_table_query = f"DROP TABLE IF EXISTS `{table_name}`;"
            create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(columns)});"
            load_data_query = f"""
            LOAD DATA LOCAL INFILE '{safe_path}' 
            INTO TABLE `{table_name}` 
            FIELDS TERMINATED BY ',' 
            ENCLOSED BY '"' 
            LINES TERMINATED BY '\n'
            IGNORE 1 rows;
            """
            #print(create_table_query)

            # Execute SQL Queries
            if conds[1]:
                print(f"Dropping old table ...")
                cursor.execute(drop_table_query)
            if conds[2]:
                print(f"Creating new table ...")
                cursor.execute(create_table_query)
            if conds[3]:
                print(f"Trying to load data ...")
                cursor.execute(load_data_query)
                print(f"{cursor.rowcount} rows inserted into MySQL Table: {table_name}\n")

            # delete temporary csv file
            os.remove(temp_path)
            conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

# determine data type
def detect_type(value):
    if isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        if value.is_integer():
            return "INT"
        return "FLOAT"
    elif isinstance(value, str):
        try:
            int_val = int(value)
            if '.' not in value:
                return "INT"
            if 'e' not in value.lower():
                return "INT"
        except ValueError:
            pass
        try:
            float_val = float(value)
            return "FLOAT"
        except ValueError:
            return "VARCHAR(255)"
    else:
        return "VARCHAR(255)"


# Clean up table name
def format_table_name(tbl_nm):
    # Replace sequences of spaces or hyphens with a single underscore
    frmt_nm = re.sub(r'[ -]+', '_', tbl_nm)
    return frmt_nm
