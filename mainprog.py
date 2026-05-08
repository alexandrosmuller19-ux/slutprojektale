import os
from budget_manager import BudgetManager

# rensa skärmen
def clear_screen():
    input("Press Enter to continue...")
    os.system('cls')

# Initialize budget manager
budget = BudgetManager("budget.csv")

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
        budget.create_new_budget()
        clear_screen()
    
    elif choice == "2":
        entry_type_choice = input("\nAdd (1) Wage, (2) Cost, or (3) Debt? ")
        year = int(input("Enter year (e.g., 2026): "))
        month = int(input("Enter month (1-12): "))
        
        if entry_type_choice == "1":
            description = input("Description (e.g., Bonus): ")
            amount = float(input("Amount: "))
            budget.add_entry(year, month, "wage", description, amount)
        elif entry_type_choice == "2":
            description = input("Cost name: ")
            amount = float(input("Amount: "))
            budget.add_entry(year, month, "cost", description, amount)
        elif entry_type_choice == "3":
            description = input("Debt name: ")
            amount = float(input("Amount: "))
            budget.add_entry(year, month, "debt", description, amount)
        clear_screen()
    
    elif choice == "3":
        entries = budget.load_all_entries()
        year = int(input("Enter year: "))
        month = int(input("Enter month (1-12): "))
        budget.display_monthly_budget(year, month, entries)
        clear_screen()
    
    elif choice == "4":
        entries = budget.load_all_entries()
        year = int(input("Enter year: "))
        budget.display_yearly_budget(year, entries)
        clear_screen()
    
    elif choice == "5":
        print("Goodbye!")
        break
    
    else:
        print("Invalid choice")
