import tkinter as tk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox,simpledialog,ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import uuid
import hashlib



class DatabaseObject:
    def __init__(self, connection):
        self.connection = connection

    @staticmethod
    def create_connection(host_name, user_name, user_password, db_name):
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("MySQL Database connection successful")
            return connection
        except Error as err:
            print(f"Error: '{err}'")
            return None

    def read(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result if result else []
        except Error as e:
            print(f"The error '{e}' occurred")
            return []

    def write(self, query, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, data)
            self.connection.commit()
            print("Query successful")
        except Error as e:
            print(f"The error '{e}' occurred")

class User(DatabaseObject):
    def __init__(self, connection, username, password):
        super().__init__(connection)
        self.username = username
        self.password = password

    def verify_login(self):
        sql = "SELECT user_id, hashed_password FROM users WHERE username = %s"
        result = self.read(sql, (self.username,))
        if result:
            user_id, hashed_password = result[0]
            if hashed_password == self.hash_password(self.password):
                print("Login successful")
                return user_id
            else:
                print("Incorrect password")
        else:
            print("Username not found")
        return None

    def create_user(self, email, department_id):
        hashed_password = self.hash_password(self.password)
        sql = """
        INSERT INTO users (email, username, department_id, hashed_password)
        VALUES (%s, %s, %s, %s)
        """
        self.write(sql, (email, self.username, department_id, hashed_password))

    @staticmethod
    def hash_password(password):
        hasher = hashlib.sha256()
        hasher.update(password.encode('utf-8'))
        return hasher.hexdigest()

class Player(DatabaseObject):
    def __init__(self, connection, name, user_id):
        super().__init__(connection)
        self.name = name
        self.user_id = user_id

    def get_stats(self):
        sql = """SELECT goals_scored, fouls_committed, assists_made, minutes_played
                 FROM player_stats WHERE player_id = %s"""
        return self.read(sql, (self.user_id,))

    def add_player(self, age, grade, position):
        sql = """INSERT INTO players (name, age, grade, position, user_id)
                 VALUES (%s, %s, %s, %s, %s)"""
        self.write(sql, (self.name, age, grade, position, self.user_id))

class TeamSheet(DatabaseObject):
    def __init__(self, connection, user_id):
        super().__init__(connection)
        self.user_id = user_id
        self.players = LinkedList()

    def save(self, week):
        # Assume a method to convert LinkedList to a list of player names
        player_names = self.players.to_list()
        for player_name in player_names:
            sql = """INSERT INTO team_sheets (user_id, week, player_name)
                     VALUES (%s, %s, %s)"""
            self.write(sql, (self.user_id, week, player_name))

class LinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        new_node = LinkedListNode(data)
        new_node.next = self.head
        self.head = new_node

    def remove(self, data):
        current = self.head
        prev = None
        while current and current.data != data:
            prev = current
            current = current.next
        if current:
            if prev:
                prev.next = current.next
            else:
                self.head = current.next

    def to_list(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements


class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop() if self.items else None

    def peek(self):
        return self.items[-1] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

actions_stack= Stack()



def get_current_user_id():
    global current_user_id
    return current_user_id

# Replace the following with your MySQL connection details
host = "localhost"
user = "root"
password = ""
database = "football_app"

# Create the database connection using the class method
connection = DatabaseObject.create_connection(host, user, password, database)

# GUI for registration
def registration():
    def register():
        email = entry_email.get()
        username = entry_username.get()
        department_id = entry_teacher_id.get()
        password = entry_password.get()
        confirm_password = entry_confirm_password.get()

        if password == confirm_password:
            db_object = DatabaseObject(connection)
            user = User(connection, username, password)
            user.create_user(email, department_id)
            messagebox.showinfo("Registration", "User created successfully")
            register_window.destroy()
        else:
            messagebox.showerror("Registration Error", "Passwords do not match.")

    # Create a new window
    register_window = tk.Toplevel()
    register_window.title("Register")

    # Create entry fields
    tk.Label(register_window, text="Email:").grid(row=0, column=0)
    entry_email = tk.Entry(register_window)
    entry_email.grid(row=0, column=1)

    tk.Label(register_window, text="Username:").grid(row=1, column=0)
    entry_username = tk.Entry(register_window)
    entry_username.grid(row=1, column=1)

    tk.Label(register_window, text="Teacher ID:").grid(row=2, column=0)  # Additional field for Teacher ID
    entry_teacher_id = tk.Entry(register_window)
    entry_teacher_id.grid(row=2, column=1)

    tk.Label(register_window, text="Password:").grid(row=3, column=0)
    entry_password = tk.Entry(register_window, show="*")
    entry_password.grid(row=3, column=1)

    tk.Label(register_window, text="Confirm Password:").grid(row=4, column=0)
    entry_confirm_password = tk.Entry(register_window, show="*")
    entry_confirm_password.grid(row=4, column=1)

    # Create a register button
    register_button = tk.Button(register_window, text="Register", command=register)
    register_button.grid(row=5, column=1, pady=10, sticky=tk.E)

    # Forgot Password Link (not functional in this example)
    forgot_password_label = tk.Label(register_window, text="Forgot Password?", fg="blue", cursor="hand2")
    forgot_password_label.grid(row=6, column=1, sticky=tk.W)
    forgot_password_label.bind("<Button-1>", lambda e: messagebox.showinfo("Reset Password", "Password reset not implemented."))

    register_window.mainloop()

# GUI for login
def logout(dashboard_window):
    dashboard_window.destroy()
    login()
# Function to create the main dashboard GUI
def main_dashboard(user_id, username):
    dashboard_window = tk.Tk()
    dashboard_window.title(f"{username}'s Football Team!")

    # Display user's username in the title (personalized dashboard)
    user_title_label = tk.Label(dashboard_window, text=f"{username}'s Football Team!", font=("Helvetica", 16))
    user_title_label.pack(pady=20)

    # Button to edit team sheets
    team_sheets_button = tk.Button(dashboard_window, text="Team Sheets", command=lambda: edit_team_sheets(user_id, username))
    team_sheets_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Button to view player stats
    player_stats_button = tk.Button(dashboard_window, text="Player Stats", command=lambda: view_player_stats(user_id))
    player_stats_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Button to view player list
    player_list_button = tk.Button(dashboard_window, text="Player List", command=lambda: view_player_list(user_id))
    player_list_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Logout button
    logout_button = tk.Button(dashboard_window, text="Logout", command=lambda: logout(dashboard_window))
    logout_button.pack(pady=10, anchor=tk.NE)

    dashboard_window.mainloop()


team_sheets_df = pd.DataFrame(columns=['Week', 'GK', 'LB', 'CB', 'RB', 'LW', 'CM', 'RW', 'ST', 'Substitutes'])

# Function to update the DataFrame with a new team sheet
def update_team_sheet(week, positions, substitutes):
    global team_sheets_df
    # Create a new entry for the DataFrame
    new_sheet = {'Week': week}
    new_sheet.update(positions)
    new_sheet['Substitutes'] = substitutes
    team_sheets_df = team_sheets_df.append(new_sheet, ignore_index=True)
    print(team_sheets_df)

def handle_substitute(sub_btn, position_label):
    player_name = simpledialog.askstring("Input", f"Enter player name for {position_label}:")
    if player_name:
        sub_btn.config(text=player_name)



def edit_team_sheets(user_id, username):
    team_sheet_window = tk.Toplevel()
    team_sheet_window.title("Team Sheets")
    team_positions={}
    team_substitutes={}
    buttons = {}
    sub_buttons={}

    positions = {
        'GK': (350, 30), 'LB': (50, 105), 'CB1': (175, 105), 'CB2': (525, 105), 'RB': (650, 105),
        'CM1': (275, 200), 'CM2': (350, 200), 'CM3': (425, 200),
        'LW': (50, 295), 'ST': (350, 295), 'RW': (650, 295),
    }

    def update_positions(position_label, player_name, is_substitute, substitute_buttons):
        if is_substitute:
            team_substitutes[position_label] = player_name
            for sub_btn in substitute_buttons[position_label]:
                print(player_name)
                sub_btn.config(text=player_name)
        else:
            team_positions[position_label] = player_name
            for pos, btn_list in buttons.items():
                print(player_name)
                print(pos)
                if pos == position_label:
                    for btn in btn_list:
                        btn.config(text=player_name)


    # Function to prompt for player name and update button text
    def prompt_player_name(position_label, is_substitute):
        player_name = simpledialog.askstring("Input", f"Enter player name for {position_label}:")
        if player_name:
            button_dict = sub_buttons if is_substitute else buttons
            button_dict[position_label].config(text=player_name)
            action = {
                "type": "position_update",
                "position_label": position_label,
                "previous_player": button_dict[position_label].cget("text"),
                "new_player": player_name
            }
            actions_stack.push(action)
            # Update the team_positions or team_substitutes dictionary
            if is_substitute:
                team_substitutes[position_label.replace(" Sub", "")] = player_name
            else:
                team_positions[position_label] = player_name

        # Function to undo the last action
    def undo_last_action():
        if not actions_stack.is_empty():
            last_action = actions_stack.pop()
            if last_action["type"] == "position_update":
                position_label = last_action["position_label"]
                previous_player = last_action["previous_player"]
                buttons[position_label].config(text=previous_player)
                print(f"Undid change of {position_label} from {last_action['new_player']} to {previous_player}")

    # Function to draw the soccer field lines
    def draw_field(canvas):
        canvas.create_rectangle(10, 10, 690, 390, outline="black")  # Field outline
        canvas.create_line(10, 200, 690, 200, fill="black")  # Midfield horizontal line
        canvas.create_oval(340, 180, 360, 220, outline="black")  # Center circle

    #Function to create buttons for player positions
    def create_position_buttons(canvas, positions, is_substitute):
        button_dict = sub_buttons if is_substitute else buttons
        for pos, (x, y) in positions.items():
            pos_label = f"{pos} Sub" if is_substitute else pos
            btn = tk.Button(canvas, text=pos_label,
                            command=lambda pos=pos_label: prompt_player_name(pos, is_substitute))
            canvas.create_window(x, y, window=btn, anchor="center")
            button_dict[pos_label] = btn

    field_canvas_width = 690
    field_canvas_height = 390

    # Create a canvas for the main field
    field_canvas = tk.Canvas(team_sheet_window, width=field_canvas_width, height=field_canvas_height, bg='lightgrey')
    field_canvas.grid(row=1, column=0, columnspan=8, pady=20, padx=20)

    selected_week = tk.IntVar(value=1)  # Default to week 1

    # Create a canvas for the substitutes field
    substitutes_field_canvas = tk.Canvas(team_sheet_window, width=field_canvas_width, height=field_canvas_height,
                                         bg='lightgrey')
    substitutes_field_canvas.grid(row=1, column=8, columnspan=8, pady=20, padx=20)


    # # Draw the main field with player position buttons
    # draw_field(team_sheet_window, field_canvas, positions, is_substitute=False, on_click=prompt_player_name)
    #
    # # Draw the substitutes field with player position buttons
    # draw_field(team_sheet_window, substitutes_field_canvas, positions, is_substitute=True, on_click=prompt_player_name)

    def save_team_sheet(connection, user_id, team_positions, team_substitutes, week):
        week = simpledialog.askinteger("Input", "Enter the week number:")
        if week is not None:
            try:
                db_object = DatabaseObject(connection)

                # Delete previous team sheets for the same user and week
                delete_query = "DELETE FROM original_team WHERE user_id = %s AND week = %s"
                db_object.write(delete_query, (user_id, week))
                delete_query = "DELETE FROM substitute_team WHERE user_id = %s AND week = %s"
                db_object.write(delete_query, (user_id, week))

                # Insert players from the original team into the players table
                for player_name in team_positions.values():
                    if player_name:  # Skip empty player names
                        # Check if the player already exists in the players table
                        check_query = "SELECT * FROM players WHERE name = %s"
                        player_exists = db_object.read(check_query, (player_name,))
                        if not player_exists:
                            # Insert the player into the players table
                            insert_query = "INSERT INTO players (name, user_id) VALUES (%s, %s)"
                            db_object.write(insert_query, (player_name, user_id))

                # Insert the original and substitute team positions
                for position, player_name in {**team_positions, **team_substitutes}.items():
                    if player_name:  # Skip empty player names
                        insert_query = "INSERT INTO team_sheets (user_id, week, player_name, position) VALUES (%s, %s, %s, %s)"
                        db_object.write(insert_query, (user_id, week, player_name, position))

                print("Team sheet saved successfully for week", week)
                messagebox.showinfo("Success", "Team sheet saved successfully for week {}".format(week))

            except Exception as e:
                print("An error occurred while saving the team sheet:", e)
                messagebox.showerror("Error", "An error occurred while saving the team sheet: {}".format(e))
        else:
            messagebox.showwarning("Input Required", "No Week number entered")

    def set_week(week):
        selected_week.set(week)

    # Function to create clickable week buttons
    def create_week_buttons():
        for i in range(1, 8):
            week_button = tk.Button(team_sheet_window, text=f"Week {i}", command=lambda i=i: selected_week.set(i))
            week_button.grid(row=0, column=i, padx=10, pady=5)

    # Create a canvas for the main field and draw the field lines
    field_canvas = tk.Canvas(team_sheet_window, width=field_canvas_width, height=field_canvas_height, bg='lightgrey')
    field_canvas.grid(row=1, column=0, columnspan=8, pady=20, padx=20)
    draw_field(field_canvas)  # Draw the main field lines
    create_position_buttons(field_canvas, positions, False)  # False for not substitute

    # Create a canvas for the substitutes field and draw the field lines
    substitutes_field_canvas = tk.Canvas(team_sheet_window, width=field_canvas_width, height=field_canvas_height,
                                         bg='lightgrey')
    substitutes_field_canvas.grid(row=1, column=8, columnspan=8, pady=20, padx=20)
    draw_field(substitutes_field_canvas)  # Draw the substitutes field lines
    create_position_buttons(substitutes_field_canvas, positions, True)  # True for substitute

    # Save Team Sheet button
    save_button = tk.Button(team_sheet_window, text="Save Team Sheet",
                            command=lambda: save_team_sheet(connection, user_id, team_positions, team_substitutes,
                                                            selected_week.get()))
    save_button.grid(row=2, column=3, pady=10)



    team_sheet_window.mainloop()

# Function to fetch player stats from the database
def get_player_stats(player_name):

    if player_name is None or player_name == "":
        # Return stats as "N/A" if no player is selected
        stats = {
            'minutes_played': "N/A",
            'goals_scored': "N/A",
            'fouls_committed': "N/A",
            'assists_made': "N/A"
        }
    else:
        # Query to get the player's ID based on the name
        player_id_query = "SELECT player_id FROM players WHERE name = %s"

        # Query to get the player's stats
        stats_query = """SELECT 
            ps.goals_scored, 
            ps.fouls_committed, 
            ps.assists_made,
            (SELECT GROUP_CONCAT(minutes_played SEPARATOR ',') 
             FROM player_game_week_stats pgws 
             WHERE pgws.player_id = ps.player_id) AS minutes_played_list
        FROM player_stats AS ps
        WHERE ps.player_id = %s;"""

        try:
            db_object = DatabaseObject(connection)
            player_id_result = db_object.read(player_id_query, (player_name,))
            if player_id_result:
                player_id = player_id_result[0][0]

                # Fetch the player's stats using the player's ID

                stats_result = db_object.read(stats_query, (player_id,))

                # If stats exist, aggregate minutes played into a list and fetch other stats
                if stats_result:
                    goals_scored = stats_result[0][0]
                    fouls_committed = stats_result[0][1]
                    assists_made = stats_result[0][2]
                    minutes_played = stats_result[0][3]

                    minutes_played = [row[1] for row in stats_result]
                    total_minutes_played = sum(minutes_played)
                else:
                    minutes_played = []  # Set minutes played to "N/A" if no stats found
                    goals_scored = 0
                    fouls_committed = 0
                    assists_made = 0

                stats = {
                    'minutes_played': minutes_played,
                    'goals_scored': goals_scored,
                    'fouls_committed': fouls_committed,
                    'assists_made': assists_made
                }
            else:
                # If player ID is not found, set stats to "N/A"
                stats = {
                    'minutes_played': "N/A",
                    'goals_scored': "N/A",
                    'fouls_committed': "N/A",
                    'assists_made': "N/A"
                }
        except Exception as e:
            print(f"An error occurred: {e}")
            stats = {
                'minutes_played': [],
                'goals_scored': 0,
                'fouls_committed': 0,
                'assists_made': 0
            }

    return stats

def view_player_stats(user_id):
    print(f"Viewing player stats for user ID: {user_id}")
    window = tk.Tk()
    window.title("Player Stats")

    players_frame = tk.Frame(window)
    players_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Corrected to use 'read' method
    players_query = "SELECT name, player_id FROM players WHERE user_id = %s"
    db_object = DatabaseObject(connection)
    players = db_object.read(players_query, (user_id,))

    players_listbox = tk.Listbox(players_frame)
    for player_name, _ in players:
        players_listbox.insert(tk.END, player_name)
    players_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    stats_frame = tk.Frame(window)
    stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    minutes_played_label = tk.Label(stats_frame, text="Minutes Played")
    minutes_played_label.pack()
    minutes_played_entry = tk.Entry(stats_frame)
    minutes_played_entry.pack()

    goals_scored_label = tk.Label(stats_frame, text="Goals Scored")
    goals_scored_label.pack()
    goals_scored_entry = tk.Entry(stats_frame)
    goals_scored_entry.pack()

    fouls_committed_label = tk.Label(stats_frame, text="Fouls/Cards Committed")
    fouls_committed_label.pack()
    fouls_committed_entry = tk.Entry(stats_frame)
    fouls_committed_entry.pack()

    assists_made_label = tk.Label(stats_frame, text="Assists made")
    assists_made_label.pack()
    assists_made_entry = tk.Entry(stats_frame)
    assists_made_entry.pack()

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=stats_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update_graph(minutes_played):
        ax.clear()

        # Check if minutes_played is not "N/A" and is a list with data
        if isinstance(minutes_played, list) and minutes_played != ["N/A"]:
            # Plot the new graph
            ax.plot(range(1, len(minutes_played) + 1), minutes_played, marker='o')
            ax.set_xticks(range(1, len(minutes_played) + 1))
            ax.set_xticklabels(range(1, len(minutes_played) + 1))
        else:
            # Handle case with no data or "N/A"
            ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes)

        ax.set_title('Minutes Played Per Game Week')
        ax.set_xlabel('Game Week')
        ax.set_ylabel('Minutes Played')

        # Redraw the canvas with the updated graph
        canvas.draw()

    def update_stats_display(player_name):
        stats = get_player_stats(player_name)
        if stats:
            # Assuming stats is a dictionary; directly use the keys to update UI elements
            minutes_played_entry.delete(0, tk.END)
            minutes_played_entry.insert(0, stats.get('minutes_played', "N/A"))
            goals_scored_entry.delete(0, tk.END)
            goals_scored_entry.insert(0, stats.get('goals_scored', "N/A"))
            fouls_committed_entry.delete(0, tk.END)
            fouls_committed_entry.insert(0, stats.get('fouls_committed', "N/A"))
            assists_made_entry.delete(0, tk.END)
            assists_made_entry.insert(0, stats.get('assists_made', "N/A"))

            # Update the graph, ensure minutes_played is a list before passing
            if isinstance(stats['minutes_played'], list):
                update_graph(stats['minutes_played'])
            else:
                print("Error: Expected 'minutes_played' to be a list.")
        else:
            print("No stats found for the selected player.")


    # Function to handle player selection
    def on_player_selected(event):
        selection = players_listbox.curselection()
        if selection:
            index = selection[0]
            player_name = players[index][0]  # Get the player name
            update_stats_display(player_name)

    players_listbox.bind('<<ListboxSelect>>', on_player_selected)

    # Start the main loop
    window.mainloop()

# Function to create player list GUI
def create_player_list_gui(connection):
    window = tk.Tk()
    window.title("Player Information")

    # Define columns
    columns = ("Player Name", "Age", "Grade", "Position", "Minutes Allocated")

    # Create Treeview widget
    tree = ttk.Treeview(window, columns=columns, show='headings')
    tree.pack(side="left", fill="both", expand=True)

    # Define headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True)

    # Function to refresh the player list display
    def refresh_player_list():
        for i in tree.get_children():
            tree.delete(i)
        display_player_list()

    # Function to display the player list
    def display_player_list():
        query = "SELECT player_id, name, age, grade, position, minutes_played FROM players"
        try:
            db_object = DatabaseObject(connection)
            players = db_object.read(query)
            for player in players:
                player_id, name, age, grade, position, minutes_played = player
                tree.insert('', 'end', values=(name, age, grade, position, minutes_played))
        except Exception as e:
            print(f"An error occurred: {e}")

    # Function to get the ID of the selected player
    def get_selected_player_details(tree):
        selected_item = tree.selection()
        if selected_item:  # If there is a selected item
            item = tree.item(selected_item)
            return item['values']  # Return the details of the selected player
        return None  # If no item is selected, return None

    # Function to add a new player
    def add_player():
        add_window = tk.Toplevel(window)
        add_window.title("Add New Player")

        # Entry widgets to input player details
        tk.Label(add_window, text="Player Name:").grid(row=0, column=0)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1)

        tk.Label(add_window, text="Age:").grid(row=1, column=0)
        age_entry = tk.Entry(add_window)
        age_entry.grid(row=1, column=1)

        tk.Label(add_window, text="Grade:").grid(row=2, column=0)
        grade_entry = tk.Entry(add_window)
        grade_entry.grid(row=2, column=1)

        tk.Label(add_window, text="Position:").grid(row=3, column=0)
        position_entry = tk.Entry(add_window)
        position_entry.grid(row=3, column=1)


        tk.Label(add_window, text="Minutes Played:").grid(row=4, column=0)
        minutes_played_entry = tk.Entry(add_window)
        minutes_played_entry.grid(row=4, column=1)

        # Function to process the new player data and add it to the database
        def save_new_player():
            name = name_entry.get()
            age = age_entry.get()
            grade = grade_entry.get()
            position = position_entry.get()
            minutes_played = minutes_played_entry.get()
            current_user_id = get_current_user_id()
            query = "INSERT INTO players (name, age, grade, position,minutes_played) VALUES (%s, %s, %s, %s, %s)"
            db_object = DatabaseObject(connection)
            db_object.write(query, (name, age, grade, position,minutes_played))

            add_window.destroy()
            refresh_player_list()

        # Save button to trigger the save_new_player function
        save_button = tk.Button(add_window, text="Save", command=save_new_player)
        save_button.grid(row=4, column=1)

    def get_selected_player_id(tree, connection):
        selected_item = tree.selection()
        if selected_item:
            item = tree.item(selected_item)
            player_name = item['values'][0]  # Assuming the first value is the player's name

            # Construct a query to fetch player_id using the player's name
            query = "SELECT player_id FROM players WHERE name = %s"
            db_object = DatabaseObject(connection)
            player_id = db_object.read(query, (player_name,))

            if player_id:
                return player_id[0][0]  # Assuming player_id is the first value of the first row
        return None

    # Function to add a new player
    def edit_selected_player():
        player_id = get_selected_player_id(tree, connection)
        if player_id is None:
            messagebox.showwarning("No Selection", "Please select a player to edit.")
            return

        # Fetch player details from the database using the player_id
        query = "SELECT name, age, grade, position, minutes_played FROM players WHERE player_id = %s"
        db_object = DatabaseObject(connection)
        player_details = db_object.read(query, (player_id,))
        if player_details:
            player_details = player_details[0]

            # Create an edit window
            edit_window = tk.Toplevel(window)
            edit_window.title("Edit Player")

            # Dictionary to hold entry widgets corresponding to player details
            entries = {}

            # Labels for each player detail
            labels = ["Player Name", "Age", "Grade", "Position", "Minutes Allocated"]
            player_fields = ["name", "age", "grade", "position", "minutes_played"]

            # Create entry fields pre-filled with the player's current details
            for i, (label, field) in enumerate(zip(labels, player_fields)):
                tk.Label(edit_window, text=label).grid(row=i, column=0)
                entry = tk.Entry(edit_window)
                entry.grid(row=i, column=1)
                if i < len(player_details):  # Check if the index is within the range of player_details
                    entry.insert(0, player_details[i] if player_details[i] is not None else "N/A")
                else:
                    entry.insert(0, "N/A")  # Insert a default value if the index is out of range
                entries[field] = entry

            # Function to update the player details in the database
            def submit_edits():
                # Collect updates; only include fields where the entry differs from the original value
                updates = {field: entry.get() for field, entry in entries.items() if
                           entry.get() != str(player_details[player_fields.index(field)])}
                for field, entry in entries.items():
                    new_value = entry.get()
                    old_value = player_details[player_fields.index(field)]
                    if new_value != str(old_value):
                        if field == "age" or field == "minutes_played":
                            try:
                                int(new_value)  # Check if value is an integer
                                updates[field] = new_value
                            except ValueError:
                                messagebox.showerror("Invalid Input", f"{field.capitalize()} must be an integer.")
                                return
                        else:
                            updates[field] = new_value

                if new_value != str(old_value):
                    if field == "age":
                        try:
                            int(new_value)  # Check if age is an integer
                            updates[field] = new_value
                        except ValueError:
                            messagebox.showerror("Invalid Input", "Age must be an integer.")
                            return
                    elif field == "grade":
                        if len(new_value) < 2:
                            messagebox.showerror("Invalid Input", "Grade must have at least 2 characters.")
                            return
                        else:
                            updates[field] = new_value
                    elif field == "minutes_played":
                        try:
                            int(new_value)  # Check if minutes allocated is an integer
                            updates[field] = new_value
                        except ValueError:
                            messagebox.showerror("Invalid Input", "Minutes Allocated must be an integer.")
                            return
                    elif field == "name":
                        if len(new_value) < 2:
                            messagebox.showerror("Invalid Input", "Name must have at least 2 characters.")
                            return
                        else:
                            updates[field] = new_value
                    else:
                        updates[field] = new_value

                if updates:
                    # Generate the SET clause for the UPDATE query
                    set_clause = ', '.join(f"{field} = %s" for field in updates.keys())
                    values = list(updates.values())
                    # Ensure player_id is part of the parameters

                    parameters = tuple(values)+(player_id,)

                    # Construct and execute the UPDATE query
                    update_query = f"UPDATE players SET {set_clause} WHERE player_id = %s"
                    try:
                        # Execute the UPDATE query
                        db_object.write(update_query, parameters)
                        messagebox.showinfo("Success", "Player details updated successfully.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred while updating player details: {e}")

                edit_window.destroy()
                refresh_player_list()  # Refresh the player list to reflect the updates

            # Submit button to apply the changes
            submit_button = tk.Button(edit_window, text="Submit", command=submit_edits)
            submit_button.grid(row=len(labels), column=1)


    # Function to delete the selected player based on details
    def delete_selected_player(tree):
        player_details = get_selected_player_details(tree)
        print(player_details)
        if player_details:
            name, age, grade, position, minutes_played = player_details
            # Ask for confirmation before deleting
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete player {name}?"):
                # Construct the DELETE query with placeholder for each detail
                query = "DELETE FROM players WHERE name = %s AND age = %s AND grade = %s AND position = %s AND minutes_played = %s"
                try:
                    # Execute the DELETE query with player details
                    db_object = DatabaseObject(connection)
                    db_object.write( query, (name, age, grade, position, minutes_played))
                    refresh_player_list()
                except Exception as e:
                    print(f"An error occurred: {e}")
        else:
            messagebox.showwarning("No Selection", "Please select a player to delete.")

    # Add button to add new player
    add_button = tk.Button(window, text="Add Player", command=add_player)
    add_button.pack(side="top", fill="x")

    #Edit the existing player
    update_button = tk.Button(window, text="Update Player", command=edit_selected_player)
    update_button.pack(side="top", fill="x")

    # delete a selected player
    delete_button = tk.Button(window, text="Delete Player", command=lambda: delete_selected_player(tree))
    delete_button.pack(side="top", fill="x")

    # Display the player list
    display_player_list()


    window.mainloop()
