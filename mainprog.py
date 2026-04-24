import csv
import os
from datetime import datetime
from collections import defaultdict

CSV_FILE = "budget.csv"

# rensa skärmen
def clear_screen():
    input("Press Enter to continue...")
    os.system('cls')

# initiera CSV-fil om den inte finns
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Year', 'Month', 'Type', 'Description', 'Amount'])
        print(f"Created new budget file: {CSV_FILE}")

# lägg till budgetepost
def add_entry(year, month, entry_type, description, amount):
    try:
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([year, month, entry_type, description, amount])
        print(f"Added {entry_type}: {description} - {amount}")
    except Exception as e:
        print(f"Error adding entry: {e}")

# ladda alla poster från CSV
def load_all_entries():
    entries = defaultdict(lambda: {'wage': 0, 'costs': [], 'debts': []})
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header
            for row in reader:
                if len(row) >= 5:
                    year, month, entry_type, description, amount = row[0], row[1], row[2], row[3], row[4]
                    try:
                        amount = float(amount)
                        key = f"{year}-{month}"
                        if entry_type.lower() == 'wage':
                            entries[key]['wage'] += amount
                        elif entry_type.lower() == 'cost':
                            entries[key]['costs'].append((description, amount))
                        elif entry_type.lower() == 'debt':
                            entries[key]['debts'].append((description, amount))
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass
    return entries

# räkna totalkostnader
def calculate_total_costs(costs_list):
    return sum(amount for _, amount in costs_list)

# räkna totalskulder
def calculate_total_debts(debts_list):
    return sum(amount for _, amount in debts_list)

# visa månadlig budget
def display_monthly_budget(year, month, entries):
    key = f"{year}-{month}"
    if key not in entries:
        print(f"No budget data for {year}-{month:02d}")
        return
    
    data = entries[key]
    wage = data['wage']
    costs = data['costs']
    debts = data['debts']
    
    total_costs = calculate_total_costs(costs)
    total_debts = calculate_total_debts(debts)
    disposable = wage - total_costs - total_debts
    
    print(f"\n{'='*50}")
    print(f"Budget for {year}-{month:02d}")
    print(f"{'='*50}")
    print(f"Wage: {wage}")
    
    print(f"\nCosts:")
    for name, amount in costs:
        print(f"  {name}: {amount}")
    print(f"Total costs: {total_costs}")
    
    print(f"\nDebts:")
    for name, amount in debts:
        print(f"  {name}: {amount}")
    print(f"Total debts: {total_debts}")
    
    print(f"\nDisposable income: {disposable}")
    print(f"{'='*50}")

# visa årsbudget
def display_yearly_budget(year, entries):
    yearly_data = {'wage': 0, 'costs': 0, 'debts': 0, 'months': []}
    
    for key in sorted(entries.keys()):
        if key.startswith(str(year)):
            data = entries[key]
            yearly_data['wage'] += data['wage']
            yearly_data['costs'] += calculate_total_costs(data['costs'])
            yearly_data['debts'] += calculate_total_debts(data['debts'])
            yearly_data['months'].append(key)
    
    if not yearly_data['months']:
        print(f"No budget data for year {year}")
        return
    
    disposable = yearly_data['wage'] - yearly_data['costs'] - yearly_data['debts']
    
    print(f"\n{'='*50}")
    print(f"Annual Budget for {year}")
    print(f"{'='*50}")
    print(f"Total Wage (all months): {yearly_data['wage']}")
    print(f"Total Costs (all months): {yearly_data['costs']}")
    print(f"Total Debts (all months): {yearly_data['debts']}")
    print(f"Total Disposable Income: {disposable}")
    print(f"Months with data: {', '.join(yearly_data['months'])}")
    print(f"{'='*50}")

# skapa ny månadlig budget
def create_new_budget():
    print("\n" + "="*50)
    print("CREATE NEW MONTHLY BUDGET")
    print("="*50)
    
    year = int(input("Enter year (e.g., 2026): "))
    month = int(input("Enter month (1-12): "))
    
    # add wage
    wage_description = input("Wage description (e.g., Salary): ")
    wage_amount = float(input("Wage amount: "))
    add_entry(year, month, "wage", wage_description, wage_amount)
    
    # add costs
    while True:
        add_more_costs = input("\nAdd a cost? (y/n): ").lower()
        if add_more_costs != 'y':
            break
        cost_description = input("Cost name (e.g., Rent): ")
        cost_amount = float(input("Cost amount: "))
        add_entry(year, month, "cost", cost_description, cost_amount)
    
    # add debts
    while True:
        add_more_debts = input("\nAdd a debt? (y/n): ").lower()
        if add_more_debts != 'y':
            break
        debt_description = input("Debt name (e.g., Loan): ")
        debt_amount = float(input("Debt amount: "))
        add_entry(year, month, "debt", debt_description, debt_amount)
    
    print(f"\nBudget for {year}-{month:02d} created successfully!")

# huvudloop
initialize_csv()

while True:
    print("\n" + "="*50)
    print("BUDGET PROGRAM - Single CSV File Management")
    print("="*50)
    print("1. Create new monthly budget")
    print("2. Add individual entry")
    print("3. View monthly budget")
    print("4. View yearly budget")
    print("5. Exit")
    print("="*50)
    
    choice = input("Choose 1-5: ")
    
    if choice == "1":
        create_new_budget()
        clear_screen()
    
    elif choice == "2":
        entry_type_choice = input("\nAdd (1) Wage, (2) Cost, or (3) Debt? ")
        year = int(input("Enter year (e.g., 2026): "))
        month = int(input("Enter month (1-12): "))
        
        if entry_type_choice == "1":
            description = input("Description (e.g., Bonus): ")
            amount = float(input("Amount: "))
            add_entry(year, month, "wage", description, amount)
        elif entry_type_choice == "2":
            description = input("Cost name: ")
            amount = float(input("Amount: "))
            add_entry(year, month, "cost", description, amount)
        elif entry_type_choice == "3":
            description = input("Debt name: ")
            amount = float(input("Amount: "))
            add_entry(year, month, "debt", description, amount)
        clear_screen()
    
    elif choice == "3":
        entries = load_all_entries()
        year = int(input("Enter year: "))
        month = int(input("Enter month (1-12): "))
        display_monthly_budget(year, month, entries)
        clear_screen()
    
    elif choice == "4":
        entries = load_all_entries()
        year = int(input("Enter year: "))
        display_yearly_budget(year, entries)
        clear_screen()
    
    elif choice == "5":
        print("Goodbye!")
        break
    
    else:
        print("Invalid choice")
