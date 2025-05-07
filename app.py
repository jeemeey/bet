import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
import zipfile


def run_simulation(rounds, initial_bet, high_risk):
    starting_balance = 1000
    balance = starting_balance
    max_balance = starting_balance
    anchor_peak = starting_balance
    in_dynamic_phase = False
    dynamic_peak = None

    quick_cashout_base = 1.7
    bet_base = initial_bet

    current_quick_cashout = quick_cashout_base
    current_bet = bet_base
    aggressive_level = 0

    dynamic_bet = 50
    dynamic_cashout_high = 3.5
    dynamic_cashout_low = 1.7
    use_high_cashout = True

    balance_history = [balance]
    log_data = []

    for i in range(1, rounds + 1):
        if i % 7 == 0:
            num_players = random.randint(10, 30)
        else:
            num_players = random.randint(50, 100)

        if num_players >= 80:
            crash_point = round(random.uniform(1.0, 2.0), 2)
        elif 50 <= num_players < 80:
            crash_point = round(random.uniform(1.0, 10.0), 2)
        else:
            crash_point = round(random.uniform(1.0, 25.0), 2)

        if not in_dynamic_phase:
            if balance < 1200:
                cashout_point = current_quick_cashout
                bet = current_bet
            elif balance < 1500:
                cashout_point = current_quick_cashout
                bet = current_bet
                if balance >= anchor_peak + 200:
                    anchor_peak = balance
                    aggressive_level += 1
                    current_quick_cashout += 0.5
                    if aggressive_level % 2 == 0:
                        current_bet += 5
            else:
                in_dynamic_phase = True
                dynamic_peak = balance
                use_high_cashout = dynamic_bet <= 50
                cashout_point = dynamic_cashout_high if use_high_cashout else dynamic_cashout_low
                bet = dynamic_bet
        else:
            cashout_point = dynamic_cashout_high if use_high_cashout else dynamic_cashout_low
            bet = dynamic_bet

            if balance >= dynamic_peak + 200:
                dynamic_peak = balance
                dynamic_bet += 10
                use_high_cashout = not use_high_cashout

            if balance <= dynamic_peak - 200:
                dynamic_peak = balance
                dynamic_bet = max(10, dynamic_bet - 10)
                use_high_cashout = not use_high_cashout

        if high_risk and i % 20 == 0:
            cashout_point = 10.0  # High-risk round

        balance_before = balance
        if cashout_point <= crash_point:
            win = bet * (cashout_point - 1)
            balance += win
            result = 'Win'
        else:
            balance -= bet
            result = 'Loss'

        balance_history.append(balance)

        log_data.append({
            'Round': i,
            'Balance Before': balance_before,
            'Bet': bet,
            'Cashout': cashout_point,
            'Result': result,
            'Balance After': balance
        })

        if balance > max_balance:
            max_balance = balance

    df = pd.DataFrame(log_data)
    df.to_excel("simulation_log.xlsx", index=False)
    df.to_csv("simulation_log.csv", index=False)

    with zipfile.ZipFile("simulation_logs.zip", "w") as zipf:
        zipf.write("simulation_log.xlsx")
        zipf.write("simulation_log.csv")

    return balance_history, df


def start_simulation():
    try:
        rounds = int(entry_rounds.get())
        initial_bet = float(entry_bet.get())
    except ValueError:
        messagebox.showerror("Error", "من فضلك أدخل أرقام صحيحة!")
        return

    high_risk_enabled = high_risk_var.get()

    balance_history, df = run_simulation(rounds, initial_bet, high_risk_enabled)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(balance_history)
    ax.set_title('Crash Simulator')
    ax.set_xlabel('Round')
    ax.set_ylabel('Balance')

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=2)

    messagebox.showinfo("تم الحفظ", "تم حفظ الملفات: simulation_log.xlsx, simulation_log.csv, simulation_logs.zip")


# إعداد نافذة Tkinter
window = tk.Tk()
window.title("Crash Simulator - JEMY Edition")

label_rounds = tk.Label(window, text="عدد الجولات:")
label_rounds.grid(row=0, column=0)
entry_rounds = tk.Entry(window)
entry_rounds.grid(row=0, column=1)

label_bet = tk.Label(window, text="قيمة الرهان:")
label_bet.grid(row=1, column=0)
entry_bet = tk.Entry(window)
entry_bet.grid(row=1, column=1)

high_risk_var = tk.BooleanVar()
high_risk_check = tk.Checkbutton(window, text="تفعيل High-Risk Mode", variable=high_risk_var)
high_risk_check.grid(row=2, column=0, columnspan=2)

start_button = tk.Button(window, text="تشغيل المحاكاة", command=start_simulation)
start_button.grid(row=3, column=0, columnspan=2)

window.mainloop()
