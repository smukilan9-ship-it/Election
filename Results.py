import customtkinter as ctk
import Database as db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DARK_NAVY = "#0F1117"
NAVY = "#1A1D27"
SPACE_CADET = "#22263A"
BLUE = "#4F6EF7"
DARK_BLUE = "#3A56D4"
WHITE = "#F0F2FF"
GRAY = "#8B90A7"
DARK_GRAY = "#2A2F45"
GREEN = "#22C77A"
YELLOW = "#F5A623"
RED = "#F75A5A"
SPORT = "#00ffb7"


class ResultsPage(ctk.CTkFrame):
    def __init__(self, parent, switch_page_callback):
        super().__init__(parent, fg_color="transparent")
        self.switch_page = switch_page_callback
        self.selected_election_id = None
        self.elections_map = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.build_header()
        self.build_body()
        self.refresh()

    def build_header(self):
        page_header = ctk.CTkFrame(self, fg_color="transparent")
        page_header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 12))
        page_header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(page_header, text="Results", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w")
        self.election_dropdown_var = ctk.StringVar(value="")
        self.election_dropdown = ctk.CTkOptionMenu(page_header, variable=self.election_dropdown_var, values=["No elections"], fg_color=SPACE_CADET, button_color=SPACE_CADET, button_hover_color=DARK_GRAY, text_color=WHITE, width=240,
                                                   command=self.on_election_select)
        self.election_dropdown.grid(row=0, column=1, padx=(24, 0), sticky="w")
        ctk.CTkButton(page_header, text="Refresh", fg_color=SPACE_CADET, hover_color=DARK_GRAY, text_color=GRAY, height=34, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=self.refresh).grid(row=0, column=2, sticky="e",
                                                                                                                                                                                                                   padx=(12, 0))

    def build_body(self):
        self.results_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_scroll.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 24))
        self.results_scroll.grid_columnconfigure(0, weight=1)

    def refresh(self):
        elections = db.list_elections()
        if not elections:
            self.election_dropdown.configure(values=["No elections"])
            self.election_dropdown_var.set("No elections")
            self.selected_election_id = None
            self.render_empty()
            return

        dropdown_labels = [f"{e['e_name']}  (ID: {e['election_id']})" for e in elections]
        self.election_dropdown.configure(values=dropdown_labels)
        self.elections_map = {f"{e['e_name']}  (ID: {e['election_id']})": e["election_id"] for e in elections}

        if self.selected_election_id is None:
            self.selected_election_id = elections[0]["election_id"]

        matching = [e for e in elections if e["election_id"] == self.selected_election_id]
        if matching:
            self.election_dropdown_var.set(f"{matching[0]['e_name']}  (ID: {matching[0]['election_id']})")
        else:
            self.selected_election_id = elections[0]["election_id"]
            self.election_dropdown_var.set(dropdown_labels[0])

        self.render_results()

    def on_election_select(self, value):
        if value in self.elections_map:
            self.selected_election_id = self.elections_map[value]
            self.render_results()

    def render_empty(self):
        for w in self.results_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.results_scroll, text="No elections found. Create one to see results here.", font=ctk.CTkFont(size=14), text_color=GRAY, anchor="w").grid(row=0, column=0, sticky="w", padx=8, pady=8)

    def render_results(self):
        for w in self.results_scroll.winfo_children():
            w.destroy()

        if not self.selected_election_id:
            self.render_empty()
            return

        data = db.get_results_for_election(self.selected_election_id)
        results = data["results"]
        total_votes = data["total_votes"]
        total_voters = data["total_voters"]

        if total_voters > 0:
            turnout_pct = round((total_votes / total_voters) * 100)
        else:
            turnout_pct = 0

        summary_row = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
        summary_row.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for i in range(3):
            summary_row.grid_columnconfigure(i, weight=1)

        self.make_summary_card(summary_row, 0, "Voters registered", str(total_voters), BLUE)
        self.make_summary_card(summary_row, 1, "Votes cast", str(total_votes), GREEN)
        self.make_summary_card(summary_row, 2, "Turnout", f"{turnout_pct}%", YELLOW)

        if not results:
            ctk.CTkLabel(self.results_scroll, text="No candidates or votes yet for this election.", font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w").grid(row=1, column=0, sticky="w", padx=8, pady=8)
            return

        kutumba_colors = {"Atri": "#E05555", "Gautama": "#22C77A", "Kashyappa": "#4F6EF7", "Vashista": "#F5C842"}
        kutumba_order = ["Atri", "Gautama", "Kashyappa", "Vashista"]

        by_kutumba = {}
        sports_roles = {}

        for role, candidates in results.items():
            if "Sports Captain" in role:
                sports_roles[role] = candidates
            else:
                for c in candidates:
                    k = c["kutumba"] or "Unknown"
                    if k not in by_kutumba:
                        by_kutumba[k] = {}
                    if role not in by_kutumba[k]:
                        by_kutumba[k][role] = []
                    by_kutumba[k][role].append(c)

        current_row = 1

        for kutumba in kutumba_order:
            if kutumba not in by_kutumba:
                continue

            color = kutumba_colors.get(kutumba, SPORT)
            kutumba_roles = by_kutumba[kutumba]

            kutumba_section = ctk.CTkFrame(self.results_scroll, fg_color=NAVY, corner_radius=16)
            kutumba_section.grid(row=current_row, column=0, sticky="ew", pady=(0, 16))
            kutumba_section.grid_columnconfigure(0, weight=1)
            current_row += 1

            ctk.CTkFrame(kutumba_section, fg_color=color, height=4, corner_radius=0).grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(kutumba_section, text=kutumba, font=ctk.CTkFont(size=16, weight="bold"), text_color=color, anchor="w").grid(row=1, column=0, sticky="w", padx=18, pady=(12, 8))

            inner_row = 2
            for role, candidates in sorted(kutumba_roles.items()):
                ctk.CTkLabel(kutumba_section, text=role, font=ctk.CTkFont(size=12, weight="bold"), text_color=GRAY, anchor="w").grid(row=inner_row, column=0, sticky="w", padx=18, pady=(8, 4))
                inner_row += 1

                max_votes_for_role = max((c["votes"] for c in candidates), default=1)
                total_votes_for_role = sum(c["votes"] for c in candidates)

                for c in candidates:
                    is_leading = c["votes"] == max_votes_for_role and max_votes_for_role > 0

                    if max_votes_for_role > 0:
                        bar_fill_pct = c["votes"] / max_votes_for_role
                    else:
                        bar_fill_pct = 0

                    if total_votes_for_role > 0:
                        vote_pct = round((c["votes"] / total_votes_for_role) * 100)
                    else:
                        vote_pct = 0

                    candidate_row = ctk.CTkFrame(kutumba_section, fg_color=SPACE_CADET, corner_radius=10)
                    candidate_row.grid(row=inner_row, column=0, sticky="ew", padx=14, pady=4)
                    candidate_row.grid_columnconfigure(1, weight=1)
                    inner_row += 1

                    ctk.CTkLabel(candidate_row, text=c["name"], font=ctk.CTkFont(size=13, weight="bold" if is_leading else "normal"), text_color=color if is_leading else WHITE, anchor="w", width=200).grid(row=0, column=0, padx=(14, 8), pady=(10, 4),
                                                                                                                                                                                                             sticky="w")

                    bar_background = ctk.CTkFrame(candidate_row, fg_color=DARK_GRAY, height=10, corner_radius=5)
                    bar_background.grid(row=0, column=1, padx=(0, 8), pady=(10, 4), sticky="ew")
                    bar_background.grid_propagate(False)

                    if bar_fill_pct > 0:
                        bar_fill = ctk.CTkFrame(bar_background, fg_color=color, height=10, corner_radius=5)
                        bar_background.update_idletasks()
                        bar_fill.place(relx=0, rely=0, relwidth=bar_fill_pct, relheight=1.0)

                    ctk.CTkLabel(candidate_row, text=f"{c['votes']} votes  ({vote_pct}%)", font=ctk.CTkFont(size=12), text_color=color if is_leading else GRAY, anchor="e", width=120).grid(row=0, column=2, padx=(0, 14), pady=(10, 4), sticky="e")
                    ctk.CTkLabel(candidate_row, text="Leading" if is_leading and c["votes"] > 0 else "", font=ctk.CTkFont(size=10, weight="bold"), text_color=color, anchor="w").grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

            ctk.CTkFrame(kutumba_section, fg_color="transparent", height=8).grid(row=inner_row, column=0)

        for role, candidates in sorted(sports_roles.items()):
            color = SPORT
            sports_section = ctk.CTkFrame(self.results_scroll, fg_color=NAVY, corner_radius=16)
            sports_section.grid(row=current_row, column=0, sticky="ew", pady=(0, 16))
            sports_section.grid_columnconfigure(0, weight=1)
            current_row += 1

            ctk.CTkFrame(sports_section, fg_color=color, height=4, corner_radius=0).grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(sports_section, text=role, font=ctk.CTkFont(size=16, weight="bold"), text_color=WHITE, anchor="w").grid(row=1, column=0, sticky="w", padx=18, pady=(12, 12))

            max_votes_for_role = max((c["votes"] for c in candidates), default=1)
            total_votes_for_role = sum(c["votes"] for c in candidates)

            for ci, c in enumerate(candidates):
                is_leading = c["votes"] == max_votes_for_role and max_votes_for_role > 0

                if max_votes_for_role > 0:
                    bar_fill_pct = c["votes"] / max_votes_for_role
                else:
                    bar_fill_pct = 0

                if total_votes_for_role > 0:
                    vote_pct = round((c["votes"] / total_votes_for_role) * 100)
                else:
                    vote_pct = 0

                candidate_row = ctk.CTkFrame(sports_section, fg_color=SPACE_CADET, corner_radius=10)
                candidate_row.grid(row=2 + ci, column=0, sticky="ew", padx=14, pady=4)
                candidate_row.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(candidate_row, text=c["name"], font=ctk.CTkFont(size=13, weight="bold" if is_leading else "normal"), text_color=color if is_leading else WHITE, anchor="w", width=200).grid(row=0, column=0, padx=(14, 8), pady=(10, 4),
                                                                                                                                                                                                         sticky="w")

                bar_background = ctk.CTkFrame(candidate_row, fg_color=DARK_GRAY, height=10, corner_radius=5)
                bar_background.grid(row=0, column=1, padx=(0, 8), pady=(10, 4), sticky="ew")
                bar_background.grid_propagate(False)

                if bar_fill_pct > 0:
                    bar_fill = ctk.CTkFrame(bar_background, fg_color=color, height=10, corner_radius=5)
                    bar_background.update_idletasks()
                    bar_fill.place(relx=0, rely=0, relwidth=bar_fill_pct, relheight=1.0)

                ctk.CTkLabel(candidate_row, text=f"{c['votes']} votes  ({vote_pct}%)", font=ctk.CTkFont(size=12), text_color=color if is_leading else GRAY, anchor="e", width=120).grid(row=0, column=2, padx=(0, 14), pady=(10, 4), sticky="e")
                ctk.CTkLabel(candidate_row, text="Leading" if is_leading and c["votes"] > 0 else "", font=ctk.CTkFont(size=10, weight="bold"), text_color=color, anchor="w").grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

            ctk.CTkFrame(sports_section, fg_color="transparent", height=8).grid(row=len(candidates) + 2, column=0)

    def make_summary_card(self, parent, col, label, value, color):
        card = ctk.CTkFrame(parent, fg_color=NAVY, corner_radius=14)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 12, 0))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=GRAY, anchor="w").grid(row=1, column=0, padx=16, pady=(14, 2), sticky="w")
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color=WHITE, anchor="w").grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")