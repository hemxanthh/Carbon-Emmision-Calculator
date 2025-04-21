import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Define emission factors (kg CO2 per unit)
EMISSION_FACTORS = {
    'transport': {
        'Car': 0.21,       # per km
        'Bus': 0.11,
        'Train': 0.05,
        'Flight': 0.285
    },
    'electricity': {
        'Electricity': 0.475       # per kWh
    },
    'food': {
        'Beef': 27.0,      # per kg
        'Chicken': 6.9,
        'Vegetables': 2.0
    }
}

# Initialize database
def initialize_database():
    conn = sqlite3.connect('carbon_emissions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            activity TEXT NOT NULL,
            amount REAL NOT NULL,
            emission REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Calculate emission
def calculate_emission(category, activity, amount):
    try:
        factor = EMISSION_FACTORS[category][activity]
        return amount * factor
    except KeyError:
        return None

# Log emission to database
def log_emission(category, activity, amount, emission):
    conn = sqlite3.connect('carbon_emissions.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emissions (category, activity, amount, emission)
        VALUES (?, ?, ?, ?)
    ''', (category, activity, amount, emission))
    conn.commit()
    conn.close()

# Retrieve total emissions
def get_total_emissions():
    conn = sqlite3.connect('carbon_emissions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(emission) FROM emissions GROUP BY category')
    results = cursor.fetchall()
    conn.close()
    return results

# GUI Application
class CarbonCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Carbon Emission Calculator")
        self.root.geometry("400x400")
        self.create_widgets()

    def create_widgets(self):
        # Category Selection
        ttk.Label(self.root, text="Select Category:").pack(pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.root, textvariable=self.category_var, state="readonly")
        self.category_combo['values'] = ('transport', 'electricity', 'food')
        self.category_combo.pack(pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.update_activity_options)

        # Activity Selection
        ttk.Label(self.root, text="Select Activity:").pack(pady=5)
        self.activity_var = tk.StringVar()
        self.activity_combo = ttk.Combobox(self.root, textvariable=self.activity_var, state="readonly")
        self.activity_combo.pack(pady=5)

        # Amount Entry
        ttk.Label(self.root, text="Enter Amount:").pack(pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.pack(pady=5)

        # Calculate Button
        ttk.Button(self.root, text="Calculate Emission", command=self.calculate_and_log).pack(pady=10)

        # Result Display
        self.result_label = ttk.Label(self.root, text="")
        self.result_label.pack(pady=5)

        # View Totals Button
        ttk.Button(self.root, text="View Total Emissions", command=self.display_totals).pack(pady=10)

    def update_activity_options(self, event):
        category = self.category_var.get()
        activities = list(EMISSION_FACTORS.get(category, {}).keys())
        self.activity_combo['values'] = activities
        if activities:
            self.activity_combo.current(0)

    def calculate_and_log(self):
        category = self.category_var.get()
        activity = self.activity_var.get()
        amount_str = self.amount_entry.get()

        if not category or not activity or not amount_str:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for amount.")
            return

        emission = calculate_emission(category, activity, amount)
        if emission is None:
            messagebox.showerror("Calculation Error", "Invalid category or activity selected.")
            return

        log_emission(category, activity, amount, emission)
        self.result_label.config(text=f"Emission: {emission:.2f} kg CO₂")

    def display_totals(self):
        totals = get_total_emissions()
        if not totals:
            messagebox.showinfo("Total Emissions", "No data available.")
            return

        total_text = "Total Emissions by Category:\n"
        for category, total in totals:
            total_text += f"{category.capitalize()}: {total:.2f} kg CO₂\n"

        messagebox.showinfo("Total Emissions", total_text)

# Main Execution
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = CarbonCalculatorApp(root)
    root.mainloop()
