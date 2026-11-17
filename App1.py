import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

con = sqlite3.connect("pharmacy.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS medicines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL,
    expiry TEXT
)
""")
con.commit()

def clear():
    name_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    expiry_entry.delete(0, tk.END)

def add():
    try:
        name = name_entry.get()
        qty = int(qty_entry.get())
        price = float(price_entry.get())
        expiry = expiry_entry.get()

        datetime.strptime(expiry, "%Y-%m-%d")

        if not name or qty < 0 or price < 0:
            raise ValueError

        cur.execute(
            "INSERT INTO medicines(name,quantity,price,expiry) VALUES(?,?,?,?)",
            (name, qty, price, expiry)
        )
        con.commit()
        view()
        clear()
        messagebox.showinfo("Success", "Medicine added successfully")

    except ValueError:
        messagebox.showerror("Error", "Enter valid details. Date: YYYY-MM-DD")

def view():
    for row in tree.get_children():
        tree.delete(row)

    cur.execute("SELECT * FROM medicines")
    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)

def delete():
    selected = tree.selection()

    if not selected:
        messagebox.showerror("Error", "Select a medicine")
        return

    item = tree.item(selected[0])
    mid = item["values"][0]

    cur.execute("DELETE FROM medicines WHERE id=?", (mid,))
    con.commit()
    view()
    messagebox.showinfo("Success", "Medicine deleted")

def update():
    selected = tree.selection()

    if not selected:
        messagebox.showerror("Error", "Select a medicine")
        return

    try:
        name = name_entry.get()
        qty = int(qty_entry.get())
        price = float(price_entry.get())
        expiry = expiry_entry.get()

        datetime.strptime(expiry, "%Y-%m-%d")

        if not name or qty < 0 or price < 0:
            raise ValueError

        mid = tree.item(selected[0])["values"][0]

        cur.execute("""
        UPDATE medicines
        SET name=?, quantity=?, price=?, expiry=?
        WHERE id=?
        """, (name, qty, price, expiry, mid))

        con.commit()
        view()
        clear()
        messagebox.showinfo("Success", "Medicine updated")

    except ValueError:
        messagebox.showerror("Error", "Enter valid details")

def select(event):
    selected = tree.selection()

    if selected:
        values = tree.item(selected[0])["values"]
        clear()

        name_entry.insert(0, values[1])
        qty_entry.insert(0, values[2])
        price_entry.insert(0, values[3])
        expiry_entry.insert(0, values[4])

def check_expiry():
    today = datetime.today().date()
    soon = today + timedelta(days=30)

    cur.execute("SELECT name, expiry FROM medicines")
    result = []

    for name, expiry in cur.fetchall():
        date = datetime.strptime(expiry, "%Y-%m-%d").date()

        if date < today:
            result.append(name + " - EXPIRED")

        elif date <= soon:
            result.append(name + " - EXPIRING SOON")

    if result:
        messagebox.showwarning("Expiry Alert", "\n".join(result))
    else:
        messagebox.showinfo("Expiry Alert", "No expiry alerts!")

def low_stock():
    cur.execute("SELECT name, quantity FROM medicines WHERE quantity <= 10")
    result = cur.fetchall()

    if result:
        messagebox.showwarning(
            "Low Stock",
            "\n".join([f"{name} - {qty} units" for name, qty in result])
        )
    else:
        messagebox.showinfo("Stock", "All medicines have sufficient stock")

# Main Window
root = tk.Tk()
root.title("Pharmacy Stock and Medicine Expiry Manager")
root.geometry("850x600")
root.config(bg="lightblue")

tk.Label(root, text="PHARMACY MANAGEMENT SYSTEM",
         font=("Arial", 20, "bold"), bg="lightblue").pack(pady=15)

frame = tk.Frame(root, bg="lightblue")
frame.pack()

tk.Label(frame, text="Medicine Name", bg="lightblue").grid(row=0, column=0, padx=10, pady=5)
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1)

tk.Label(frame, text="Quantity", bg="lightblue").grid(row=1, column=0, padx=10, pady=5)
qty_entry = tk.Entry(frame)
qty_entry.grid(row=1, column=1)

tk.Label(frame, text="Price", bg="lightblue").grid(row=2, column=0, padx=10, pady=5)
price_entry = tk.Entry(frame)
price_entry.grid(row=2, column=1)

tk.Label(frame, text="Expiry Date (YYYY-MM-DD)",
         bg="lightblue").grid(row=3, column=0, padx=10, pady=5)
expiry_entry = tk.Entry(frame)
expiry_entry.grid(row=3, column=1)

btn_frame = tk.Frame(root, bg="lightblue")
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Add", width=12, command=add).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Update", width=12, command=update).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Delete", width=12, command=delete).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="View Stock", width=12, command=view).grid(row=0, column=3, padx=5)
tk.Button(btn_frame, text="Check Expiry", width=12, command=check_expiry).grid(row=1, column=0, padx=5, pady=10)
tk.Button(btn_frame, text="Low Stock", width=12, command=low_stock).grid(row=1, column=1, padx=5, pady=10)
tk.Button(btn_frame, text="Clear", width=12, command=clear).grid(row=1, column=2, padx=5, pady=10)

columns = ("ID", "Name", "Quantity", "Price", "Expiry")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)

tree.pack(pady=15, fill="x", padx=15)
tree.bind("<<TreeviewSelect>>", select)

view()

root.mainloop()
con.close()
