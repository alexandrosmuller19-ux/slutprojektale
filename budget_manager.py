import csv
import os
from collections import defaultdict


class BudgetManager:
    #Manages budget entries and calculations using CSV file.
    
    def __init__(self, csv_file="budget.csv"):
        self.csv_file = csv_file
        self.initialize_csv()
    
    def initialize_csv(self):
        #Initialize CSV file if it doesn't exist.
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Year', 'Month', 'Type', 'Description', 'Amount'])
            print(f"Created new budget file: {self.csv_file}")
    
    def add_entry(self, year, month, entry_type, description, amount):
        #Add a single budget entry to CSV.
        try:
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([year, month, entry_type, description, amount])
            print(f"Added {entry_type}: {description} - {amount}")
        except Exception as e:
            print(f"Error adding entry: {e}")
    
    def load_all_entries(self):
        #Load all entries from CSV file.
        entries = defaultdict(lambda: {'wage': 0, 'costs': [], 'debts': []})
        try:
            with open(self.csv_file, 'r') as csvfile:
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
    
    @staticmethod
    def calculate_total_costs(costs_list):
        #Calculate total costs from a list of cost tuples.
        return sum(amount for _, amount in costs_list)
    
    @staticmethod
    def calculate_total_debts(debts_list):
        #Calculate total debts from a list of debt tuples.
        return sum(amount for _, amount in debts_list)
    
    def display_monthly_budget(self, year, month, entries):
        #Display budget for a specific month.
        key = f"{year}-{month}"
        if key not in entries:
            print(f"No budget data for {year}-{month:02d}")
            return
        
        data = entries[key]
        wage = data['wage']
        costs = data['costs']
        debts = data['debts']
        
        total_costs = self.calculate_total_costs(costs)
        total_debts = self.calculate_total_debts(debts)
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
    
    def display_yearly_budget(self, year, entries):
        #Display budget for a specific year.
        yearly_data = {'wage': 0, 'costs': 0, 'debts': 0, 'months': []}
        
        for key in sorted(entries.keys()):
            if key.startswith(str(year)):
                data = entries[key]
                yearly_data['wage'] += data['wage']
                yearly_data['costs'] += self.calculate_total_costs(data['costs'])
                yearly_data['debts'] += self.calculate_total_debts(data['debts'])
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
    
    def create_new_budget(self):
        #Create a new monthly budget with wage, costs, and debts.
        print("\n" + "="*50)
        print("CREATE NEW MONTHLY BUDGET")
        print("="*50)
        
        year = int(input("Enter year (e.g., 2026): "))
        month = int(input("Enter month (1-12): "))
        
        # add wage
        wage_description = input("Wage description (e.g., Salary): ")
        wage_amount = float(input("Wage amount: "))
        self.add_entry(year, month, "wage", wage_description, wage_amount)
        
        # add costs
        while True:
            add_more_costs = input("\nAdd a cost? (y/n): ").lower()
            if add_more_costs != 'y':
                break
            cost_description = input("Cost name (e.g., Rent): ")
            cost_amount = float(input("Cost amount: "))
            self.add_entry(year, month, "cost", cost_description, cost_amount)
        
        # add debts
        while True:
            add_more_debts = input("\nAdd a debt? (y/n): ").lower()
            if add_more_debts != 'y':
                break
            debt_description = input("Debt name (e.g., Loan): ")
            debt_amount = float(input("Debt amount: "))
            self.add_entry(year, month, "debt", debt_description, debt_amount)
        
        print(f"\nBudget for {year}-{month:02d} created successfully!")
