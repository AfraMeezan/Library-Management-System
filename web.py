import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
from datetime import datetime
import pandas as pd
import os

EMAIL = "aframeezan.rk@gmail.com"
APP_PASSWORD = "xady buae nsbc ualp"
RECEIVER = "aframeezan.rk@gmail.com"

def init_db():
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        url TEXT,
        price REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def fetch_price_amazon(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('span', {'id': 'productTitle'})
    price = soup.find('span', {'class': 'a-offscreen'})
    if title and price:
        name = title.get_text(strip=True)
        amount = float(price.get_text(strip=True).replace('₹', '').replace(',', ''))
        return name, amount
    return None, None

def insert_product(name, url, price):
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, url, price) VALUES (?, ?, ?)", (name, url, price))
    conn.commit()
    conn.close()

def save_to_csv(name, url, price):
    data = {
        'Name': [name],
        'URL': [url],
        'Price': [price],
        'Timestamp': [datetime.now()]
    }
    df = pd.DataFrame(data)
    try:
        file_exists = os.path.isfile("price_history.csv")
        df.to_csv("price_history.csv", mode='a', header=not file_exists, index=False)
        print(">>> Saved to CSV.")
    except Exception as e:
        print(">>> CSV save error:", e)

def send_email_alert(name, price, url):
    body = f"Price Drop Alert!\n\n{name}\nis now ₹{price}\n\nLink: {url}"
    msg = MIMEText(body)
    msg["Subject"] = "Price Drop Alert!"
    msg["From"] = EMAIL
    msg["To"] = RECEIVER
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(">>> Email sent.")
    except Exception as e:
        print(">>> Email error:", e)

def monitor(url, threshold):
    print(f"[{datetime.now()}] Checking price for {url}...")
    name, price = fetch_price_amazon(url)
    if name and price:
        print(f"Product: {name}\nPrice: ₹{price}")
        insert_product(name, url, price)
        save_to_csv(name, url, price)
        if price < threshold:
            print(">>> Price dropped! Sending email...")
            send_email_alert(name, price, url)
    else:
        print("Failed to fetch data.")

def schedule_monitor(url, threshold):
    schedule.every(6).hours.do(monitor, url, threshold)
    monitor(url, threshold)  # Run immediately once
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_monitoring():
    url = url_entry.get().strip()
    threshold_str = threshold_entry.get().strip()
    if not url or not threshold_str:
        messagebox.showwarning("Input Error", "Please enter both URL and threshold.")
        return
    try:
        threshold = float(threshold_str)
    except ValueError:
        messagebox.showwarning("Input Error", "Threshold must be a number.")
        return
    messagebox.showinfo("Started", "Price monitor started in background.")
    threading.Thread(target=schedule_monitor, args=(url, threshold), daemon=True).start()


init_db()
root = tk.Tk()
root.title("Price Monitor")
root.geometry("400x250")

tk.Label(root, text="Product URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text="Threshold Price (₹):").pack(pady=5)
threshold_entry = tk.Entry(root, width=20)
threshold_entry.pack()

tk.Button(root, text="Start Monitoring", command=start_monitoring, bg="green", fg="white").pack(pady=20)

root.mainloop()
