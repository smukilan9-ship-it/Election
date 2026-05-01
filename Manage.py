import customtkinter as ctk
import Database as db
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import pandas as pd
import socket

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


class ManagePage(ctk.CTkFrame):
    def __init__(self, parent, switch_page_callback):
        super().__init__(parent, fg_color="transparent")
        self.switch_page = switch_page_callback
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.elections = []
        self.selected_election_id = None
        self.active_tab = "candidates"
        self.voting_link = ""
        self.build()
        self.refresh()

    def build(self):
        page_header = ctk.CTkFrame(self, fg_color="transparent")
        page_header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 12))
        page_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(page_header, text="Manage", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(page_header, text="Refresh", fg_color=SPACE_CADET, hover_color=DARK_GRAY, text_color=GRAY, height=34, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=self.refresh).grid(row=0, column=1, sticky="e")

        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 24))
        main_area.grid_columnconfigure(0, weight=0)
        main_area.grid_columnconfigure(1, weight=1)
        main_area.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(main_area, fg_color=NAVY, corner_radius=18, width=320)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_panel.grid_propagate(False)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left_panel, text="Elections", font=ctk.CTkFont(size=16, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        self.election_list = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.election_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.election_list.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(left_panel, text="Create election", fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, height=38, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=lambda: self.switch_page("create")).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        right_panel = ctk.CTkFrame(main_area, fg_color=NAVY, corner_radius=18)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(4, weight=1)
        self.right_panel = right_panel

        name_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        name_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 2))
        name_row.grid_columnconfigure(0, weight=1)

        self.election_name_label = ctk.CTkLabel(name_row, text="Select an election", font=ctk.CTkFont(size=18, weight="bold"), text_color=WHITE, anchor="w")
        self.election_name_label.grid(row=0, column=0, sticky="w")
        self.election_id_label = ctk.CTkLabel(name_row, text="", font=ctk.CTkFont(family="Courier New", size=12, weight="bold"), text_color=BLUE, fg_color=SPACE_CADET, corner_radius=8)
        self.election_id_label.grid(row=0, column=1, sticky="e", padx=(8, 0))
        self.election_info_label = ctk.CTkLabel(right_panel, text="", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w", justify="left")
        self.election_info_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 4))

        self.link_row = ctk.CTkFrame(right_panel, fg_color=SPACE_CADET, corner_radius=10)
        self.link_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.link_row.grid_columnconfigure(0, weight=1)
        self.link_label = ctk.CTkLabel(self.link_row, text="", font=ctk.CTkFont(family="Courier New", size=11), text_color=BLUE, anchor="w")
        self.link_label.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        self.copy_button = ctk.CTkButton(self.link_row, text="Copy", width=60, height=26, corner_radius=6, font=ctk.CTkFont(size=11, weight="bold"), fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, command=self.copy_link)
        self.copy_button.grid(row=0, column=1, padx=(0, 8), pady=8)

        tabs_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        tabs_row.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 8))
        self.candidates_tab_btn = ctk.CTkButton(tabs_row, text="Candidates", width=120, height=32, corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"), fg_color=SPACE_CADET, text_color=WHITE, command=lambda: self.switch_tab("candidates"))
        self.candidates_tab_btn.grid(row=0, column=0, padx=(0, 6))
        self.voters_tab_btn = ctk.CTkButton(tabs_row, text="Voters", width=120, height=32, corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"), fg_color="transparent", text_color=GRAY, command=lambda: self.switch_tab("voters"))
        self.voters_tab_btn.grid(row=0, column=1)

        self.tab_content = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.tab_content.grid(row=4, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)

        bottom_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        bottom_row.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 16))
        bottom_row.grid_columnconfigure(0, weight=1)
        self.delete_election_btn = ctk.CTkButton(bottom_row, text="Delete election", fg_color="transparent", hover_color=DARK_GRAY, text_color=RED, border_width=1, border_color=DARK_GRAY, height=36, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=self.delete_selected_election, state="disabled")
        self.delete_election_btn.grid(row=0, column=1, sticky="e")

    def switch_tab(self, tab):
        self.active_tab = tab
        if tab == "candidates":
            self.candidates_tab_btn.configure(fg_color=SPACE_CADET, text_color=WHITE)
            self.voters_tab_btn.configure(fg_color="transparent", text_color=GRAY)
        else:
            self.voters_tab_btn.configure(fg_color=SPACE_CADET, text_color=WHITE)
            self.candidates_tab_btn.configure(fg_color="transparent", text_color=GRAY)
        self.refresh_details()

    def refresh(self):
        for w in self.election_list.winfo_children():
            w.destroy()

        self.elections = db.list_elections()
        if not self.elections:
            ctk.CTkLabel(self.election_list, text="No elections yet.", font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w").grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        else:
            for i, e in enumerate(self.elections):
                eid = e.get("election_id")
                name = e.get("e_name", "Untitled")
                created = e.get("created_at", "").strip()
                is_sel = (eid == self.selected_election_id)
                ctk.CTkButton(self.election_list, text=f"{name}\n{created}" if created else name, fg_color=SPACE_CADET if is_sel else "transparent", hover_color=SPACE_CADET, text_color=WHITE if is_sel else GRAY, anchor="w", height=54, corner_radius=12, font=ctk.CTkFont(size=12, weight="bold" if is_sel else "normal"), command=lambda x=eid: self.select_election(x)).grid(row=i, column=0, sticky="ew", pady=6)

        if self.selected_election_id is None and self.elections:
            self.selected_election_id = self.elections[0].get("election_id")
        self.refresh_details()

    def select_election(self, election_id):
        self.selected_election_id = election_id
        self.refresh()

    def copy_link(self):
        self.clipboard_clear()
        self.clipboard_append(self.voting_link)
        self.copy_button.configure(text="Copied")
        self.after(2000, lambda: self.copy_button.configure(text="Copy"))

    def refresh_details(self):
        for w in self.tab_content.winfo_children():
            w.destroy()

        if not self.selected_election_id:
            self.election_name_label.configure(text="Select an election")
            self.election_id_label.configure(text="")
            self.election_info_label.configure(text="")
            self.link_row.grid_remove()
            self.delete_election_btn.configure(state="disabled")
            return

        e = db.get_election(self.selected_election_id)
        if not e:
            self.selected_election_id = None
            self.refresh()
            return

        name = e.get("e_name", "Untitled")
        desc = e.get("description")
        if desc:
            desc = desc.strip()
        created = e.get("created_at").strip()

        self.election_name_label.configure(text=name)
        self.election_id_label.configure(text=f"  ID: {self.selected_election_id}  ")

        info_parts = [f"Created: {created}"]
        if desc:
            info_parts.append(f"Description: {desc}")
        self.election_info_label.configure(text="  .  ".join(info_parts))

        local_ip = socket.gethostbyname(socket.gethostname())
        self.voting_link = f"http://{local_ip}:5001/login?election_id={self.selected_election_id}"
        self.link_label.configure(text=self.voting_link)
        self.link_row.grid()
        self.delete_election_btn.configure(state="normal")

        if self.active_tab == "candidates":
            self.render_candidates()
        else:
            self.render_voters()

    def render_candidates(self):
        candidates_scroll = ctk.CTkScrollableFrame(self.tab_content, fg_color="transparent")
        candidates_scroll.grid(row=0, column=0, sticky="nsew")
        candidates_scroll.grid_columnconfigure(0, weight=1)

        candidates = db.list_candidates(self.selected_election_id)
        if not candidates:
            ctk.CTkLabel(candidates_scroll, text="No candidates for this election.", font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w").grid(row=0, column=0, sticky="ew", padx=6, pady=6)
            return

        for i, c in enumerate(candidates):
            candidate_card = ctk.CTkFrame(candidates_scroll, fg_color=SPACE_CADET, corner_radius=14)
            candidate_card.grid(row=i, column=0, sticky="ew", padx=6, pady=6)
            candidate_card.grid_columnconfigure(0, weight=1)

            name = c.get("name", "-")
            role = c.get("role", "-")
            kutumba = c.get("kutumba", "").strip() or "-"
            id_no = c.get("id_no", "-")

            ctk.CTkLabel(candidate_card, text=f"{name}  .  {role}  .  {kutumba}", font=ctk.CTkFont(size=13, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
            ctk.CTkLabel(candidate_card, text=f"ID: {id_no}", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
            ctk.CTkButton(candidate_card, text="Delete", fg_color="transparent", hover_color=DARK_GRAY, text_color=RED, border_width=1, border_color=DARK_GRAY, height=32, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=lambda cid=c.get("id"): self.delete_candidate(cid)).grid(row=0, column=1, rowspan=2, sticky="e", padx=14)

    def render_voters(self):
        voters_area = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        voters_area.grid(row=0, column=0, sticky="nsew")
        voters_area.grid_columnconfigure(0, weight=1)
        voters_area.grid_rowconfigure(1, weight=1)

        voters_header = ctk.CTkFrame(voters_area, fg_color="transparent")
        voters_header.grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 8))
        voters_header.grid_columnconfigure(0, weight=1)

        voters = db.list_voters_for_election(self.selected_election_id)

        ctk.CTkLabel(voters_header, text=f"{len(voters)} voter{'s' if len(voters) != 1 else ''} for this election.", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(voters_header, text="Import voters", fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, height=32, corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"), command=self.import_voters).grid(row=0, column=1, sticky="e")

        voters_scroll = ctk.CTkScrollableFrame(voters_area, fg_color="transparent")
        voters_scroll.grid(row=1, column=0, sticky="nsew")
        voters_scroll.grid_columnconfigure(0, weight=1)

        if not voters:
            ctk.CTkLabel(voters_scroll, text="No voters imported yet. Use the import button to load a CSV or Excel file.", font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w", justify="left").grid(row=0, column=0, sticky="ew", padx=6, pady=6)
            return

        for i, v in enumerate(voters):
            voter_card = ctk.CTkFrame(voters_scroll, fg_color=SPACE_CADET, corner_radius=10)
            voter_card.grid(row=i, column=0, sticky="ew", padx=6, pady=4)
            voter_card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(voter_card, text=f"{v['id_no']}  .  {v['kutumba'] or '-'}", font=ctk.CTkFont(size=13), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=8)
            ctk.CTkButton(voter_card, text="Remove", fg_color="transparent", hover_color=DARK_GRAY, text_color=RED, border_width=1, border_color=DARK_GRAY, height=28, corner_radius=8, font=ctk.CTkFont(size=11, weight="bold"), command=lambda vid=v['id']: self.remove_voter(vid)).grid(row=0, column=1, sticky="e", padx=10)

    def import_voters(self):
        path = fd.askopenfilename(title="Select voters file", filetypes=[("CSV / Excel", "*.csv *.xlsx *.xls"), ("All files", "*.*")])
        if not path:
            return

        if path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)

        df.columns = [c.strip().lower() for c in df.columns]
        missing = [c for c in ("id_no", "kutumba") if c not in df.columns]
        if missing:
            mb.showerror("Missing columns", f"File is missing: {', '.join(missing)}")
            return

        voter_rows = df[["id_no", "kutumba"]].to_dict(orient="records")
        imported, skipped = db.import_voters_for_election(self.selected_election_id, voter_rows)
        mb.showinfo("Import complete", f"Imported: {imported}   Skipped: {skipped}")
        self.refresh_details()

    def remove_voter(self, voter_id):
        db.remove_voter_from_election(self.selected_election_id, voter_id)
        self.refresh_details()

    def delete_candidate(self, candidate_id):
        db.delete_candidate(candidate_id)
        self.refresh_details()

    def delete_selected_election(self):
        if not self.selected_election_id:
            return
        db.delete_election(self.selected_election_id)
        self.selected_election_id = None
        self.refresh()