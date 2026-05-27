import csv
import os
from collections import defaultdict


class BudgetManager:
    # Hanterar budgetposter och beräkningar med en CSV-fil för beständig lagring
    
    def __init__(self, csv_file="budget.csv"):
        # Initierar budgethanteraren med en sökväg till CSV-filen
        self.csv_file = csv_file
        self.initialize_csv()
    
    def initialize_csv(self):
        # Skapar CSV-fil med rubriker om den inte redan finns
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Year', 'Month', 'Type', 'Description', 'Amount'])
            print(f"Created new budget file: {self.csv_file}")
    
    def add_entry(self, year, month, entry_type, description, amount):
        # Lägger till en enskild budgetpost i CSV-filen
        try:
            with open(self.csv_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([year, month, entry_type, description, amount])
            print(f"Added {entry_type}: {description} - {amount}")
        except Exception as e:
            print(f"Error adding entry: {e}")
    
    def get_all_raw_entries(self):
        # Hämtar alla poster som en rå lista av dicts för redigering och borttagning
        entries = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    entries.append(dict(row))
        except FileNotFoundError:
            pass
        return entries
    
    def delete_entry(self, row_index):
        # Tar bort en post via radindex (0-baserat, exklusive rubrikrad)
        try:
            entries = self.get_all_raw_entries()
            if 0 <= row_index < len(entries):
                # Ta bort den angivna posten
                entries.pop(row_index)
                # Skriv om hela CSV-filen med kvarvarande poster
                with open(self.csv_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Year', 'Month', 'Type', 'Description', 'Amount'])
                    for entry in entries:
                        writer.writerow([entry['Year'], entry['Month'], entry['Type'], 
                                       entry['Description'], entry['Amount']])
                print(f"Deleted entry at row {row_index}")
                return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
        return False
    
    def update_entry(self, row_index, year, month, entry_type, description, amount):
        # Uppdaterar en post via radindex med nya värden
        try:
            entries = self.get_all_raw_entries()
            if 0 <= row_index < len(entries):
                # Ersätt posten med uppdaterade värden
                entries[row_index] = {
                    'Year': year,
                    'Month': month,
                    'Type': entry_type,
                    'Description': description,
                    'Amount': amount
                }
                # Skriv om hela CSV-filen med uppdaterade poster
                with open(self.csv_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Year', 'Month', 'Type', 'Description', 'Amount'])
                    for entry in entries:
                        writer.writerow([entry['Year'], entry['Month'], entry['Type'], 
                                       entry['Description'], entry['Amount']])
                print(f"Updated entry at row {row_index}")
                return True
        except Exception as e:
            print(f"Error updating entry: {e}")
        return False
    
    def load_all_entries(self):
        # Läser in alla budgetposter från CSV-filen och organiserar dem per månad
        entries = defaultdict(lambda: {'wage': 0, 'costs': [], 'debts': []})
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Hoppa över rubrikraden
                for row in reader:
                    if len(row) >= 5:
                        year, month, entry_type, description, amount = row[0], row[1], row[2], row[3], row[4]
                        try:
                            amount = float(amount)
                            key = f"{year}-{month}"
                            # Kategoriserar poster efter typ: inkomst, utgifter eller skulder
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
        # Summerar alla utgifter från en lista av (beskrivning, belopp)-tupler
        return sum(amount for _, amount in costs_list)
    
    @staticmethod
    def calculate_total_debts(debts_list):
        # Summerar alla skulder från en lista av (beskrivning, belopp)-tupler
        return sum(amount for _, amount in debts_list)
    
    def display_monthly_budget(self, year, month, entries):
        # Visar budgetsammanfattning för en specifik månad med inkomst, utgifter och skulder
        key = f"{year}-{month}"
        if key not in entries:
            print(f"No budget data for {year}-{month:02d}")
            return
        
        data = entries[key]
        wage = data['wage']
        costs = data['costs']
        debts = data['debts']
        
        # Beräknar totalsummor för varje kategori
        total_costs = self.calculate_total_costs(costs)
        total_debts = self.calculate_total_debts(debts)
        # Beräknar kvarvarande pengar efter utgifter och skulder
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
        # Visar årlig budgetsammanfattning för alla månader under ett givet år
        yearly_data = {'wage': 0, 'costs': 0, 'debts': 0, 'months': []}
        
        # Sammanställer all månadsdata för det angivna året
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
        
        # Beräknar total disponibel inkomst för hela året
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
        # Skapar en ny månadsbudget med inkomst, utgifter och skulder
        print("\n" + "="*50)
        print("CREATE NEW MONTHLY BUDGET")
        print("="*50)
        
        # Hämtar år och månad från användarinmatning
        year = int(input("Enter year (e.g., 2026): "))
        month = int(input("Enter month (1-12): "))
        
        # Lägger till en inkomstpost för budgeten
        wage_description = input("Wage description (e.g., Salary): ")
        wage_amount = float(input("Wage amount: "))
        self.add_entry(year, month, "wage", wage_description, wage_amount)
        
        # Lägger till utgifter – användaren kan lägga till flera poster
        while True:
            add_more_costs = input("\nAdd a cost? (y/n): ").lower()
            if add_more_costs != 'y':
                break
            cost_description = input("Cost name (e.g., Rent): ")
            cost_amount = float(input("Cost amount: "))
            self.add_entry(year, month, "cost", cost_description, cost_amount)
        
        # Lägger till skulder – användaren kan lägga till flera poster
        while True:
            add_more_debts = input("\nAdd a debt? (y/n): ").lower()
            if add_more_debts != 'y':
                break
            debt_description = input("Debt name (e.g., Loan): ")
            debt_amount = float(input("Debt amount: "))
            self.add_entry(year, month, "debt", debt_description, debt_amount)
        
        # Bekräftar att budgeten har skapats
        print(f"\nBudget for {year}-{month:02d} created successfully!")