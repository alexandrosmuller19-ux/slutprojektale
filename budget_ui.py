import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from budget_manager import BudgetManager
from datetime import datetime


class BudgetUI:
    # Professionell Budget Manager GUI med modernt design.

    MONTH_NAMES = {
        1: "Januari", 2: "Februari", 3: "Mars", 4: "April", 5: "Maj", 6: "Juni",
        7: "Juli", 8: "Augusti", 9: "September", 10: "Oktober", 11: "November", 12: "December"
    }

    COLORS = {
        'primary':      '#1A56DB',
        'primary_dark': '#1344B7',
        'primary_light':'#F0F9FF',
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
        'surface_alt':  '#F1F5F9',
        'border':       '#E2E8F0',
        'border_focus': '#93C5FD',
        'text':         '#0F172A',
        'text_muted':   '#64748B',
        'text_light':   '#94A3B8',
        'sidebar_bg':   '#1E293B',
        'sidebar_text': '#CBD5E1',
        'shadow':       '#00000008',
    }

    FONTS = {
        'title':        ('Segoe UI', 26, 'bold'),
        'heading':      ('Segoe UI', 18, 'bold'),
        'subheading':   ('Segoe UI', 14, 'bold'),
        'body':         ('Segoe UI', 11),
        'body_bold':    ('Segoe UI', 12, 'bold'),
        'small':        ('Segoe UI', 10),
        'small_bold':   ('Segoe UI', 11, 'bold'),
        'mono':         ('Consolas', 11),
    }

    def __init__(self, root):
        # Initierar huvudapplikationsfönstret
        self.root = root
        self.root.title("Budget Manager")
        self.root.geometry("1400x860")
        self.root.minsize(900, 600)
        self.root.configure(bg=self.COLORS['bg'])

        # Initierar budgethanteraren som hanterar data
        self.budget = BudgetManager("budget.csv")

        # Konfigurerar UI-stilar och bygger layouten
        self._setup_styles()
        self._build_layout()
        # Laddar och visar initial data
        self.refresh_data()

    # STILAR

    def _setup_styles(self):
        # Konfigurerar alla ttk-widgetstillar med anpassade färger och typsnitt
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

    #  LAYOUT SKELETT

    def _build_layout(self):
        # Bygger det övre navigeringsfältet
        self._build_navbar()

        # Lägger till en tunn avdelarlinje under navigeringsfältet
        tk.Frame(self.root, bg=self.COLORS['border'], height=1).pack(fill=tk.X)

        # Skapar ett rullningsbart huvudinnehållsområde
        body_outer = tk.Frame(self.root, bg=self.COLORS['bg'])
        body_outer.pack(fill=tk.BOTH, expand=True)

        # Konfigurerar canvas med vertikal scrolllist för smidig rullning
        self._canvas = tk.Canvas(body_outer, bg=self.COLORS['bg'],
                                 highlightthickness=0, bd=0)
        _vsb = ttk.Scrollbar(body_outer, orient=tk.VERTICAL,
                              command=self._canvas.yview, style='Vertical.TScrollbar')
        self._canvas.configure(yscrollcommand=_vsb.set)

        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inre ram som håller allt innehåll (kort, tabeller, osv.)
        self._body = tk.Frame(self._canvas, bg=self.COLORS['bg'])
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._body, anchor='nw'
        )

        # Binder storleksändringshändelser för att uppdatera rullningsområdet
        self._body.bind('<Configure>', self._on_body_resize)
        self._canvas.bind('<Configure>', self._on_canvas_resize)

        # Aktiverar mushjulsrullning för alla plattformar (Windows, Mac, Linux)
        self._canvas.bind('<MouseWheel>', self._on_mousewheel)
        self._canvas.bind('<Button-4>', self._on_mousewheel_linux)  # Linux rulla upp
        self._canvas.bind('<Button-5>', self._on_mousewheel_linux)  # Linux rulla ner
        self._body.bind_all('<MouseWheel>', self._on_mousewheel)

        # Säkerställer att canvas kan ta emot fokus och rullningshändelser
        self._canvas.focus_set()

    def _on_body_resize(self, event):
        # Uppdaterar rullningsområdet när innehållets storlek förändras
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _on_canvas_resize(self, event):
        # Justerar canvasens fönsterbredd för att matcha canvasens bredd
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Hanterar mushjulsrullning på Windows/Mac
        try:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        except:
            pass

    def _on_mousewheel_linux(self, event):
        # Hanterar mushjulsrullning på Linux (olika knappkoder)
        if event.num == 4:
            # Rulla upp
            self._canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            # Rulla ner
            self._canvas.yview_scroll(1, 'units')

    #  NAVBAR

    def _build_navbar(self):
        # Skapar det övre navigeringsfältet med logotyp och åtgärdsknappar
        nav = tk.Frame(self.root, bg=self.COLORS['surface'], height=68)
        nav.pack(fill=tk.X, side=tk.TOP)
        nav.pack_propagate(False)

        inner = tk.Frame(nav, bg=self.COLORS['surface'])
        inner.pack(fill=tk.BOTH, expand=True, padx=36, pady=0)

        # Vänster sida: Logotyp och apptitel
        logo_wrap = tk.Frame(inner, bg=self.COLORS['surface'])
        logo_wrap.pack(side=tk.LEFT, fill=tk.Y)

        dot = tk.Label(logo_wrap, text='●', font=('Segoe UI', 14),
                       bg=self.COLORS['surface'], fg=self.COLORS['primary'])
        dot.pack(side=tk.LEFT, padx=(0, 8), pady=22)

        title = tk.Label(logo_wrap, text='Budget Manager', font=self.FONTS['heading'],
                         bg=self.COLORS['surface'], fg=self.COLORS['text'])
        title.pack(side=tk.LEFT, pady=22)

        # Höger sida: Åtgärdsknappar
        btn_wrap = tk.Frame(inner, bg=self.COLORS['surface'])
        btn_wrap.pack(side=tk.RIGHT, fill=tk.Y, pady=14)

        # Knapp för att skapa ny månadsbudget
        self._mk_btn(btn_wrap, '+ New Budget', self.COLORS['primary'],
                     self.open_create_budget_window, side=tk.LEFT, padx=(0, 10))
        # Knapp för att lägga till enskild post
        self._mk_btn(btn_wrap, '+ Add Entry', self.COLORS['secondary'],
                     self.open_add_entry_window, side=tk.LEFT)

    #  HJÄLP: skapa en platt knapp med hovering-effekt

    def _mk_btn(self, parent, text, bg_color, command,
                side=tk.LEFT, padx=0, pady=0, width=None):
        btn = tk.Button(parent, text=text, font=self.FONTS['body_bold'],
                        bg=bg_color, fg='#FFFFFF', activebackground=bg_color,
                        activeforeground='#FFFFFF', relief=tk.FLAT,
                        cursor='hand2', bd=0, padx=20, pady=11,
                        command=command)
        if width:
            btn.config(width=width)
        btn.pack(side=side, padx=padx, pady=pady)

        # Mörkna vid hovring
        def _darken(e, c=bg_color):
            r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            d = lambda v: max(0, int(v * 0.80))
            btn.config(bg=f'#{d(r):02x}{d(g):02x}{d(b):02x}')

        def _restore(e, c=bg_color):
            btn.config(bg=c)

        btn.bind('<Enter>', _darken)
        btn.bind('<Leave>', _restore)
        return btn

    #  UPPDATERA  (rensar kroppen och ritar om allting)

    def refresh_data(self):
        # Rensar befintligt innehåll och laddar om data från CSV
        for w in self._body.winfo_children():
            w.destroy()

        # Laddar alla budgetposter organiserade per månad
        entries = self.budget.load_all_entries()

        # Visar tomt tillstånd om ingen data finns
        if not entries:
            self._show_empty_state()
            return

        wrapper = tk.Frame(self._body, bg=self.COLORS['bg'])
        wrapper.pack(fill=tk.BOTH, expand=True, padx=36, pady=32)

        # Visar sammanfattningsmått (total inkomst, utgifter, osv.) längst upp
        self._build_dashboard_summary(wrapper, entries)

        # Skapar sektion för månadsbudgetkort
        self._section_label(wrapper, 'Monthly Budgets', top_pad=28)

        cards_area = tk.Frame(wrapper, bg=self.COLORS['bg'])
        cards_area.pack(fill=tk.X)

        # Sorterar poster efter datum i omvänd ordning (nyaste först)
        sorted_keys = sorted(entries.keys(), reverse=True)

        # Layoutar kort i 3 kolumner
        COLS = 3
        for i, key in enumerate(sorted_keys):
            col = i % COLS
            row = i // COLS
            # Skapar ny rad var tredje kort
            if col == 0:
                row_frame = tk.Frame(cards_area, bg=self.COLORS['bg'])
                row_frame.pack(fill=tk.X, pady=(0, 20))
                # Förbereder kolumnramar för konsekvent layout
                self._col_frames = []
                for c in range(COLS):
                    cf = tk.Frame(row_frame, bg=self.COLORS['bg'])
                    cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                            padx=(0 if c == 0 else 14, 0))
                    self._col_frames.append(cf)

            # Bygger individuellt budgetkort
            self._build_budget_card(self._col_frames[col], key, entries[key])

        # Visar alla transaktioner i tabellformat
        self._section_label(wrapper, 'Transaction History', top_pad=44)
        self._build_transactions_table(wrapper, entries)

    def _show_empty_state(self):
        # Visar platshållare när inga budgetar har skapats
        frame = tk.Frame(self._body, bg=self.COLORS['bg'])
        frame.pack(expand=True, fill=tk.BOTH)

        # Centrerar den tomma tillståndsrutan
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

    def _build_dashboard_summary(self, parent, entries):
        # Beräknar och visar övergripande ekonomiska sammanfattningsmått
        total_income = 0
        total_expenses = 0
        total_debts = 0

        # Summerar alla poster över alla månader
        for data in entries.values():
            total_income += data['wage']
            total_expenses += self.budget.calculate_total_costs(data['costs'])
            total_debts += self.budget.calculate_total_debts(data['debts'])

        # Beräknar återstående saldo
        remaining = total_income - total_expenses - total_debts

        dashboard = tk.Frame(parent, bg=self.COLORS['bg'])
        dashboard.pack(fill=tk.X, pady=(0, 8))

        # Visar 4 viktiga ekonomiska nyckeltal
        metrics = [
            ('Total Income', f'{total_income:,.0f} kr', self.COLORS['success'], self.COLORS['success_bg']),
            ('Total Expenses', f'{total_expenses:,.0f} kr', self.COLORS['danger'], self.COLORS['danger_bg']),
            ('Total Debts', f'{total_debts:,.0f} kr', self.COLORS['warning'], self.COLORS['warning_bg']),
            ('Remaining', f'{remaining:,.0f} kr',
             self.COLORS['success'] if remaining >= 0 else self.COLORS['danger'],
             self.COLORS['success_bg'] if remaining >= 0 else self.COLORS['danger_bg']),
        ]

        for label, value, color, bg in metrics:
            self._build_metric_card(dashboard, label, value, color, bg)

    def _build_metric_card(self, parent, label, value, color, bg):
        # Skapar individuellt måttkort med etikett och värde
        card = tk.Frame(parent, bg=bg,
                        highlightbackground=color,
                        highlightthickness=2)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12), pady=0)

        inner = tk.Frame(card, bg=bg)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(inner, text=label, font=self.FONTS['small'],
                 bg=bg, fg=self.COLORS['text_muted']).pack(anchor=tk.W)
        tk.Label(inner, text=value, font=self.FONTS['heading'],
                 bg=bg, fg=color).pack(anchor=tk.W, pady=(4, 0))

    def _section_label(self, parent, text, top_pad=0):
        label_frame = tk.Frame(parent, bg=self.COLORS['bg'])
        label_frame.pack(anchor=tk.W, pady=(top_pad, 20), fill=tk.X)

        tk.Label(label_frame, text=text, font=self.FONTS['heading'],
                 bg=self.COLORS['bg'], fg=self.COLORS['primary']
                 ).pack(anchor=tk.W, side=tk.LEFT)

        # Dekorativ linje
        line = tk.Frame(label_frame, bg=self.COLORS['primary'], height=3)
        line.pack(anchor=tk.W, pady=(10, 0), fill=tk.X, expand=True, padx=(160, 0))

    #  BUDGETKORT

    def _build_budget_card(self, parent, key, data):
        # Skapar ett kort som visar ekonomisk sammanfattning för en månad
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        # Beräknar ekonomiska totaler för månaden
        wage = data['wage']
        costs = self.budget.calculate_total_costs(data['costs'])
        debts = self.budget.calculate_total_debts(data['debts'])
        disposable = wage - costs - debts

        # Skapar kortbehållaren
        card = tk.Frame(parent, bg=self.COLORS['surface'],
                        highlightbackground=self.COLORS['border'],
                        highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Skapar färgad rubrik som visar månad och år
        hdr = tk.Frame(card, bg=self.COLORS['primary'], height=68)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        hdr_inner = tk.Frame(hdr, bg=self.COLORS['primary'])
        hdr_inner.pack(fill=tk.BOTH, expand=True, padx=18)

        # Vänster sida: Månad och år som titel
        title_frame = tk.Frame(hdr_inner, bg=self.COLORS['primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=14)

        tk.Label(title_frame, text=f'{month_name}', font=('Segoe UI', 18, 'bold'),
                 bg=self.COLORS['primary'], fg='#FFFFFF').pack(anchor=tk.W)
        tk.Label(title_frame, text=f'{year}', font=self.FONTS['small'],
                 bg=self.COLORS['primary'], fg='#BFDBFE').pack(anchor=tk.W)

        # Höger sida: Redigeringsknapp med hovringeffekt
        edit_btn = tk.Label(hdr_inner, text='Edit →',
                            font=self.FONTS['small_bold'],
                            bg=self.COLORS['primary'], fg='#BFDBFE',
                            cursor='hand2')
        edit_btn.pack(side=tk.RIGHT, pady=14)
        edit_btn.bind('<Button-1>', lambda e, k=key: self.open_edit_budget_window(k))
        edit_btn.bind('<Enter>', lambda e: edit_btn.config(fg='#FFFFFF'))
        edit_btn.bind('<Leave>', lambda e: edit_btn.config(fg='#BFDBFE'))

        # Kortets kropp: Ekonomisk uppdelning
        body = tk.Frame(card, bg=self.COLORS['surface'])
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        # Visar inkomstrad
        self._card_row(body, 'Income', wage, self.COLORS['success'],
                       self.COLORS['success_bg'], is_main=True)

        # Visar utgiftsrad
        self._card_row(body, 'Expenses', costs, self.COLORS['danger'],
                       self.COLORS['danger_bg'], is_main=True)

        # Visar skuldsrad (om några finns)
        if debts > 0:
            self._card_row(body, 'Debts', debts, self.COLORS['warning'],
                           self.COLORS['warning_bg'], is_main=False)

        # Visar återstående saldo (grön om positivt, röd om negativt)
        rem_fg = self.COLORS['success'] if disposable >= 0 else self.COLORS['danger']
        rem_bg = self.COLORS['success_bg'] if disposable >= 0 else self.COLORS['danger_bg']
        self._card_row(body, 'Remaining', disposable, rem_fg, rem_bg, bold=True, is_main=True)

        # Visuell avdelare
        tk.Frame(body, bg=self.COLORS['border'], height=1).pack(fill=tk.X, pady=12)

        # Länk till detaljerad uppdelningsvy
        det = tk.Label(body, text='View full breakdown →',
                       font=self.FONTS['small_bold'],
                       bg=self.COLORS['surface'], fg=self.COLORS['primary'],
                       cursor='hand2')
        det.pack(anchor=tk.W)
        det.bind('<Button-1>', lambda e, k=key, d=data: self.show_month_details(k, d))
        det.bind('<Enter>', lambda e: det.config(fg=self.COLORS['primary_dark']))
        det.bind('<Leave>', lambda e: det.config(fg=self.COLORS['primary']))

    def _card_row(self, parent, label, amount, fg, bg, bold=False, is_main=False):
        row = tk.Frame(parent, bg=bg if is_main else self.COLORS['surface'])
        row.pack(fill=tk.X, pady=(8 if not is_main else 10))

        font = self.FONTS['body_bold'] if bold else self.FONTS['body']
        label_font = ('Segoe UI', 12, 'bold') if is_main else self.FONTS['small_bold']

        tk.Label(row, text=label, font=label_font,
                 bg=bg if is_main else self.COLORS['surface'],
                 fg=self.COLORS['text'] if is_main else self.COLORS['text_muted'],
                 padx=(12 if is_main else 0), pady=(8 if is_main else 4)).pack(side=tk.LEFT)

        tk.Label(row, text=f'{amount:,.0f} kr', font=('Segoe UI', 13, 'bold') if is_main else font,
                 bg=bg if is_main else self.COLORS['surface'], fg=fg,
                 padx=(12 if is_main else 0), pady=(8 if is_main else 4)).pack(side=tk.RIGHT)

    #  TRANSAKTIONER TABELL

    def _build_transactions_table(self, parent, entries):
        # Skapar en tabell med alla enskilda transaktioner sorterade efter datum
        frame = tk.Frame(parent, bg=self.COLORS['surface'],
                         highlightbackground=self.COLORS['border'],
                         highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)

        # Definierar tabellkolumner
        cols = ('Date', 'Type', 'Description', 'Amount')
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=15)

        # Anger kolumnbredder och justering
        tree.column('Date',        width=110, anchor=tk.CENTER, stretch=False)
        tree.column('Type',        width=130, anchor=tk.CENTER, stretch=False)
        tree.column('Description', width=400, anchor=tk.W,      stretch=True)
        tree.column('Amount',      width=120, anchor=tk.E,      stretch=False)

        for col in cols:
            tree.heading(col, text=col)

        # Lägger till vertikal scrolllist i tabellen
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview,
                            style='Vertical.TScrollbar')
        tree.configure(yscroll=vsb.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Konfigurerar alternerande radfärger och posttypsf\u00e4rger
        tree.tag_configure('even', background='#F8FAFC')
        tree.tag_configure('odd',  background=self.COLORS['surface'])
        tree.tag_configure('income',  foreground=self.COLORS['success'])
        tree.tag_configure('expense', foreground=self.COLORS['danger'])
        tree.tag_configure('debt',    foreground=self.COLORS['warning'])

        # Sparar tabelldata för referens
        self._table_entries = []

        try:
            all_entries = self.budget.get_all_raw_entries()
            if all_entries:
                # Fyller tabellen med alla transaktioner
                for csv_idx, row in enumerate(all_entries):
                    date_str  = f"{row['Year']}-{int(row['Month']):02d}"
                    type_lbl  = self._translate_type(row['Type'])
                    row_tag   = 'even' if csv_idx % 2 == 0 else 'odd'
                    type_tag  = {'Income': 'income', 'Expense': 'expense',
                                 'Debt': 'debt'}.get(type_lbl, 'odd')

                    # Sparar postens metadata för redigering och borttagning
                    self._table_entries.append({
                        'csv_index': csv_idx,
                        'Year': int(row['Year']),
                        'Month': int(row['Month']),
                        'Type': row['Type'],
                        'Description': row['Description'],
                        'Amount': float(row['Amount'])
                    })

                    # Infogar formaterad rad i tabellen
                    tree.insert('', tk.END,
                                values=(date_str, type_lbl, row['Description'],
                                        f"{float(row['Amount']):,.0f} kr"),
                                tags=(row_tag, type_tag))
        except Exception as e:
            messagebox.showerror('Error', f'Could not load entries: {e}')

        # Binder dubbelklick för att redigera vald post
        def on_double_click(event):
            selection = tree.selection()
            if selection:
                item_id = selection[0]
                # Hämtar index för den klickade raden
                idx = int(tree.index(item_id))
                if 0 <= idx < len(self._table_entries):
                    entry = self._table_entries[idx]
                    # Öppnar redigeringsfönster för vald post
                    self.open_edit_entry_window(entry['csv_index'], entry)

        tree.bind('<Double-1>', on_double_click)

    def _translate_type(self, type_str):
        # Konverterar posttypskoder till visningsetiketter
        return {'wage': 'Income', 'cost': 'Expense',
                'debt': 'Debt'}.get(type_str.lower(), type_str)

    #  EDIT ENTRY FÖNSTER

    def open_edit_entry_window(self, csv_index, entry_data):
        """Öppnar fönster för att redigera en befintlig post"""
        win = tk.Toplevel(self.root)
        win.title('Edit Entry')
        win.geometry('500x520')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, False)

        self._modal_header(win, 'Edit Budget Entry', self.COLORS['warning'])

        content = tk.Frame(win, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        # ── Postdetaljer ──
        self._form_section_label(content, '📝 Entry Details', top_pad=0)

        type_mapping = {'wage': 'wage', 'cost': 'cost', 'debt': 'debt'}
        type_var = tk.StringVar(value=type_mapping.get(entry_data['Type'].lower(), 'cost'))

        # Typfält
        row = tk.Frame(content, bg=self.COLORS['bg'])
        row.pack(fill=tk.X, pady=8)
        tk.Label(row, text='Type', font=self.FONTS['small_bold'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text'],
                 width=16, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 12), pady=(0, 4))
        type_widget = ttk.Combobox(row, textvariable=type_var,
                                   values=['wage', 'cost', 'debt'],
                                   state='readonly', font=self.FONTS['body'])
        type_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        desc_var = self._form_field(content, 'Description', entry_data['Description'])
        amount_var = self._form_field(content, 'Amount (kr)', str(entry_data['Amount']))

        # ── När ──
        self._form_section_label(content, '📅 When')
        year_var = self._form_field(content, 'Year', str(entry_data['Year']))
        month_var = self._form_field(content, 'Month', str(entry_data['Month']))

        def submit():
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                entry_type = type_var.get()
                description = desc_var.get().strip()
                amount = float(amount_var.get())

                if not all([year, month, entry_type, description, amount]):
                    messagebox.showerror('Error', 'Please fill in all fields', parent=win)
                    return

                # Uppdaterar posten
                self.budget.update_entry(csv_index, year, month, entry_type, description, amount)
                messagebox.showinfo('Success', 'Entry updated successfully!', parent=win)
                win.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror('Error', f'Could not update entry: {e}', parent=win)

        tk.Frame(content, bg=self.COLORS['bg'], height=16).pack()
        btn_frame = tk.Frame(content, bg=self.COLORS['bg'])
        btn_frame.pack(fill=tk.X)
        self._mk_btn(btn_frame, 'Save Changes', self.COLORS['warning'], submit,
                     side=tk.LEFT, padx=(0, 8))
        self._mk_btn(btn_frame, 'Cancel', self.COLORS['text_light'], win.destroy,
                     side=tk.LEFT)

    def _show_entry_context_menu(self, event, csv_index, entry_data):
        """Visar högerklickskontextmeny för tabellpost"""
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label='✏️  Edit',
                        command=lambda: self.open_edit_entry_window(csv_index, entry_data))
        menu.add_command(label='🗑️  Delete',
                        command=lambda: self._delete_entry_prompt(csv_index, entry_data))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _delete_entry_prompt(self, csv_index, entry_data):
        """Visar bekräftelsedialog innan post tas bort"""
        desc = entry_data['Description']
        amount = entry_data['Amount']
        msg = f'Delete entry: {desc} ({amount} kr)?\n\nThis action cannot be undone.'

        if messagebox.askyesno('Confirm Delete', msg):
            self.budget.delete_entry(csv_index)
            self.refresh_data()

    def _quick_edit_entry(self, year, month, description, amount):
        """Snabbredigering för poster från månadsdetaljvyn"""
        # Hittar CSV-index för denna post
        all_entries = self.budget.get_all_raw_entries()
        for idx, entry in enumerate(all_entries):
            if (int(entry['Year']) == year and
                int(entry['Month']) == month and
                entry['Description'] == description and
                float(entry['Amount']) == amount):
                entry_data = {
                    'Year': year,
                    'Month': month,
                    'Type': entry['Type'],
                    'Description': description,
                    'Amount': amount
                }
                self.open_edit_entry_window(idx, entry_data)
                return
        messagebox.showerror('Error', 'Could not find entry to edit')

    #  MÅNADFÖNSTER DETALJER

    def show_month_details(self, key, data):
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        win = tk.Toplevel(self.root)
        win.title(f'Details — {month_name} {year}')
        win.geometry('600x720')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(True, True)

        self._modal_header(win, f'{month_name} {year}', self.COLORS['primary'])

        # Rullningsbart innehåll
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
        # Binder rullningshändelser endast till denna canvas för att undvika konflikter när modalen stängs
        def safe_scroll_mouse(e):
            try:
                cv.yview_scroll(int(-1*(e.delta/120)), 'units')
            except:
                pass

        def safe_scroll_linux(delta):
            def handler(e):
                try:
                    cv.yview_scroll(delta, 'units')
                except:
                    pass
            return handler

        cv.bind('<MouseWheel>', safe_scroll_mouse)
        cv.bind('<Button-4>', safe_scroll_linux(-1))  # Linux rulla upp
        cv.bind('<Button-5>', safe_scroll_linux(1))   # Linux rulla ner

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(inner, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        wage        = data['wage']
        total_costs = self.budget.calculate_total_costs(data['costs'])
        total_debts = self.budget.calculate_total_debts(data['debts'])
        disposable  = wage - total_costs - total_debts

        self._detail_section(content, 'Income',   wage,        self.COLORS['success'], [], int(year), int(month))
        self._detail_section(content, 'Expenses', total_costs, self.COLORS['danger'],  data['costs'], int(year), int(month))
        self._detail_section(content, 'Debts',    total_debts, self.COLORS['warning'], data['debts'], int(year), int(month))

        # Sammanfattningsbar
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

    def _detail_section(self, parent, title, total, color, items, year=None, month=None):
        section = tk.Frame(parent, bg=self.COLORS['surface'],
                           highlightbackground=self.COLORS['border'],
                           highlightthickness=1)
        section.pack(fill=tk.X, pady=(0, 16))

        # Färgat huvudstreck
        hdr = tk.Frame(section, bg=color, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        hi = tk.Frame(hdr, bg=color)
        hi.pack(fill=tk.BOTH, expand=True, padx=18)

        tk.Label(hi, text=title, font=('Segoe UI', 13, 'bold'),
                 bg=color, fg='#FFFFFF').pack(side=tk.LEFT, pady=13)
        tk.Label(hi, text=f'{total:,.0f} kr', font=('Segoe UI', 14, 'bold'),
                 bg=color, fg='#FFFFFF').pack(side=tk.RIGHT, pady=13)

        # Objektrader
        if items:
            item_frame = tk.Frame(section, bg=self.COLORS['surface'])
            item_frame.pack(fill=tk.X, padx=18, pady=16)

            for name, amount in items:
                row = tk.Frame(item_frame, bg=self.COLORS['surface_alt'])
                row.pack(fill=tk.X, pady=6, padx=10, ipady=8)

                # Vänster sida: Namn och belopp
                left_frame = tk.Frame(row, bg=self.COLORS['surface_alt'])
                left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

                tk.Label(left_frame, text=name, font=self.FONTS['body_bold'],
                         bg=self.COLORS['surface_alt'],
                         fg=self.COLORS['text']).pack(anchor=tk.W)

                # Höger sida: Belopp och åtgärdsknappar
                right_frame = tk.Frame(row, bg=self.COLORS['surface_alt'])
                right_frame.pack(side=tk.RIGHT)

                tk.Label(right_frame, text=f'{amount:,.0f} kr', font=('Segoe UI', 12, 'bold'),
                         bg=self.COLORS['surface_alt'],
                         fg=color).pack(side=tk.RIGHT, padx=(14, 0))

                # Redigera- och Ta bort-knappar
                if year and month:
                    # Hittar CSV-index för denna post
                    def make_edit_func(y, m, n, a):
                        def edit_func():
                            all_entries = self.budget.get_all_raw_entries()
                            for idx, entry in enumerate(all_entries):
                                if (int(entry['Year']) == y and
                                    int(entry['Month']) == m and
                                    entry['Description'] == n and
                                    float(entry['Amount']) == a):
                                    entry_data = {
                                        'Year': y,
                                        'Month': m,
                                        'Type': entry['Type'],
                                        'Description': n,
                                        'Amount': a
                                    }
                                    self.open_edit_entry_window(idx, entry_data)
                                    return
                        return edit_func

                    def make_delete_func(y, m, n, a):
                        def delete_func():
                            all_entries = self.budget.get_all_raw_entries()
                            for idx, entry in enumerate(all_entries):
                                if (int(entry['Year']) == y and
                                    int(entry['Month']) == m and
                                    entry['Description'] == n and
                                    float(entry['Amount']) == a):
                                    desc = entry['Description']
                                    amt = entry['Amount']
                                    msg = f'Delete: {desc} ({amt} kr)?\n\nThis cannot be undone.'
                                    if messagebox.askyesno('Confirm Delete', msg):
                                        self.budget.delete_entry(idx)
                                        self.refresh_data()
                                    return
                        return delete_func

                    # Ta bort-knapp
                    del_btn = tk.Label(right_frame, text='🗑️', font=('Segoe UI', 11),
                                      bg=self.COLORS['surface_alt'], fg=self.COLORS['danger'],
                                      cursor='hand2', padx=6)
                    del_btn.pack(side=tk.RIGHT)
                    del_btn.bind('<Button-1>', lambda e: make_delete_func(year, month, name, amount)())
                    del_btn.bind('<Enter>', lambda e: del_btn.config(fg=self.COLORS['primary_dark']))
                    del_btn.bind('<Leave>', lambda e: del_btn.config(fg=self.COLORS['danger']))

                    # Redigera-knapp
                    edit_btn = tk.Label(right_frame, text='✏️', font=('Segoe UI', 11),
                                       bg=self.COLORS['surface_alt'], fg=self.COLORS['warning'],
                                       cursor='hand2', padx=6)
                    edit_btn.pack(side=tk.RIGHT)
                    edit_btn.bind('<Button-1>', lambda e: make_edit_func(year, month, name, amount)())
                    edit_btn.bind('<Enter>', lambda e: edit_btn.config(fg=self.COLORS['primary_dark']))
                    edit_btn.bind('<Leave>', lambda e: edit_btn.config(fg=self.COLORS['warning']))

        # Knapp för att lägga till post längst ned om vi har år/månad-info
        if year and month:
            add_frame = tk.Frame(section, bg=self.COLORS['surface'])
            add_frame.pack(fill=tk.X, padx=18, pady=(8, 14))

            add_link = tk.Label(add_frame, text='+ Add New Entry', font=self.FONTS['small_bold'],
                               bg=self.COLORS['surface'], fg=self.COLORS['secondary'],
                               cursor='hand2')
            add_link.pack(anchor=tk.W)

            add_link.bind('<Button-1>', lambda e, y=year, m=month:
                         self.open_add_entry_window(y, m))
            add_link.bind('<Enter>', lambda e: add_link.config(fg=self.COLORS['accent']))
            add_link.bind('<Leave>', lambda e: add_link.config(fg=self.COLORS['secondary']))

    #  SKAPA BUDGETFÖNSTER

    def open_create_budget_window(self):
        # Öppnar modalt fönster för att skapa en ny månadsbudget
        win = tk.Toplevel(self.root)
        win.title('Create New Budget')
        win.geometry('560x800')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, True)

        self._modal_header(win, 'Create Monthly Budget', self.COLORS['primary'])

        # Rullningsbart formulär
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
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        # Periodssektion: År och månad
        self._form_section_label(content, '📅 When', top_pad=0)
        year_var  = self._form_field(content, 'Year',  str(datetime.now().year))
        month_var = self._form_field(content, 'Month', str(datetime.now().month))

        # Inkomstsektion: lön/inkomst
        self._form_section_label(content, '💰 Income')
        wage_desc_var   = self._form_field(content, 'Description')
        wage_amount_var = self._form_field(content, 'Amount (kr)')

        # Utgiftssektion: lista med kostnader
        self._form_section_label(content, '💳 Expenses')
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

        # Lägg till/Ta bort-knappar för utgifter
        self._form_list_buttons(content, add_expense, remove_expense,
                                self.COLORS['danger'])

        # Skuldssektion: lista med skulder/lån
        self._form_section_label(content, '⚠️  Debts')
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

        # Lägg till/Ta bort-knappar för skulder
        self._form_list_buttons(content, add_debt, remove_debt,
                                self.COLORS['warning'])

        # Skickar formuläret för att skapa budgeten
        def submit():
            try:
                # Validerar och extraherar formulärvärden
                year        = int(year_var.get())
                month       = int(month_var.get())
                wage_desc   = wage_desc_var.get().strip()
                wage_amount = float(wage_amount_var.get())

                # Säkerställer att inkomst är angiven
                if not wage_desc or wage_amount <= 0:
                    messagebox.showerror('Error', 'Enter a valid income', parent=win)
                    return

                # Lägger till inkomstpost i budgeten
                self.budget.add_entry(year, month, 'wage', wage_desc, wage_amount)

                # Lägger till alla utgiftsposter
                for item in exp_lb.get(0, tk.END):
                    desc, amt = item.rsplit(':', 1)
                    self.budget.add_entry(year, month, 'cost', desc.strip(),
                                         float(amt.strip().replace('kr', '').replace(',', '').strip()))

                # Lägger till alla skuldposter
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

        tk.Frame(content, bg=self.COLORS['bg'], height=12).pack()
        btn_frame = tk.Frame(content, bg=self.COLORS['bg'])
        btn_frame.pack(fill=tk.X)
        self._mk_btn(btn_frame, 'Create Budget', self.COLORS['success'], submit,
                     side=tk.LEFT, padx=(0, 8))
        self._mk_btn(btn_frame, 'Cancel', self.COLORS['text_light'], win.destroy,
                     side=tk.LEFT)

    #  REDIGERA BUDGETFÖNSTER
 
    def open_edit_budget_window(self, key):
        year, month = key.split('-')
        month_name = self.MONTH_NAMES.get(int(month), f'Month {month}')

        win = tk.Toplevel(self.root)
        win.title('Edit Budget')
        win.geometry('700x600')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(True, True)

        self._modal_header(win, f'Edit — {month_name} {year}', self.COLORS['secondary'])

        # Rullningsbart innehåll
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

        def safe_scroll_mouse(e):
            try:
                cv.yview_scroll(int(-1*(e.delta/120)), 'units')
            except:
                pass

        cv.bind('<MouseWheel>', safe_scroll_mouse)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(inner, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        # Informationsruta
        info_box = tk.Frame(content, bg=self.COLORS['primary_light'],
                           highlightbackground=self.COLORS['primary'],
                           highlightthickness=1)
        info_box.pack(fill=tk.X, pady=(0, 20))

        info_inner = tk.Frame(info_box, bg=self.COLORS['primary_light'])
        info_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(info_inner,
                 text='💡 Manage entries for this month. Click the buttons next to each entry to edit or delete.',
                 font=self.FONTS['body'], bg=self.COLORS['primary_light'],
                 fg=self.COLORS['primary'], wraplength=400, justify=tk.LEFT).pack(anchor=tk.W)

        # Visar poster för denna månad
        tk.Label(content, text='Entries', font=self.FONTS['subheading'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text']).pack(anchor=tk.W, pady=(12, 8))

        all_entries = self.budget.get_all_raw_entries()
        month_entries = [(idx, e) for idx, e in enumerate(all_entries)
                        if int(e['Year']) == int(year) and int(e['Month']) == int(month)]

        if month_entries:
            entries_frame = tk.Frame(content, bg=self.COLORS['surface'],
                                    highlightbackground=self.COLORS['border'],
                                    highlightthickness=1)
            entries_frame.pack(fill=tk.X, pady=(0, 16))

            for csv_idx, entry in month_entries:
                row = tk.Frame(entries_frame, bg=self.COLORS['surface_alt'])
                row.pack(fill=tk.X, padx=12, pady=6, ipady=8)

                # Postinformation
                left = tk.Frame(row, bg=self.COLORS['surface_alt'])
                left.pack(side=tk.LEFT, fill=tk.X, expand=True)

                type_label = self._translate_type(entry['Type'])
                tk.Label(left, text=f"{type_label}: {entry['Description']}",
                         font=self.FONTS['body_bold'],
                         bg=self.COLORS['surface_alt'],
                         fg=self.COLORS['text']).pack(anchor=tk.W)
                tk.Label(left, text=f"{entry['Amount']} kr",
                         font=self.FONTS['body'],
                         bg=self.COLORS['surface_alt'],
                         fg=self.COLORS['text_muted']).pack(anchor=tk.W)

                # Åtgärdsknappar
                right = tk.Frame(row, bg=self.COLORS['surface_alt'])
                right.pack(side=tk.RIGHT, padx=(12, 0))

                def make_delete_func(idx, e):
                    def delete_func():
                        msg = f"Delete: {e['Description']} ({e['Amount']} kr)?\n\nThis cannot be undone."
                        if messagebox.askyesno('Confirm Delete', msg):
                            self.budget.delete_entry(idx)
                            win.destroy()
                            self.refresh_data()
                    return delete_func

                def make_edit_func(idx, e):
                    def edit_func():
                        entry_data = {
                            'Year': int(e['Year']),
                            'Month': int(e['Month']),
                            'Type': e['Type'],
                            'Description': e['Description'],
                            'Amount': float(e['Amount'])
                        }
                        self.open_edit_entry_window(idx, entry_data)
                    return edit_func

                del_btn = tk.Button(right, text='🗑️ Delete', font=self.FONTS['small'],
                                   bg=self.COLORS['danger'], fg='#FFFFFF',
                                   relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
                                   command=make_delete_func(csv_idx, entry))
                del_btn.pack(side=tk.RIGHT, padx=(4, 0))

                edit_btn = tk.Button(right, text='✏️ Edit', font=self.FONTS['small'],
                                    bg=self.COLORS['warning'], fg='#FFFFFF',
                                    relief=tk.FLAT, padx=10, pady=4, cursor='hand2',
                                    command=make_edit_func(csv_idx, entry))
                edit_btn.pack(side=tk.RIGHT, padx=(0, 4))
        else:
            tk.Label(content, text='No entries for this month yet',
                     font=self.FONTS['body'],
                     bg=self.COLORS['bg'], fg=self.COLORS['text_muted']).pack(anchor=tk.W, pady=8)

        # Knappområde
        btn_frame = tk.Frame(content, bg=self.COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=(12, 0))

        self._mk_btn(btn_frame, '+ Add Entry', self.COLORS['primary'],
                     lambda: self.open_add_entry_window(int(year), int(month)),
                     side=tk.LEFT, padx=(0, 8))
        self._mk_btn(btn_frame, 'Close', self.COLORS['text_light'],
                     win.destroy, side=tk.LEFT)

    #  LÄGG TILL INMATNINGSFÖNSTER

    def open_add_entry_window(self, year=None, month=None):
        win = tk.Toplevel(self.root)
        win.title('Add Entry')
        win.geometry('480x460')
        win.configure(bg=self.COLORS['bg'])
        win.resizable(False, False)

        self._modal_header(win, 'Add Budget Entry', self.COLORS['secondary'])

        content = tk.Frame(win, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        # Förifylls med år/månad om det finns angivet
        default_year = str(year) if year else str(datetime.now().year)
        default_month = str(month) if month else str(datetime.now().month)

        year_var    = self._form_field(content, 'Year',   default_year)
        month_var   = self._form_field(content, 'Month',  default_month)
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

    #  ÅTERANVÄNDBAR FORMULÄRHJÄLPAR

    def _modal_header(self, win, text, color):
        # Skapar en färgad rubrik för modala fönster
        hdr = tk.Frame(win, bg=color, height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=text, font=self.FONTS['heading'],
                 bg=color, fg='#FFFFFF').pack(side=tk.LEFT, padx=28, pady=22)

    def _form_section_label(self, parent, text, top_pad=16):
        # Skapar en sektionsetikett med en avdelarlinje
        tk.Frame(parent, bg=self.COLORS['border'], height=1).pack(fill=tk.X, pady=(top_pad, 14))
        tk.Label(parent, text=text, font=self.FONTS['subheading'],
                 bg=self.COLORS['bg'], fg=self.COLORS['primary']).pack(anchor=tk.W, pady=(0, 12))

    def _form_field(self, parent, label, default='', combo=False):
        # Skapar ett etiketterat formulärfält (textinmatning eller rullgardinsmeny)
        row = tk.Frame(parent, bg=self.COLORS['bg'])
        row.pack(fill=tk.X, pady=12)

        # Skapar etiketttext
        tk.Label(row, text=label, font=self.FONTS['small_bold'],
                 bg=self.COLORS['bg'], fg=self.COLORS['text'],
                 width=18, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 16), pady=(2, 0))

        var = tk.StringVar(value=default)
        if combo:
            # Skapar rullgardinslista
            widget = ttk.Combobox(row, textvariable=var,
                                  values=['wage', 'cost', 'debt'],
                                  state='readonly', font=self.FONTS['body'])
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        else:
            # Skapar textinmatningsfält
            widget = tk.Entry(row, textvariable=var, font=self.FONTS['body'],
                              bg=self.COLORS['surface'], fg=self.COLORS['text'],
                              relief=tk.FLAT, bd=0,
                              highlightbackground=self.COLORS['border'],
                              highlightthickness=1,
                              insertbackground=self.COLORS['primary'])

            # Fokuseffekt: ändrar kantfärg när fältet klickas
            def _focus_in(e):
                widget.config(highlightbackground=self.COLORS['primary'],
                              highlightthickness=2)
            def _focus_out(e):
                widget.config(highlightbackground=self.COLORS['border'],
                              highlightthickness=1)
            widget.bind('<FocusIn>',  _focus_in)
            widget.bind('<FocusOut>', _focus_out)

            widget.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9)

        return var

    def _form_listbox(self, parent):
        # Skapar en stiliserad listbox för att visa flera objekt
        lb = tk.Listbox(parent, height=5, font=self.FONTS['body'],
                        bg=self.COLORS['surface'], fg=self.COLORS['text'],
                        selectbackground=self.COLORS['primary_light'],
                        selectforeground=self.COLORS['primary'],
                        relief=tk.FLAT, bd=0,
                        highlightbackground=self.COLORS['border'],
                        highlightthickness=1,
                        activestyle='none')
        lb.pack(fill=tk.X, pady=(0, 8))
        return lb

    def _form_list_buttons(self, parent, add_cmd, remove_cmd, add_color):
        # Skapar Lägg till/Ta bort-knappar för listboxobjekt
        row = tk.Frame(parent, bg=self.COLORS['bg'])
        row.pack(fill=tk.X, pady=(6, 12))
        # Lägg till-knapp med anpassad färg
        self._mk_btn(row, '+ Add', add_color, add_cmd, side=tk.LEFT, padx=(0, 8))
        # Ta bort-knapp med neutral färg
        self._mk_btn(row, '− Remove', self.COLORS['text_light'], remove_cmd, side=tk.LEFT)

    #  ARVET SHIM (behålls så ingenting bryter utanför)

    def create_summary_row(self, parent, label, value, color):
        # Ärvd metod – omslag för _card_row för bakåtkompatibilitet
        self._card_row(parent, label, 0, color, self.COLORS['surface'])

    def translate_type(self, type_str):
        # Ärvd metod – omslag för _translate_type för bakåtkompatibilitet
        return self._translate_type(type_str)