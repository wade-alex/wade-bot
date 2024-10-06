import subprocess
import os
import psycopg2
import sys


def connect_db():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None


def run_python_file(file_path):
    try:
        # Use the same Python interpreter that's running this script
        python_executable = sys.executable
        subprocess.run([python_executable, file_path], check=True)
        print(f"Successfully executed: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {file_path}: {e}")


def run_sql_file(file_path, conn):
    try:
        with open(file_path, 'r') as sql_file:
            sql_content = sql_file.read()

        with conn.cursor() as cur:
            cur.execute(sql_content)
        conn.commit()
        print(f"Successfully executed SQL file: {file_path}")
    except (psycopg2.Error, IOError) as e:
        print(f"Error executing SQL file {file_path}: {e}")
        conn.rollback()


def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the project root (assuming the script is in src/app/__scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

    # Define the files to be executed in order with relative paths
    files = [
        os.path.join(project_root, "database", "ETL", "futbin_players_prices_ETL_VM.py"),
        os.path.join(project_root, "database", "ETL", "fut_gg_sbc_ETL_VM.py"),
        os.path.join(project_root, "database", "SQL", "reporting.reg_fodder.sql"),
        os.path.join(project_root, "database", "SQL", "reporting.reg_fodder_table.sql"),
        os.path.join(project_root, "src", "app", "__scripts", "fodder_page.py")
    ]

    # Establish database connection
    conn = connect_db()
    if conn is None:
        return

    try:
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            if file_path.endswith('.py'):
                run_python_file(file_path)
            elif file_path.endswith('.sql'):
                run_sql_file(file_path, conn)
            else:
                print(f"Unsupported file type: {file_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()