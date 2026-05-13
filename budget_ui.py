import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from budget_manager import BudgetManager
from datetime import datetime


class BudgetUI:
    """Professional Budget Manager GUI with modern design."""

    MONTH_NAMES = {
        1: "Januari", 2: "Februari", 3: "Mars", 4: "April", 5: "Maj", 6: "Juni",
        7: "Juli", 8: "Augusti", 9: "September", 10: "Oktober", 11: "November", 12: "December"
    }

    COLORS = {
        'primary':      '#1A56DB',
        'primary_dark': '#1344B7',
        'secondary':    '#0EA5E9',
        'accent':       '#06B6D4',
        'success':      '#059669',
        'success_bg':   '#ECFDF5',
        'danger':       '#DC2626',
        'danger_bg':    '#FEF2F2',
        'warning':      '#D97706',
        'warning_bg':   '#FFFBEB',
        'bg':           '#F8FAFC',
        'surface':      '#FFFFFF',
        'border':       '#E2E8F0',
        'border_focus': '#93C5FD',
        'text':         '#0F172A',
        'text_muted':   '#64748B',
        'text_light':   '#94A3B8',
        'sidebar_bg':   '#1E293B',
        'sidebar_text': '#CBD5E1',
    }

    FONTS = {
        'title':        ('Segoe UI', 22, 'bold'),
        'heading':      ('Segoe UI', 15, 'bold'),
        'subheading':   ('Segoe UI', 12, 'bold'),
        'body':         ('Segoe UI', 11),
        'body_bold':    ('Segoe UI', 11, 'bold'),
        'small':        ('Segoe UI', 10),
        'small_bold':   ('Segoe UI', 10, 'bold'),
        'mono':         ('Consolas', 11),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Budget Manager")
        self.root.geometry("1400x860")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.COLORS['bg'])

        self.budget = BudgetManager("budget.csv")

        self._setup_styles()
        self._build_layout()
        self.refresh_data()

    # ──────────────────────────────────────────────
    #  STYLES
    # ──────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')

        bg = self.COLORS['bg']
        surface = self.COLORS['surface']
        border = self.COLORS['border']
        text = self.COLORS['text']
        muted = self.COLORS['text_muted']

        s.configure('TFrame', background=bg)
        s.configure('Surface.TFrame', background=surface)
        s.configure('TLabel', background=bg, foreground=text, font=self.FONTS['body'])
        s.configure('Surface.TLabel', background=surface, foreground=text, font=self.FONTS['body'])
        s.configure('Muted.TLabel', background=surface, foreground=muted, font=self.FONTS['small'])

        s.configure('Vertical.TScrollbar',
                    troughcolor=bg, background=border, bordercolor=bg,
                    arrowcolor=muted, relief='flat', width=8)
        s.map('Vertical.TScrollbar', background=[('active', self.COLORS['text_light'])])

        s.configure('TCombobox', font=self.FONTS['body'], padding=(8, 6),
                    fieldbackground=surface, background=surface, foreground=text,
                    bordercolor=border, lightcolor=border, darkcolor=border)
        s.map('TCombobox', fieldbackground=[('readonly', surface)],
              bordercolor=[('focus', self.COLORS['border_focus'])])

        s.configure('Treeview',
                    background=surface, fieldbackground=surface, foreground=text,
                    font=self.FONTS['body'], rowheight=38, bordercolor=border)
        s.configure('Treeview.Heading',
                    background=self.COLORS['bg'], foreground=muted,
                    font=self.FONTS['small_bold'], relief='flat', padding=(10, 8))
        s.map('Treeview', background=[('selected', '#EFF6FF')],
              foreground=[('selected', self.COLORS['primary'])])

    # ──────────────────────────────────────────────
    #  LAYOUT SKELETON
    # ──────────────────────────────────────────────

    def _build_layout(self):
        # Top nav bar
        self._build_navbar()

        # Thin divider
        tk.Frame(self.root, bg=self.COLORS['border'], height=1).pack(fill=tk.X)

        # Scrollable main body
        body_outer = tk.Frame(self.root, bg=self.COLORS['bg'])
        body_outer.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(body_outer, bg=self.COLORS['bg'],
                                 highlightthickness=0, bd=0)
        _vsb = ttk.Scrollbar(body_outer, orient=tk.VERTICAL,
                              command=self._canvas.yview, style='Vertical.TScrollbar')
        self._canvas.configure(yscrollcommand=_vsb.set)

        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner frame that holds all cards / tables
        self._body = tk.Frame(self._canvas, bg=self.COLORS['bg'])
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._body, anchor='nw'
        )

        self._body.bind('<Configure>', self._on_body_resize)
        self._canvas.bind('<Configure>', self._on_canvas_resize)
        self._canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _on_body_resize(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    # ──────────────────────────────────────────────
    #  NAVBAR
    # ──────────────────────────────────────────────

    def _build_navbar(self):
        nav = tk.Frame(self.root, bg=self.COLORS['surface'], height=68)
        nav.pack(fill=tk.X, side=tk.TOP)
        nav.pack_propagate(False)

        inner = tk.Frame(nav, bg=self.COLORS['surface'])
        inner.pack(fill=tk.BOTH, expand=True, padx=36, pady=0)

        # Logo / title
        logo_wrap = tk.Frame(inner, bg=self.COLORS['surface'])
        logo_wrap.pack(side=tk.LEFT, fill=tk.Y)

        dot = tk.Label(logo_wrap, text='●', font=('Segoe UI', 14),
                       bg=self.COLORS['surface'], fg=self.COLORS['primary'])
        dot.pack(side=tk.LEFT, padx=(0, 8), pady=22)

        title = tk.Label(logo_wrap, text='Budget Manager', font=self.FONTS['heading'],
                         bg=self.COLORS['surface'], fg=self.COLORS['text'])
        title.pack(side=tk.LEFT, pady=22)

        # Buttons
        btn_wrap = tk.Frame(inner, bg=self.COLORS['surface'])
        btn_wrap.pack(side=tk.RIGHT, fill=tk.Y, pady=14)

        self._mk_btn(btn_wrap, '+ New Budget', self.COLORS['primary'],
                     self.open_create_budget_window, side=tk.LEFT, padx=(0, 10))
        self._mk_btn(btn_wrap, '+ Add Entry', self.COLORS['secondary'],
                     self.open_add_entry_window, side=tk.LEFT)

    # ──────────────────────────────────────────────
    #  HELPER: make a flat button with hover effect
    # ──────────────────────────────────────────────

    def _mk_btn(self, parent, text, bg_color, command,
                side=tk.LEFT, padx=0, pady=0, width=None):
        btn = tk.Button(parent, text=text, font=self.FONTS['body_bold'],
                        bg=bg_color, fg='#FFFFFF', activebackground=bg_color,
                        activeforeground='#FFFFFF', relief=tk.FLAT,
                        cursor='hand2', bd=0, padx=18, pady=9,
                        command=command)
        if width:
            btn.config(width=width)
        btn.pack(side=side, padx=padx, pady=pady)

        # Darken on hover
        def _darken(e, c=bg_color):
            r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            d = lambda v: max(0, int(v * 0.85))
            btn.config(bg=f'#{d(r):02x}{d(g):02x}{d(b):02x}')

        def _restore(e, c=bg_color):
            btn.config(bg=c)

        btn.bind('<Enter>', _darken)
        btn.bind('<Leave>', _restore)
        return btn

    # ──────────────────────────────────────────────
    #  REFRESH  (clears body and redraws everything)
    # ──────────────────────────────────────────────

    def refresh_data(self):
        for w in self._body.winfo_children():
            w.destroy()

        entries = self.budget.load_all_entries()

        if not entries:
            self._show_empty_state()
            return

        wrapper = tk.Frame(self._body, bg=self.COLORS['bg'])
        wrapper.pack(fill=tk.BOTH, expand=True, padx=36, pady=32)

        # ── Section: Monthly Budgets ──
        self._section_label(wrapper, 'Monthly Budgets')

        cards_area = tk.Frame(wrapper, bg=self.COLORS['bg'])
        cards_area.pack(fill=tk.X)

        sorted_keys = sorted(entries.keys(), reverse=True)

        # 3-column grid
        COLS = 3
        for i, key in enumerate(sorted_keys):
            col = i % COLS
            row = i // COLS
            if col == 0:
                row_frame = tk.Frame(cards_area, bg=self.COLORS['bg'])
                row_frame.pack(fill=tk.X, pady=(0, 16))
                # Pre-create three column slots so layout is always even
                self._col_frames = []
                for c in range(COLS):
                    cf = tk.Frame(row_frame, bg=self.COLORS['bg'])
                    cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                            padx=(0 if c == 0 else 14, 0))
                    self._col_frames.append(cf)

            self._build_budget_card(self._col_frames[col], key, entries[key])

        # ── Section: All Transactions ──
        self._section_label(wrapper, 'All Transactions', top_pad=44)
        self._build_transactions_table(wrapper, entries)

    def _show_empty_state(self):
        frame = tk.Frame(self._body, bg=self.COLORS['bg'])
        frame.pack(expand=True, fill=tk.BOTH)

        box = tk.Frame(frame, bg=self.COLORS['surface'],
                       highlightbackground=self.COLORS['border'],
                       highlightthickness=1)
        box.place(relx=0.5, rely=0.4, anchor='center')

        tk.Label(box, text='📊', font=('Segoe UI', 36),
                 bg=self.COLORS['surface']).pack(pady=(36, 8))
        tk.Label(box, text='No budgets yet',
                 font=self.FONTS['heading'], bg=self.COLORS['surface'],
                 fg=self.COLORS['text']).pack()
        tk.Label(box, text="Click  '+ New Budget'  to get started",
                 font=self.FONTS['body'], bg=self.COLORS['surface'],
                 fg=self.COLORS['text_muted']).pack(pady=(4, 36))

    def _section_label(self, parent, text, top_pad=0):
        tk.Label(parent, text=text, font=self.FONTS['heading'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text']
                 ).pack(anchor=tk.W, pady=(top_pad, 14))

    # ──────────────────────────────────────────────
    #  BUDGET CARD
    # ──────────────────────────────────────────────

    def _build_budget_card(self, parent, key, data):
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        wage = data['wage']
        costs = self.budget.calculate_total_costs(data['costs'])
        debts = self.budget.calculate_total_debts(data['debts'])
        disposable = wage - costs - debts

        card = tk.Frame(parent, bg=self.COLORS['surface'],
                        highlightbackground=self.COLORS['border'],
                        highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Card header strip
        hdr = tk.Frame(card, bg=self.COLORS['primary'], height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        hdr_inner = tk.Frame(hdr, bg=self.COLORS['primary'])
        hdr_inner.pack(fill=tk.BOTH, expand=True, padx=18)

        tk.Label(hdr_inner, text=f'{month_name} {year}',
                 font=self.FONTS['subheading'], bg=self.COLORS['primary'],
                 fg='#FFFFFF').pack(side=tk.LEFT, pady=14)

        edit_btn = tk.Label(hdr_inner, text='Edit →',
                            font=self.FONTS['small_bold'],
                            bg=self.COLORS['primary'], fg='#BFDBFE',
                            cursor='hand2')
        edit_btn.pack(side=tk.RIGHT, pady=14)
        edit_btn.bind('<Button-1>', lambda e, k=key: self.open_edit_budget_window(k))
        edit_btn.bind('<Enter>', lambda e: edit_btn.config(fg='#FFFFFF'))
        edit_btn.bind('<Leave>', lambda e: edit_btn.config(fg='#BFDBFE'))

        # Body
        body = tk.Frame(card, bg=self.COLORS['surface'])
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=16)

        self._card_row(body, 'Income', wage, self.COLORS['success'], self.COLORS['success_bg'])
        self._card_row(body, 'Expenses', costs, self.COLORS['danger'], self.COLORS['danger_bg'])

        rem_fg = self.COLORS['success'] if disposable >= 0 else self.COLORS['danger']
        rem_bg = self.COLORS['success_bg'] if disposable >= 0 else self.COLORS['danger_bg']
        self._card_row(body, 'Remaining', disposable, rem_fg, rem_bg, bold=True)

        # Details button
        det = tk.Label(body, text='View full breakdown →',
                       font=self.FONTS['small_bold'],
                       bg=self.COLORS['surface'], fg=self.COLORS['primary'],
                       cursor='hand2')
        det.pack(anchor=tk.W, pady=(10, 4))
        det.bind('<Button-1>', lambda e, k=key, d=data: self.show_month_details(k, d))
        det.bind('<Enter>', lambda e: det.config(fg=self.COLORS['primary_dark']))
        det.bind('<Leave>', lambda e: det.config(fg=self.COLORS['primary']))

    def _card_row(self, parent, label, amount, fg, bg, bold=False):
        row = tk.Frame(parent, bg=bg)
        row.pack(fill=tk.X, pady=4)

        font = self.FONTS['body_bold'] if bold else self.FONTS['body']

        tk.Label(row, text=label, font=self.FONTS['small'],
                 bg=bg, fg=self.COLORS['text_muted'],
                 padx=10, pady=6).pack(side=tk.LEFT)

        tk.Label(row, text=f'{amount:,.0f} kr', font=font,
                 bg=bg, fg=fg,
                 padx=10, pady=6).pack(side=tk.RIGHT)

    # ──────────────────────────────────────────────
    #  TRANSACTIONS TABLE
    # ──────────────────────────────────────────────

    def _build_transactions_table(self, parent, entries):
        frame = tk.Frame(parent, bg=self.COLORS['surface'],
                         highlightbackground=self.COLORS['border'],
                         highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ('Date', 'Type', 'Description', 'Amount')
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)

        tree.column('Date',        width=110, anchor=tk.CENTER, stretch=False)
        tree.column('Type',        width=130, anchor=tk.CENTER, stretch=False)
        tree.column('Description', width=500, anchor=tk.W,      stretch=True)
        tree.column('Amount',      width=160, anchor=tk.E,       stretch=False)

        for col in cols:
            tree.heading(col, text=col)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview,
                            style='Vertical.TScrollbar')
        tree.configure(yscroll=vsb.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Alternating row colours
        tree.tag_configure('even', background='#F8FAFC')
        tree.tag_configure('odd',  background=self.COLORS['surface'])
        tree.tag_configure('income',  foreground=self.COLORS['success'])
        tree.tag_configure('expense', foreground=self.COLORS['danger'])
        tree.tag_configure('debt',    foreground=self.COLORS['warning'])

        try:
            df = pd.read_csv('budget.csv')
            if not df.empty:
                for idx, row in df.iterrows():
                    date_str  = f"{row['Year']}-{int(row['Month']):02d}"
                    type_lbl  = self._translate_type(row['Type'])
                    row_tag   = 'even' if idx % 2 == 0 else 'odd'
                    type_tag  = {'Income': 'income', 'Expense': 'expense',
                                 'Debt': 'debt'}.get(type_lbl, 'odd')
                    tree.insert('', tk.END,
                                values=(date_str, type_lbl, row['Description'],
                                        f"{float(row['Amount']):,.0f} kr"),
                                tags=(row_tag, type_tag))
        except Exception as e:
            messagebox.showerror('Error', f'Could not load entries: {e}')

    def _translate_type(self, type_str):
        return {'wage': 'Income', 'cost': 'Expense',
                'debt': 'Debt'}.get(type_str.lower(), type_str)

    # ──────────────────────────────────────────────
    #  MONTH DETAILS WINDOW
    # ──────────────────────────────────────────────

    def show_month_details(self, key, data):
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        win = tk.Toplevel(self.root)
        win.title(f'Details — {month_name} {year}')
        win.geometry('600x720')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(True, True)

        self._modal_header(win, f'{month_name} {year}', self.COLORS['primary'])

        # Scrollable content
        outer = tk.Frame(win, bg=self.COLORS['bg'])
        outer.pack(fill=tk.BOTH, expand=True)

        cv = tk.Canvas(outer, bg=self.COLORS['bg'], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=cv.yview,
                           style='Vertical.TScrollbar')
        inner = tk.Frame(cv, bg=self.COLORS['bg'])

        inner.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox('all')))
        win_id = cv.create_window((0, 0), window=inner, anchor='nw')
        cv.configure(yscrollcommand=sb.set)
        cv.bind('<Configure>', lambda e: cv.itemconfig(win_id, width=e.width))
        cv.bind_all('<MouseWheel>', lambda e: cv.yview_scroll(int(-1*(e.delta/120)), 'units'))

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(inner, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        wage        = data['wage']
        total_costs = self.budget.calculate_total_costs(data['costs'])
        total_debts = self.budget.calculate_total_debts(data['debts'])
        disposable  = wage - total_costs - total_debts

        self._detail_section(content, 'Income',   wage,        self.COLORS['success'], [])
        self._detail_section(content, 'Expenses', total_costs, self.COLORS['danger'],  data['costs'])
        self._detail_section(content, 'Debts',    total_debts, self.COLORS['warning'], data['debts'])

        # Summary bar
        s_fg = self.COLORS['success'] if disposable >= 0 else self.COLORS['danger']
        s_bg = self.COLORS['success_bg'] if disposable >= 0 else self.COLORS['danger_bg']

        bar = tk.Frame(content, bg=s_bg, highlightbackground=s_fg, highlightthickness=1)
        bar.pack(fill=tk.X, pady=(20, 0))

        bar_inner = tk.Frame(bar, bg=s_bg)
        bar_inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

        tk.Label(bar_inner, text='Remaining',
                 font=self.FONTS['small'], bg=s_bg,
                 fg=self.COLORS['text_muted']).pack(anchor=tk.W)
        tk.Label(bar_inner, text=f'{disposable:,.0f} kr',
                 font=('Segoe UI', 20, 'bold'), bg=s_bg,
                 fg=s_fg).pack(anchor=tk.W, pady=(4, 0))

    def _detail_section(self, parent, title, total, color, items):
        section = tk.Frame(parent, bg=self.COLORS['surface'],
                           highlightbackground=self.COLORS['border'],
                           highlightthickness=1)
        section.pack(fill=tk.X, pady=(0, 14))

        # Coloured header strip
        hdr = tk.Frame(section, bg=color, height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        hi = tk.Frame(hdr, bg=color)
        hi.pack(fill=tk.BOTH, expand=True, padx=16)

        tk.Label(hi, text=title, font=self.FONTS['body_bold'],
                 bg=color, fg='#FFFFFF').pack(side=tk.LEFT, pady=12)
        tk.Label(hi, text=f'{total:,.0f} kr', font=self.FONTS['body_bold'],
                 bg=color, fg='#FFFFFF').pack(side=tk.RIGHT, pady=12)

        # Item rows
        if items:
            item_frame = tk.Frame(section, bg=self.COLORS['surface'])
            item_frame.pack(fill=tk.X, padx=16, pady=12)

            for name, amount in items:
                row = tk.Frame(item_frame, bg=self.COLORS['surface'])
                row.pack(fill=tk.X, pady=5)

                tk.Label(row, text=name, font=self.FONTS['body'],
                         bg=self.COLORS['surface'],
                         fg=self.COLORS['text']).pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(row, text=f'{amount:,.0f} kr', font=self.FONTS['body_bold'],
                         bg=self.COLORS['surface'],
                         fg=color).pack(side=tk.RIGHT)

    # ──────────────────────────────────────────────
    #  CREATE BUDGET WINDOW
    # ──────────────────────────────────────────────

    def open_create_budget_window(self):
        win = tk.Toplevel(self.root)
        win.title('Create New Budget')
        win.geometry('560x760')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, True)

        self._modal_header(win, 'Create Monthly Budget', self.COLORS['primary'])

        # Scrollable form
        outer = tk.Frame(win, bg=self.COLORS['bg'])
        outer.pack(fill=tk.BOTH, expand=True)

        cv = tk.Canvas(outer, bg=self.COLORS['bg'], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=cv.yview,
                           style='Vertical.TScrollbar')
        form_wrap = tk.Frame(cv, bg=self.COLORS['bg'])

        form_wrap.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox('all')))
        wid = cv.create_window((0, 0), window=form_wrap, anchor='nw')
        cv.configure(yscrollcommand=sb.set)
        cv.bind('<Configure>', lambda e: cv.itemconfig(wid, width=e.width))

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(form_wrap, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        # ── Period ──
        self._form_section_label(content, 'Period')
        year_var  = self._form_field(content, 'Year',  str(datetime.now().year))
        month_var = self._form_field(content, 'Month', str(datetime.now().month))

        # ── Income ──
        self._form_section_label(content, 'Income')
        wage_desc_var   = self._form_field(content, 'Description')
        wage_amount_var = self._form_field(content, 'Amount (kr)')

        # ── Expenses ──
        self._form_section_label(content, 'Expenses')
        exp_lb = self._form_listbox(content)

        def add_expense():
            desc = simpledialog.askstring('Add Expense', 'Description:', parent=win)
            if desc:
                amount = simpledialog.askfloat('Add Expense', 'Amount (kr):', parent=win)
                if amount:
                    exp_lb.insert(tk.END, f'{desc}: {amount:,.0f} kr')

        def remove_expense():
            sel = exp_lb.curselection()
            if sel:
                exp_lb.delete(sel[0])

        self._form_list_buttons(content, add_expense, remove_expense,
                                self.COLORS['danger'])

        # ── Debts ──
        self._form_section_label(content, 'Debts')
        debt_lb = self._form_listbox(content)

        def add_debt():
            desc = simpledialog.askstring('Add Debt', 'Description:', parent=win)
            if desc:
                amount = simpledialog.askfloat('Add Debt', 'Amount (kr):', parent=win)
                if amount:
                    debt_lb.insert(tk.END, f'{desc}: {amount:,.0f} kr')

        def remove_debt():
            sel = debt_lb.curselection()
            if sel:
                debt_lb.delete(sel[0])

        self._form_list_buttons(content, add_debt, remove_debt,
                                self.COLORS['warning'])

        # ── Submit ──
        def submit():
            try:
                year        = int(year_var.get())
                month       = int(month_var.get())
                wage_desc   = wage_desc_var.get().strip()
                wage_amount = float(wage_amount_var.get())

                if not wage_desc or wage_amount <= 0:
                    messagebox.showerror('Error', 'Enter a valid income', parent=win)
                    return

                self.budget.add_entry(year, month, 'wage', wage_desc, wage_amount)

                for item in exp_lb.get(0, tk.END):
                    desc, amt = item.rsplit(':', 1)
                    self.budget.add_entry(year, month, 'cost', desc.strip(),
                                         float(amt.strip().replace('kr', '').replace(',', '').strip()))

                for item in debt_lb.get(0, tk.END):
                    desc, amt = item.rsplit(':', 1)
                    self.budget.add_entry(year, month, 'debt', desc.strip(),
                                         float(amt.strip().replace('kr', '').replace(',', '').strip()))

                messagebox.showinfo('Success',
                                    f'Budget for {year}-{month:02d} created!', parent=win)
                win.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror('Error', f'Could not create budget: {e}', parent=win)

        tk.Frame(content, bg=self.COLORS['bg'], height=8).pack()
        self._mk_btn(content, 'Create Budget', self.COLORS['success'], submit,
                     side=tk.TOP, pady=(4, 0))

    # ──────────────────────────────────────────────
    #  EDIT BUDGET WINDOW
    # ──────────────────────────────────────────────

    def open_edit_budget_window(self, key):
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        win = tk.Toplevel(self.root)
        win.title('Edit Budget')
        win.geometry('480x280')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, False)

        self._modal_header(win, f'Edit — {month_name} {year}', self.COLORS['secondary'])

        content = tk.Frame(win, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        info = tk.Label(content,
                        text='Use "Add Entry" to add new rows to this month\'s budget.',
                        font=self.FONTS['body'], bg=self.COLORS['bg'],
                        fg=self.COLORS['text_muted'], wraplength=400, justify=tk.LEFT)
        info.pack(anchor=tk.W, pady=(0, 20))

        self._mk_btn(content, '+ Add Entry to this month',
                     self.COLORS['primary'], self.open_add_entry_window,
                     side=tk.TOP, pady=(0, 10))

        self._mk_btn(content, 'Close', self.COLORS['text_muted'],
                     win.destroy, side=tk.TOP)

    # ──────────────────────────────────────────────
    #  ADD ENTRY WINDOW
    # ──────────────────────────────────────────────

    def open_add_entry_window(self):
        win = tk.Toplevel(self.root)
        win.title('Add Entry')
        win.geometry('480x460')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, False)

        self._modal_header(win, 'Add Budget Entry', self.COLORS['secondary'])

        content = tk.Frame(win, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        year_var    = self._form_field(content, 'Year',   str(datetime.now().year))
        month_var   = self._form_field(content, 'Month',  str(datetime.now().month))
        type_var    = self._form_field(content, 'Type',   combo=True)
        desc_var    = self._form_field(content, 'Description')
        amount_var  = self._form_field(content, 'Amount (kr)')

        def submit():
            try:
                year        = int(year_var.get())
                month       = int(month_var.get())
                entry_type  = type_var.get()
                description = desc_var.get().strip()
                amount      = float(amount_var.get())

                if not all([year, month, entry_type, description, amount]):
                    messagebox.showerror('Error', 'Please fill in all fields', parent=win)
                    return

                self.budget.add_entry(year, month, entry_type, description, amount)
                messagebox.showinfo('Success', 'Entry added successfully!', parent=win)
                win.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror('Error', f'Could not add entry: {e}', parent=win)

        tk.Frame(content, bg=self.COLORS['bg'], height=4).pack()
        self._mk_btn(content, 'Add Entry', self.COLORS['success'], submit,
                     side=tk.TOP, pady=(8, 0))

    # ──────────────────────────────────────────────
    #  REUSABLE FORM HELPERS
    # ──────────────────────────────────────────────

    def _modal_header(self, win, text, color):
        hdr = tk.Frame(win, bg=color, height=64)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=text, font=self.FONTS['heading'],
                 bg=color, fg='#FFFFFF').pack(side=tk.LEFT, padx=26, pady=18)

    def _form_section_label(self, parent, text):
        tk.Frame(parent, bg=self.COLORS['border'], height=1).pack(fill=tk.X, pady=(16, 12))
        tk.Label(parent, text=text, font=self.FONTS['subheading'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text']).pack(anchor=tk.W, pady=(0, 8))

    def _form_field(self, parent, label, default='', combo=False):
        row = tk.Frame(parent, bg=self.COLORS['bg'])
        row.pack(fill=tk.X, pady=6)

        tk.Label(row, text=label, font=self.FONTS['small'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text_muted'],
                 width=14, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 12))

        var = tk.StringVar(value=default)
        if combo:
            widget = ttk.Combobox(row, textvariable=var,
                                  values=['wage', 'cost', 'debt'],
                                  state='readonly', font=self.FONTS['body'])
        else:
            widget = tk.Entry(row, textvariable=var, font=self.FONTS['body'],
                              bg=self.COLORS['surface'], fg=self.COLORS['text'],
                              relief=tk.FLAT, bd=0,
                              highlightbackground=self.COLORS['border'],
                              highlightthickness=1,
                              insertbackground=self.COLORS['primary'])

            def _focus_in(e):
                widget.config(highlightbackground=self.COLORS['border_focus'],
                              highlightthickness=2)
            def _focus_out(e):
                widget.config(highlightbackground=self.COLORS['border'],
                              highlightthickness=1)
            widget.bind('<FocusIn>',  _focus_in)
            widget.bind('<FocusOut>', _focus_out)

        widget.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        return var

    def _form_listbox(self, parent):
        lb = tk.Listbox(parent, height=4, font=self.FONTS['body'],
                        bg=self.COLORS['surface'], fg=self.COLORS['text'],
                        selectbackground='#EFF6FF',
                        selectforeground=self.COLORS['primary'],
                        relief=tk.FLAT, bd=0,
                        highlightbackground=self.COLORS['border'],
                        highlightthickness=1,
                        activestyle='none')
        lb.pack(fill=tk.X, pady=(0, 6))
        return lb

    def _form_list_buttons(self, parent, add_cmd, remove_cmd, add_color):
        row = tk.Frame(parent, bg=self.COLORS['bg'])
        row.pack(fill=tk.X, pady=(0, 4))
        self._mk_btn(row, '+ Add', add_color, add_cmd, side=tk.LEFT, padx=(0, 8))
        self._mk_btn(row, '✕ Remove selected', '#94A3B8', remove_cmd, side=tk.LEFT)

    # ──────────────────────────────────────────────
    #  LEGACY SHIM (kept so nothing external breaks)
    # ──────────────────────────────────────────────

    def create_summary_row(self, parent, label, value, color):
        self._card_row(parent, label, 0, color, self.COLORS['surface'])

    def translate_type(self, type_str):
        return self._translate_type(type_str)