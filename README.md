# CSV to MySQL Importer

A GUI application for importing CSV files into MySQL databases.

## Features

- Graphical user interface with dark theme
- Batch import of multiple CSV files from a folder
- Automatic data type detection
- Configurable MySQL connection settings
- Options to clean table names, drop existing tables, create new tables, and load data

## Compiling to Executable

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps to Compile

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the executable:**
   ```bash
   pyinstaller csv_import_gui.spec
   ```
   
   Or simply run the batch file:
   ```bash
   build.bat
   ```

3. **Find your executable:**
   The compiled executable will be in the `dist` folder as `CSV_Import_GUI.exe`

### Alternative Quick Build

If you prefer a simpler approach without the spec file:

```bash
pyinstaller --onefile --windowed --name "CSV_Import_GUI" csv_import_gui.py
```

## Usage

1. Run the executable
2. Select a folder containing CSV files
3. Enter your MySQL connection details
4. Configure import options
5. Click "Start Import"

## Dependencies

- tkinter (GUI framework)
- pandas (data manipulation)
- numpy (numerical operations)
- mysql-connector-python (MySQL database connection)

## Notes

- The executable will be larger due to included dependencies
- Make sure your MySQL server allows local file imports (`allow_local_infile=True`)
- The application does not handle primary or foreign key relationships 