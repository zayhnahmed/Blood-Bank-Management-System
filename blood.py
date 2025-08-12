from tkinter import messagebox, ttk
from customtkinter import *
from tkcalendar import Calendar
from pymongo import MongoClient
from datetime import datetime
import tkinter as tk

# Database setup
client = MongoClient("mongodb://localhost:27017/")
db = client['blood_bank']
users_collection = db['users']
donors_collection = db['donors']
donations_collection = db['donations']
inventory_collection = db['blood_inventory']

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Bank Management System")
        self.root.after(0, lambda: root.state('zoomed'))
        
        # Initialize current user
        self.current_user = None
        
        # Load login screen by default
        self.show_login_screen()

    def clear_frame(self):
        """Clear all widgets in the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_labeled_entry(self, master, label_text, is_password=False):
        """Create a labeled entry with left-aligned label and reduced width entry."""
        container = CTkFrame(master, fg_color="transparent")
        container.pack(fill="x", padx=50, pady=5)

        label = CTkLabel(container, text=label_text, anchor="w", text_color="#E5E7E9")  # Light gray text
        label.pack(side="left", padx=(0, 10))

        entry_kwargs = {
            "width": 200, 
            "show": "*", 
            "fg_color": "#2C3E50",  # Dark slate background for entries
            "border_color": "#34495E",  # Slightly lighter border
            "text_color": "#ECF0F1"  # Very light text color
        } if is_password else {
            "width": 200, 
            "fg_color": "#2C3E50", 
            "border_color": "#34495E", 
            "text_color": "#ECF0F1"
        }
        entry = CTkEntry(container, **entry_kwargs)
        entry.pack(side="right")

        return entry

    def show_login_screen(self):
        """Display the login screen with improved layout."""
        self.clear_frame()

        frame = CTkFrame(master=self.root, width=400, height=500, fg_color="#2C3E50")  # Dark slate frame
        frame.place(relx=0.5, rely=0.5, anchor="center")

        CTkLabel(master=frame, text="Login", font=("Arial", 24), text_color="#ECF0F1").pack(pady=20)

        username_entry = self.create_labeled_entry(frame, "Username")
        password_entry = self.create_labeled_entry(frame, "Password", is_password=True)

        def login_action():
            username = username_entry.get()
            password = password_entry.get()

            if not username or not password:
                messagebox.showerror("Input Error", "All fields are required.")
                return

            user = users_collection.find_one({"name": username, "password": password})

            if user:
                # Set the current user
                self.current_user = username
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.show_dashboard()
            else:
                messagebox.showerror("Login Error", "Invalid credentials.")

        CTkButton(
            master=frame, 
            text="Login", 
            command=login_action,
            fg_color="#E74C3C",  # Vibrant red for primary action
            hover_color="#C0392B"  # Darker red on hover
        ).pack(pady=20)

        CTkLabel(master=frame, text="Don't have an account? Sign up.", text_color="#BDC3C7").pack()
        
        CTkButton(
            master=frame, 
            text="Sign Up", 
            command=self.show_signup_screen,
            fg_color="#3498DB",  # Blue for secondary action
            hover_color="#2980B9"  # Darker blue on hover
        ).pack(pady=10)


    def show_signup_screen(self):
        """Display the signup screen with improved layout."""
        self.clear_frame()

        frame = CTkFrame(master=self.root, width=400, height=600)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        CTkLabel(master=frame, text="Sign Up", font=("Arial", 24)).pack(pady=20)

        username_entry = self.create_labeled_entry(frame, "Username")
        password_entry = self.create_labeled_entry(frame, "Password", is_password=True)

        dob_label = CTkLabel(master=frame, text="Date of Birth")
        dob_label.pack(pady=5)

        dob_entry = CTkEntry(master=frame, width=200, state="readonly")
        dob_entry.pack(pady=5)

        cal = Calendar(frame, selectmode="day", date_pattern="y-mm-dd")
        cal.pack(pady=10)

        def select_date():
            dob_entry.configure(state="normal")
            dob_entry.delete(0, "end")
            dob_entry.insert(0, cal.get_date())
            dob_entry.configure(state="readonly")

        CTkButton(master=frame, text="Select Date", command=select_date).pack(pady=10)

        def signup_action():
            username = username_entry.get()
            password = password_entry.get()
            dob = dob_entry.get()

            if not username or not password or not dob:
                messagebox.showerror("Input Error", "All fields are required.")
                return

            document = {"name": username, "password": password, "dob": dob}
            users_collection.insert_one(document)

            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_screen()

        CTkButton(master=frame, text="Sign Up", command=signup_action).pack(pady=10)
        CTkButton(master=frame, text="Back to Login", command=self.show_login_screen).pack(pady=10)


    def show_dashboard(self):
        """Display the dashboard after login."""
        self.clear_frame()

        # Main content frame with very dark background
        content_frame = CTkFrame(self.root, fg_color="#1C2833")
        content_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Show the home screen directly
        self.show_home(content_frame)

    def show_home(self, frame):
        """Redesigned home screen with modern, clean layout and integrated navigation."""
        # Clear existing widgets
        for widget in frame.winfo_children():
            widget.destroy()

        # Main container
        main_container = CTkFrame(frame, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # Welcome section
        welcome_frame = CTkFrame(main_container, fg_color="#2C3E50", corner_radius=15)
        welcome_frame.pack(fill="x", pady=10)

        CTkLabel(
            welcome_frame, 
            text="Welcome to Blood Bank Management System", 
            font=("Arial", 24, "bold"), 
            text_color="#ECF0F1"
        ).pack(pady=20)

        if self.current_user:
            CTkLabel(
                welcome_frame, 
                text=f"Logged in as: {self.current_user}", 
                font=("Arial", 16), 
                text_color="#BDC3C7"
            ).pack(pady=10)

        # Quick Stats Section
        stats_frame = CTkFrame(main_container, fg_color="#34495E", corner_radius=15)
        stats_frame.pack(fill="x", pady=10)

        # Calculate stats
        total_donors = donors_collection.count_documents({})
        total_donations = donations_collection.count_documents({})

        stats = [
            ("Total Donors", total_donors),
            ("Total Blood Donations", total_donations)
        ]

        # Create stat labels
        for label, value in stats:
            stat_container = CTkFrame(stats_frame, fg_color="transparent")
            stat_container.pack(pady=10, padx=20, fill="x")
            
            CTkLabel(stat_container, text=label, font=("Arial", 16), text_color="#ECF0F1").pack(side="left")
            CTkLabel(stat_container, text=str(value), font=("Arial", 16, "bold"), text_color="#E74C3C").pack(side="right")

        # Navigation Buttons Section
        nav_frame = CTkFrame(main_container, fg_color="transparent")
        nav_frame.pack(fill="x", pady=10)

        # Navigation buttons
        nav_buttons = [
            ("Donor", "#3498DB", lambda: self.show_donor_section(frame)),
            ("Blood Donations", "#2ECC71", lambda: self.show_blood_donations_section(frame)),
            ("Blood Bank", "#E74C3C", lambda: self.show_blood_bank_window(frame))
        ]

        for text, color, command in nav_buttons:
            CTkButton(
                nav_frame, 
                text=text, 
                command=command, 
                width=150, 
                height=50,
                fg_color=color,
                hover_color=color.replace(")", ", 0.7)"),
                font=("Arial", 16)
                ).pack(side="left", expand=True, padx=5, pady=10)

        # Logout Button
        logout_button = CTkButton(
            main_container, 
            text="Logout", 
            command=self.show_login_screen,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=("Arial", 16),
            width=200,
            height=50
        )
        logout_button.pack(pady=20)

    def create_table(self, parent, columns, data):
        """Create and populate a table with given columns and data."""
        table_frame = CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Custom style for dark mode treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Treeview", 
            background="#2C3E50", 
            foreground="#ECF0F1", 
            fieldbackground="#2C3E50"
        )
        style.map(
            "Custom.Treeview", 
            background=[('selected', '#E74C3C')]
        )

        # Scrollbar for the treeview
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            height=10, 
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
        )
        tree.pack(fill="both", expand=True)

        # Configure scrollbar
        scrollbar.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col, anchor="center")
            tree.column(col, anchor="center", width=120)

        for row in data:
            tree.insert("", "end", values=row)

        return tree

    def show_donor_section(self, frame):
        """Display the Donor section with entry form and table."""
        # Clear any existing widgets in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Entry Frame with dark slate background
        entry_frame = CTkFrame(frame, fg_color="#2C3E50", corner_radius=10)
        entry_frame.pack(fill="x", padx=10, pady=10)

        CTkLabel(entry_frame, text="Add Donor", font=("Arial", 16), text_color="#ECF0F1").pack(pady=10)

        # Create entry fields
        entries = {}
        
        # Name Entry
        name_container = CTkFrame(entry_frame, fg_color="transparent")
        name_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(name_container, text="Name", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        name_entry = CTkEntry(
            name_container, 
            width=200, 
            fg_color="#34495E", 
            border_color="#2C3E50", 
            text_color="#ECF0F1"
        )
        name_entry.pack(side="right")
        entries['name'] = name_entry

        # Age Entry
        age_container = CTkFrame(entry_frame, fg_color="transparent")
        age_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(age_container, text="Age", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        age_entry = CTkEntry(
            age_container, 
            width=200, 
            fg_color="#34495E", 
            border_color="#2C3E50", 
            text_color="#ECF0F1"
        )
        age_entry.pack(side="right")
        entries['age'] = age_entry

        # Gender Radio Buttons
        gender_frame = CTkFrame(entry_frame, fg_color="transparent")
        gender_frame.pack(fill="x", padx=50, pady=5)
        CTkLabel(gender_frame, text="Gender", text_color="#E5E7E9").pack(side="left", padx=(0, 10))

        gender_var = StringVar(value="prefer_not_to_say")
        gender_radio_frame = CTkFrame(gender_frame, fg_color="transparent")
        gender_radio_frame.pack(side="right")

        male_radio = CTkRadioButton(gender_radio_frame, text="Male", variable=gender_var, value="male")
        female_radio = CTkRadioButton(gender_radio_frame, text="Female", variable=gender_var, value="female")
        prefer_not_radio = CTkRadioButton(gender_radio_frame, text="Prefer Not to Say", variable=gender_var, value="prefer_not_to_say")
        
        male_radio.pack(side="left", padx=5)
        female_radio.pack(side="left", padx=5)
        prefer_not_radio.pack(side="left", padx=5)

        # Blood Group Dropdown
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group_container = CTkFrame(entry_frame, fg_color="transparent")
        blood_group_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(blood_group_container, text="Blood Group", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        
        blood_group_var = StringVar(value=blood_groups[0])
        blood_group_dropdown = CTkOptionMenu(
            blood_group_container, 
            values=blood_groups, 
            variable=blood_group_var,
            fg_color="#34495E",
            text_color="#ECF0F1"
        )
        blood_group_dropdown.pack(side="right")

        def add_donor():
            donor_data = {
                'name': name_entry.get(),
                'age': age_entry.get(),
                'gender': gender_var.get(),
                'blood_group': blood_group_var.get()
            }

            # Validate input
            for key, value in donor_data.items():
                if not value:
                    messagebox.showerror("Error", f"{key.replace('_', ' ').title()} is required")
                    return

            # Insert donor data
            donors_collection.insert_one(donor_data)
            
            # Show success message
            messagebox.showinfo("Success", "Donor added successfully!")
            
            # Refresh the entire donor section
            self.show_donor_section(frame)

        # Add Donor button with red accent
        CTkButton(
            entry_frame, 
            text="Add Donor", 
            command=add_donor,
            fg_color="#E74C3C",  # Vibrant red
            hover_color="#C0392B"  # Darker red on hover
        ).pack(pady=10)

        # Table Label
        CTkLabel(frame, text="Donor List", font=("Arial", 16), text_color="#ECF0F1").pack(pady=10)
        
        # Columns for the table
        columns = ["Name", "Age", "Gender", "Blood Group"]
        
        # Fetch donors from database
        donor_data = list(donors_collection.find({}, {"_id": 0}))
        donor_rows = [[d.get(col.lower().replace(" ", "_"), "") for col in columns] for d in donor_data]
        
        # Create table with custom styling
        self.create_table(frame, columns, donor_rows)
        back_frame = CTkFrame(frame, fg_color="transparent")
        back_frame.pack(fill="x", padx=10, pady=5, anchor="w")
        back_button = CTkButton(
            back_frame, 
            text="← Back to Home", 
            command=lambda: self.show_home(frame),
            fg_color="#34495E",
            hover_color="#2C3E50",
            font=("Arial", 12)
        )
        back_button.pack(side="left", padx=10)


    def show_blood_donations_section(self, frame):
        """Display the Blood Donations section with entry form and table."""
        # Clear any existing widgets in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Entry Frame with dark slate background
        entry_frame = CTkFrame(frame, fg_color="#2C3E50", corner_radius=10)
        entry_frame.pack(fill="x", padx=10, pady=10)

        CTkLabel(entry_frame, text="Add Blood Donation", font=("Arial", 16), text_color="#ECF0F1").pack(pady=10)

        # Blood Groups
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        # Name Entry
        name_container = CTkFrame(entry_frame, fg_color="transparent")
        name_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(name_container, text="Name", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        name_entry = CTkEntry(
            name_container, 
            width=200, 
            fg_color="#34495E",  
            border_color="#2C3E50", 
            text_color="#ECF0F1"
    )
        name_entry.pack(side="right")

        # Age Entry
        age_container = CTkFrame(entry_frame, fg_color="transparent")
        age_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(age_container, text="Age", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        age_entry = CTkEntry(
            age_container, 
            width=200, 
            fg_color="#34495E", 
            border_color="#2C3E50", 
            text_color="#ECF0F1"
        )
        age_entry.pack(side="right")


        units_container = CTkFrame(entry_frame, fg_color="transparent")
        units_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(units_container, text="Units", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        units_entry = CTkEntry(
            units_container, 
            width=200, 
            fg_color="#34495E", 
            border_color="#2C3E50", 
            text_color="#ECF0F1"
        )
        units_entry.pack(side="right")




        # Gender Radio Buttons
        gender_frame = CTkFrame(entry_frame, fg_color="transparent")
        gender_frame.pack(fill="x", padx=50, pady=5)
        CTkLabel(gender_frame, text="Gender", text_color="#E5E7E9").pack(side="left", padx=(0, 10))

        gender_var = StringVar(value="prefer_not_to_say")
        gender_radio_frame = CTkFrame(gender_frame, fg_color="transparent")
        gender_radio_frame.pack(side="right")

        male_radio = CTkRadioButton(gender_radio_frame, text="Male", variable=gender_var, value="male")
        female_radio = CTkRadioButton(gender_radio_frame, text="Female", variable=gender_var, value="female")
        prefer_not_radio = CTkRadioButton(gender_radio_frame, text="Prefer Not to Say", variable=gender_var, value="prefer_not_to_say")
        
        male_radio.pack(side="left", padx=5)
        female_radio.pack(side="left", padx=5)
        prefer_not_radio.pack(side="left", padx=5)

        # Blood Group Dropdown
        blood_group_container = CTkFrame(entry_frame, fg_color="transparent")
        blood_group_container.pack(fill="x", padx=50, pady=5)
        CTkLabel(blood_group_container, text="Blood Group", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
        
        blood_group_var = StringVar(value=blood_groups[0])
        blood_group_dropdown = CTkOptionMenu(
            blood_group_container, 
            values=blood_groups, 
            variable=blood_group_var,
            fg_color="#34495E",
            text_color="#ECF0F1"
        )
        blood_group_dropdown.pack(side="right")

       

        def add_donation():
            donation_data = {
                'name': name_entry.get(),
                'age': age_entry.get(),
                'gender': gender_var.get(),
                'blood_group': blood_group_var.get(),
                'units': units_entry.get(),
                'date': datetime.now().strftime("%Y-%m-%d")
            }

            # Validate input
            # for key, value in donation_data.items():
            #     if not value and key != 'date':
            #         messagebox.showerror("Error", f"{key.replace('_', ' ').title()} is required")
            #         return

            try:
            # Ensure units are a valid integer
                units_str = units_entry.get()
                try:
                    units = int(units_str)  # Try to convert the units to an integer
                except ValueError:
                    raise ValueError(f"Invalid units entry: '{units_str}' is not a valid number.")

                # Insert donation data
                donations_collection.insert_one(donation_data)

                # Update blood bank inventory
                inventory_collection.find_one_and_update(
                    {"blood_group": donation_data['blood_group']},
                    {"$inc": {"amount": units}},
                    upsert=True,
                    return_document=True
                )

                # Show success message
                messagebox.showinfo("Success", "Blood Donation recorded successfully!")

                # Refresh the entire blood donations section
                self.show_blood_donations_section(frame)


            except ValueError as ve:
                # Catch invalid value error and show appropriate message
                messagebox.showerror("Input Error", f"Error: {str(ve)}")

            except Exception as e:
                # General error handling
                messagebox.showerror(" caught Error", f"Failed to record donation: {str(e)}")


        # Record Donation button with green accent
        CTkButton(
            entry_frame, 
            text="Record Donation", 
            command=add_donation,
            fg_color="#2ECC71",  # Vibrant green
            hover_color="#27AE60"  # Darker green on hover
        ).pack(pady=10)

        # Table Label
        CTkLabel(frame, text="Blood Donations", font=("Arial", 16), text_color="#ECF0F1").pack(pady=10)
        
        # Columns for the table
        columns = ["Name", "Age", "Gender", "Blood Group","Units", "Date"]
        
        # Fetch donations from database
        donation_data = list(donations_collection.find({}, {"_id": 0}))
        donation_rows = [[d.get(col.lower().replace(" ", "_"), "") for col in columns] for d in donation_data]
        
        # Create table with custom styling
        self.create_table(frame, columns, donation_rows)
        back_frame = CTkFrame(frame, fg_color="transparent")
        back_frame.pack(fill="x", padx=10, pady=5, anchor="w")

        back_button = CTkButton(
            back_frame, 
            text="← Back to Home", 
            command=lambda: self.show_home(frame),
            fg_color="#34495E",
            hover_color="#2C3E50",
            font=("Arial", 12)
        )
        back_button.pack(side="left", padx=10)


    def show_blood_bank_window(self,frame):
        for widget in frame.winfo_children():
            widget.destroy()

        # Entry Frame with dark slate background
        inventory_frame = CTkFrame(frame, fg_color="#2C3E50", corner_radius=10)
        inventory_frame.pack(fill="x", padx=10, pady=10)

        # Blood Groups
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

      

        CTkLabel(
            inventory_frame, 
            text="Blood Bank Inventory", 
            font=("Arial", 24, "bold"), 
            text_color="#ECF0F1"
        ).pack(pady=20)

        # Create grid for blood groups
        grid_frame = CTkFrame(inventory_frame, fg_color="transparent")
        grid_frame.pack(expand=True, fill="both", padx=20, pady=10)

        for i, blood_group in enumerate(blood_groups):
            # Get current inventory for this blood group
            inventory_count = inventory_collection.find_one({"blood_group": blood_group})
            count = inventory_count['amount'] if inventory_count else 0

            group_frame = CTkFrame(grid_frame, fg_color="#34495E")
            group_frame.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="nsew")

            CTkLabel(group_frame, text=blood_group, font=("Arial", 16), text_color="#ECF0F1").pack(pady=5)
            amount_label = CTkLabel(group_frame, text=f"{count} Units", font=("Arial", 14), text_color="#E74C3C")
            amount_label.pack(pady=5)

            def create_transaction_window():
                transaction_window = CTkToplevel(self.root)
                transaction_window.title("Blood Transaction")
                transaction_window.geometry("400x600")  # Increased height to accommodate new dropdown
                transaction_window.configure(fg_color="#1C2833")
                
                # Make the window transient to the main window
                transaction_window.transient(self.root)
                transaction_window.grab_set() 

                # Transaction Type
                CTkLabel(transaction_window, text="Transaction Type", font=("Arial", 16), text_color="#ECF0F1").pack(pady=10)
                transaction_var = StringVar(value="collect")
                collect_radio = CTkRadioButton(transaction_window, text="Collect", variable=transaction_var, value="collect")
                deposit_radio = CTkRadioButton(transaction_window, text="Deposit", variable=transaction_var, value="deposit")
                collect_radio.pack(pady=5)
                deposit_radio.pack(pady=5)

                # Blood Group Dropdown
                blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
                blood_group_frame = CTkFrame(transaction_window, fg_color="transparent")
                blood_group_frame.pack(fill="x", padx=50, pady=5)
                CTkLabel(blood_group_frame, text="Blood Group", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
                blood_group_var = StringVar(value=blood_groups[0])
                blood_group_dropdown = CTkOptionMenu(
                    blood_group_frame, 
                    values=blood_groups, 
                    variable=blood_group_var,
                    fg_color="#34495E",
                    button_color="#2C3E50",
                    text_color="#ECF0F1"
                )
                blood_group_dropdown.pack(side="right")

                # Customer/Hospital Name
                name_frame = CTkFrame(transaction_window, fg_color="transparent")
                name_frame.pack(fill="x", padx=50, pady=5)
                CTkLabel(name_frame, text="Name", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
                name_entry = CTkEntry(
                    name_frame, 
                    width=200, 
                    fg_color="#34495E", 
                    border_color="#2C3E50", 
                    text_color="#ECF0F1"
                )
                name_entry.pack(side="right")

                # Blood Amount
                amount_frame = CTkFrame(transaction_window, fg_color="transparent")
                amount_frame.pack(fill="x", padx=50, pady=5)
                CTkLabel(amount_frame, text="Amount (Units)", text_color="#E5E7E9").pack(side="left", padx=(0, 10))
                amount_entry = CTkEntry(
                    amount_frame, 
                    width=200, 
                    fg_color="#34495E", 
                    border_color="#2C3E50", 
                    text_color="#ECF0F1"
                )
                amount_entry.pack(side="right")

                def process_transaction():
                    # Implement transaction logic here
                    transaction_type = transaction_var.get()
                    blood_group = blood_group_var.get()
                    name = name_entry.get()
                    amount = amount_entry.get()
                    
                    # Validate inputs
                    if not name or not amount:
                        messagebox.showerror("Error", "All fields are required")
                        return
                    
                    try:
                        # Convert amount to integer
                        amount = int(amount)
                    except ValueError:
                        messagebox.showerror("Error", "Amount must be a number")
                        return
                    
                    # Retrieve current inventory for the specific blood group
                    current_inventory = inventory_collection.find_one({"blood_group": blood_group})
                    
                    if current_inventory is None:
                        messagebox.showerror("Error", f"No inventory found for {blood_group} blood group")
                        return
                    
                    current_amount = current_inventory.get('amount', 0)
                    
                    # Process transaction based on type
                    if transaction_type == "collect":
                        # Reduce inventory
                        if amount > current_amount:
                            messagebox.showerror("Error", f"Insufficient {blood_group} blood units")
                            return
                        new_amount = current_amount - amount
                    else:  # deposit
                        new_amount = current_amount + amount
                    
                    # Update inventory in MongoDB
                    inventory_collection.update_one(
                        {"blood_group": blood_group},
                        {"$set": {"amount": new_amount}}
                    )
                    
                    # Show success message
                    messagebox.showinfo("Success", f"{transaction_type.capitalize()} transaction processed for {blood_group}!")
                    transaction_window.destroy()
                    self.show_blood_bank_window(frame)

                CTkButton(
                    transaction_window, 
                    text="Process Transaction", 
                    command=process_transaction,
                    fg_color="#2ECC71",
                    hover_color="#27AE60"
                ).pack(pady=20)
                CTkButton(
                    transaction_window, 
                    text="Cancel", 
                    command=lambda: transaction_window.destroy(),
                    fg_color="#E74C3C",
                    hover_color="#C0392B"
                ).pack(pady=20)
            CTkButton(
                group_frame, 
                text="Collect/Borrow", 
                command=create_transaction_window,
                fg_color="#E74C3C",
                hover_color="#C0392B"
            ).pack(pady=5)

        # Configure grid layout
        for i in range(2):
            grid_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        back_frame = CTkFrame(frame, fg_color="transparent")
        back_frame.pack(fill="x", padx=10, pady=5, anchor="w")

        back_button = CTkButton(
            back_frame, 
            text="← Back to Home", 
            command=lambda: self.show_home(frame),
            fg_color="#34495E",
            hover_color="#2C3E50",
            font=("Arial", 12)
        )
        back_button.pack(padx=10)


root = CTk()
app = App(root)
root.mainloop()