import customtkinter as ctk
import Database as db
from create_election import CreateElectionPage
from Manage import ManagePage
from Results import ResultsPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK_NAVY= "#0F1117"
NAVY= "#1A1D27"
SPACE_CADET= "#22263A"
BLUE= "#4F6EF7"
DARK_BLUE= "#3A56D4"
WHITE= "#F0F2FF"
GRAY="#8B90A7"
DARK_GRAY= "#2A2F45"
GREEN = "#22C77A"
YELLOW = "#F5A623"
RED= "#F75A5A"


class Homepage(ctk.CTkFrame):
    def __init__(self, parent, switch_page_callback):
        super().__init__(parent, fg_color="transparent")
        self.switch_page = switch_page_callback
        self.build()

    def build(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        counts = db.get_counts()
        elections = db.list_elections()

        top_section = ctk.CTkFrame(scroll, fg_color=NAVY, corner_radius=18)
        top_section.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 14))
        top_section.grid_columnconfigure(0, weight=1)
        top_section.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(top_section, text="ELECTION SOFTWARE",font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),text_color=BLUE, fg_color=SPACE_CADET, corner_radius=8,).grid(row=0, column=0, padx=24, pady=(22, 8), sticky="w")
        ctk.CTkLabel(top_section, text="Welcome back",font=ctk.CTkFont(size=32, weight="bold"),text_color=WHITE, anchor="w",).grid(row=1, column=0, padx=24, pady=(0, 6), sticky="w")
        ctk.CTkLabel(top_section,text="Create elections, add candidates, manage voters,\nand monitor results - all in one place.",font=ctk.CTkFont(size=14), text_color=GRAY, anchor="w", justify="left",).grid(row=2, column=0, padx=24, pady=(0, 18), sticky="w")

        top_buttons = ctk.CTkFrame(top_section, fg_color="transparent")
        top_buttons.grid(row=1, column=1, rowspan=2, padx=24, pady=(8, 18), sticky="e")
        top_buttons.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(top_buttons, text="Create election",fg_color=BLUE, hover_color=DARK_BLUE,text_color=WHITE, height=40, corner_radius=10,font=ctk.CTkFont(size=13, weight="bold"),command=lambda: self.switch_page("create"),).grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(top_buttons, text="View results",fg_color=SPACE_CADET, hover_color=DARK_GRAY,text_color=WHITE, height=40, corner_radius=10,font=ctk.CTkFont(size=13, weight="bold"),command=lambda: self.switch_page("results"),).grid(row=1, column=0, sticky="ew")

        counts_row = ctk.CTkFrame(scroll, fg_color="transparent")
        counts_row.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 16))
        for i in range(3):
            counts_row.grid_columnconfigure(i, weight=1)

        def make_count_card(parent, col, label, value, color):
            card = ctk.CTkFrame(parent, fg_color=NAVY, corner_radius=14)
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 12, 0))
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0).grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12, weight="bold"),text_color=GRAY, anchor="w").grid(row=1, column=0, padx=16, pady=(14, 2), sticky="w")
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=26, weight="bold"),text_color=WHITE, anchor="w").grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

        make_count_card(counts_row, 0, "Elections", counts.get("elections", 0), BLUE)
        make_count_card(counts_row, 1, "Candidates", counts.get("candidates", 0), GREEN)
        make_count_card(counts_row, 2, "Voters", counts.get("voters", 0), YELLOW)

        recent_section = ctk.CTkFrame(scroll, fg_color=NAVY, corner_radius=18)
        recent_section.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 16))
        recent_section.grid_columnconfigure(0, weight=1)

        recent_header = ctk.CTkFrame(recent_section, fg_color="transparent")
        recent_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        recent_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(recent_header, text="Recent elections",font=ctk.CTkFont(size=18, weight="bold"),text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(recent_header, text="Refresh",fg_color=SPACE_CADET, hover_color=DARK_GRAY,text_color=GRAY, height=32, corner_radius=10,font=ctk.CTkFont(size=12, weight="bold"),command=self.build,).grid(row=0, column=1, sticky="e")

        elections_list = ctk.CTkFrame(recent_section, fg_color="transparent")
        elections_list.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        elections_list.grid_columnconfigure(0, weight=1)

        if not elections:
            ctk.CTkLabel(elections_list,text="No elections yet. Create your first election to get started.",font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        else:
            for i, e in enumerate(elections):
                election_row = ctk.CTkFrame(elections_list, fg_color=SPACE_CADET, corner_radius=12)
                election_row.grid(row=i, column=0, sticky="ew", pady=6)
                election_row.grid_columnconfigure(0, weight=1)

                name = e.get("e_name", "Untitled")
                desc = e.get("description")
                if desc:
                    desc = desc.strip()
                else:
                    desc = "No description"
                created = e.get("created_at").strip()

                ctk.CTkLabel(election_row, text=name,font=ctk.CTkFont(size=14, weight="bold"),text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
                ctk.CTkLabel(election_row,text=desc if len(desc) <= 90 else desc[:87] + "...",font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w", justify="left").grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
                ctk.CTkLabel(election_row, text=created,font=ctk.CTkFont(size=11, weight="bold"), text_color=GRAY).grid(row=0, column=1, rowspan=2, sticky="e", padx=14)

        ctk.CTkLabel(scroll, text="Quick actions",font=ctk.CTkFont(size=18, weight="bold"),text_color=WHITE, anchor="w").grid(row=3, column=0, padx=32, pady=(0, 10), sticky="w")
        actions_row = ctk.CTkFrame(scroll, fg_color="transparent")
        actions_row.grid(row=4, column=0, sticky="ew", padx=32, pady=(0, 32))
        for i in range(3):
            actions_row.grid_columnconfigure(i, weight=1)

        actions = [("Results", "Live results and vote counts.", "results", BLUE, "Open"),("Create election", "Start a new election in 3 steps.", "create", GREEN, "Create"),("Manage", "Edit elections, candidates and voters.", "manage", YELLOW, "Manage"),]

        for i, (title, description, page, color, btn_label) in enumerate(actions):
            action_card = ctk.CTkFrame(actions_row, fg_color=NAVY, corner_radius=16)
            action_card.grid(row=0, column=i, padx=(0 if i == 0 else 12, 0), sticky="nsew")
            action_card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(action_card, text=title,font=ctk.CTkFont(size=16, weight="bold"),text_color=WHITE, anchor="w").grid(row=0, column=0, padx=18, pady=(16, 6), sticky="w")
            ctk.CTkLabel(action_card, text=description,font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w", justify="left").grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")
            ctk.CTkButton(action_card, text=btn_label,font=ctk.CTkFont(size=13, weight="bold"),fg_color=SPACE_CADET, hover_color=DARK_GRAY, text_color=color,corner_radius=10, height=38,command=lambda p=page: self.switch_page(p),).grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        db.init_db()
        self.title("Election Software")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=DARK_NAVY)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.pages = {}
        self.current_page = None
        self.show_page("home")

    def build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=NAVY, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(sidebar, text="ELECTION SOFTWARE",font=ctk.CTkFont(family="Courier New", size=18, weight="bold"),text_color=BLUE,).grid(row=0, column=0, padx=24, pady=(28, 32))

        nav_items = [("Home", "home"), ("Results", "results"), ("Create election", "create"), ("Manage", "manage"),]
        self.nav_buttons = {}
        for i, (label, page) in enumerate(nav_items):
            btn = ctk.CTkButton(sidebar, text=label,font=ctk.CTkFont(size=13),fg_color="transparent", hover_color=SPACE_CADET,text_color=GRAY, anchor="w",height=40, corner_radius=8,command=lambda p=page: self.show_page(p),)
            btn.grid(row=i + 1, column=0, padx=12, pady=2, sticky="ew")
            self.nav_buttons[page] = btn

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.grid_forget()

        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color=SPACE_CADET, text_color=WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=GRAY)

        if page_name == "create":
            if "create" in self.pages:
                self.pages["create"].reset()
            else:
                self.pages["create"] = CreateElectionPage(self, self.show_page)

        elif page_name == "home":
            if "home" in self.pages:
                self.pages["home"].build()
            else:
                self.pages["home"] = Homepage(self, self.show_page)

        elif page_name == "manage":
            if "manage" in self.pages:
                self.pages["manage"].refresh()
            else:
                self.pages["manage"] = ManagePage(self, self.show_page)

        elif page_name == "results":
            if "results" in self.pages:
                self.pages["results"].refresh()
            else:
                self.pages["results"] = ResultsPage(self, self.show_page)

        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=1, sticky="nsew")
            self.current_page = self.pages[page_name]


if __name__ == "__main__":
    import threading
    from webpage import app as flask_app

    flask_thread = threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()

    app = App()
    app.mainloop()