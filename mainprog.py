import os

#sparar lön, kostnader och skulder
wage = 0
costs = []
debts = []

#huvudloop för programmet
while True:
    print("\nBudget Program")
    print("1. Add wage")
    print("2. Add cost")
    print("3. Add debt")
    print("4. Show budget")
    print("5. Exit")
    
    #användarens val
    choice = input("Pick 1-5: ")
    
    #om användaren väljer 1, ange lön
    if choice == "1":
        wage = float(input("Enter wage: "))
        print("Wage set to", wage)
    
    #om användaren väljer 2, lägg till kostnad
    elif choice == "2":
        cost_name = input("Cost name: ")
        cost_amount = float(input("Cost amount: "))
        costs.append((cost_name, cost_amount))
        print("Added", cost_name)
    
    #om användaren väljer 3, lägg till skuld
    elif choice == "3":
        debt_name = input("Debt name: ")
        debt_amount = float(input("Debt amount: "))
        debts.append((debt_name, debt_amount))
        print("Added", debt_name)
    
    #om användaren väljer 4, visa budgetöversikt
    elif choice == "4":
        print("\nBudget")
        print("Wage:", wage)
        
        #räkna ihop alla kostnader
        total_costs = 0
        print("\nCosts:")
        for name, amount in costs:
            print(name, ":", amount)
            total_costs = total_costs + amount
        print("Total costs:", total_costs)
        
        #räkna ihop alla skulder
        total_debts = 0
        print("\nDebts:")
        for name, amount in debts:
            print(name, ":", amount)
            total_debts = total_debts + amount
        print("Total debts:", total_debts)
        
        #beräkna disponibelt inkomst
        disposable = wage - total_costs - total_debts
        print("\nDisposable income:", disposable)
    
    #om användaren väljer 5, avsluta programmet
    elif choice == "5":
        print("Bye!")
        break
    
    #om användaren skriver något ogiltigt
    else:
        print("Invalid choice")