def view_player_list(user_id):
    print(f"Viewing player list for user ID: {user_id}")
    create_player_list_gui(connection)


def login():
    def attempt_login():
        global current_user_id

        username = entry_username.get()
        password = entry_password.get()

        # Instantiate a User object
        user = User(connection, username, password)

        # Verify the login credentials using the User object method
        user_id = user.verify_login()

        if user_id:
            current_user_id = user_id
            messagebox.showinfo("Login", f"User {username} logged in with ID: {user_id}")
            login_window.destroy()
            main_dashboard(user_id, username)
        else:
            messagebox.showerror("Login Error", "Invalid username or password")

    # Create a new window
    login_window = tk.Tk()
    login_window.title("Login")

    # Create entry fields
    tk.Label(login_window, text="Email:").grid(row=0, column=0)
    entry_email = tk.Entry(login_window)
    entry_email.grid(row=0, column=1)

    tk.Label(login_window, text="Username:").grid(row=1, column=0)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=1, column=1)

    tk.Label(login_window, text="Password:").grid(row=2, column=0)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=2, column=1)

    # Create a login button
    login_button = tk.Button(login_window, text="Login", command=attempt_login)
    login_button.grid(row=3, column=1, pady=10, sticky=tk.E)

    # Create a register button on the login window to open the registration form
    register_button = tk.Button(login_window, text="Register", command=registration)
    register_button.grid(row=4, column=0, columnspan=2)

    login_window.mainloop()

# Launch the login window
if __name__ == "__main__":
    login()