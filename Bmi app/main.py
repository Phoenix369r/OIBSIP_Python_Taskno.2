import tkinter as tk
from tkinter import ttk, messagebox, Canvas, PhotoImage
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

DATA_FILE = "bmi_data.csv"

# Utility to ensure CSV file has correct headers
def ensure_data_file():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        df = pd.DataFrame(columns=["Name", "Weight", "Height", "BMI", "Category", "Date"])
        df.to_csv(DATA_FILE, index=False)

# BMI calculation logic
def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        return round(bmi, 2), "Underweight", "blue"
    elif 18.5 <= bmi < 25:
        return round(bmi, 2), "Normal", "green"
    elif 25 <= bmi < 30:
        return round(bmi, 2), "Overweight", "orange"
    else:
        return round(bmi, 2), "Obese", "red"

class BMICalculatorApp:
    def __init__(self, root):
        ensure_data_file()

        self.root = root
        self.root.title("BMI Calculator")
        self.root.geometry("500x540")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=5)
        self.style.configure("TEntry", font=("Segoe UI", 11))

        self.create_widgets()

    def create_widgets(self):
        # Load image using Canvas
        try:
            canvas = Canvas(self.root, width=234, height=180, highlightthickness=0)
            self.logo_img = PhotoImage(file="img.png")
            canvas.create_image(117,90 , image=self.logo_img)
            canvas.pack(pady=(10, 0))
        except Exception as e:
            print("Canvas image error:", e)

        frame = ttk.LabelFrame(self.root, text="Enter Details", padding=20)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(frame, width=25)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=5)
        self.weight_entry = ttk.Entry(frame, width=25)
        self.weight_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Height (m):").grid(row=2, column=0, sticky="w", pady=5)
        self.height_entry = ttk.Entry(frame, width=25)
        self.height_entry.grid(row=2, column=1, pady=5)

        self.result_label = tk.Label(self.root, text="", font=("Segoe UI", 12, "bold"))
        self.result_label.pack(pady=10)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Calculate BMI", command=self.calculate_and_store).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View History", command=self.view_history).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Plot Trend", command=self.plot_trend).grid(row=0, column=2, padx=5)

        ttk.Button(self.root, text="🪑 Clear User History", command=self.clear_history).pack(pady=5)

    def calculate_and_store(self):
        ensure_data_file()
        try:
            name = self.name_entry.get().strip()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if not name:
                messagebox.showerror("Input Error", "Please enter your name.")
                return

            bmi, category, color = calculate_bmi(weight, height)
            self.result_label.config(text=f"BMI: {bmi} ({category})", fg=color)

            record = {
                "Name": name,
                "Weight": weight,
                "Height": height,
                "BMI": bmi,
                "Category": category,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df = pd.read_csv(DATA_FILE)
            new_row = pd.DataFrame([record])
            df = new_row if df.empty else pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for weight and height.")

    def view_history(self):
        ensure_data_file()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Enter your name to view history.")
            return

        df = pd.read_csv(DATA_FILE)
        user_data = df[df["Name"].str.lower() == name.lower()]
        if user_data.empty:
            messagebox.showinfo("No Data", "No history found for this user.")
            return

        hist_win = tk.Toplevel(self.root)
        hist_win.title(f"{name}'s BMI History")
        hist_win.geometry("500x300")

        tree = ttk.Treeview(hist_win, columns=("Date", "Weight", "Height", "BMI", "Category"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for _, row in user_data.iterrows():
            tree.insert("", "end", values=(row["Date"], row["Weight"], row["Height"], row["BMI"], row["Category"]))

        tree.pack(fill="both", expand=True)

    def plot_trend(self):
        ensure_data_file()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Enter your name to plot trend.")
            return

        df = pd.read_csv(DATA_FILE)
        user_data = df[df["Name"].str.lower() == name.lower()]
        if user_data.empty:
            messagebox.showinfo("No Data", "No data to plot.")
            return

        user_data["Date"] = pd.to_datetime(user_data["Date"])
        user_data = user_data.sort_values("Date")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(user_data["Date"], user_data["BMI"], marker='o', linestyle='-', color='purple')
        ax.set_title(f"BMI Trend for {name}")
        ax.set_ylabel("BMI")
        ax.set_xlabel("Date")
        ax.grid(True)

        plot_win = tk.Toplevel(self.root)
        plot_win.title("BMI Trend")
        canvas = FigureCanvasTkAgg(fig, master=plot_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def clear_history(self):
        ensure_data_file()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Enter the name to clear history.")
            return

        df = pd.read_csv(DATA_FILE)
        if df[df["Name"].str.lower() == name.lower()].empty:
            messagebox.showinfo("No Data", f"No history found for {name}.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete all history for '{name}'?")
        if confirm:
            df = df[df["Name"].str.lower() != name.lower()]
            df.to_csv(DATA_FILE, index=False)
            messagebox.showinfo("Deleted", f"History for '{name}' has been cleared.")
            self.result_label.config(text="")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
