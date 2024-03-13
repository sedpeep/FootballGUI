# FootballGUI Project

This repository contains the code for the FootballGUI project, a Python application for managing football-related data.

## Prerequisites

Before running the FootballGUI project, ensure you have the following:
- PyCharm Professional and MySQL installed on your system.

## Getting Started

To get started with the FootballGUI project, follow these steps:

1. Clone this repository to your local machine.
2. Open PyCharm Professional and create a new Python project.
3. Copy and paste the contents of the project folder into the newly created Python project directory.
4. In PyCharm, navigate to the `FootballGUI.py` file located within the project directory.
5. Look for the database icon on the right side of the PyCharm interface and click on it.
6. Click the "+" icon to add a new database connection, then select MySQL.
7. Enter your MySQL username and password. By default, the username is "root", but if you have a different one, you can enter that.
8. After adding the database connection, a console window will open.
9. Open the `football_app.sql` file located in the project directory and copy the SQL code from it.
10. Paste the copied SQL code into the console window and execute the script.
11. In the `FootballGUI.py` file, navigate to line 181 and replace the following placeholders with your MySQL connection details:
    ```python
    # Replace the following with your MySQL connection details
    host = "localhost"
    user = "root"
    password = ""
    database = "football_app"
    ```
12. Save the changes made to the `FootballGUI.py` file.
13. Execute the program by running the `FootballGUI.py` file.

## Usage

Once the project is set up and running, you can use the FootballGUI application to manage football-related data efficiently.
