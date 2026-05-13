import tkinter as tk
from budget_ui import BudgetUI

# Launch the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetUI(root)
    root.mainloop()
