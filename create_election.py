import customtkinter as ctk
import Database as db
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import pandas as pd

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


class CreateElectionPage(ctk.CTkFrame):
    def __init__(self, parent, switch_page_callback):
        super().__init__(parent, fg_color="transparent")
        self.switch_page = switch_page_callback
        self.election_id = None
        self.voter_import_count = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.step_frames = {}
        self.build_steps()
        self.show_step(0)

    def reset(self):
        self.election_id = None
        self.voter_import_count = 0
        for fr in self.step_frames.values():
            fr.destroy()
        self.step_frames = {}
        self.build_steps()
        self.show_step(0)

    def show_step(self, step):
        for fr in self.step_frames.values():
            fr.grid_remove()
        if step == 2:
            self.refresh_step3()
        self.step_frames[step].grid(row=0, column=0, sticky="nsew")

    def is_sports_role(self, role):
        return "Sports Captain" in role

    def next_step1(self):
        title_text = self.title_entry.get().strip()
        description_text = self.description_box.get("0.0", "end").strip()
        if not title_text:
            return
        self.election_id = db.step1_add(title_text, description_text)
        self.show_step(1)

    def next_step2(self):
        candidate_rows = []
        for candidate in self.candidates:
            name = candidate["name"].get().strip()
            id_no = candidate["id_no"].get().strip()
            role = candidate["role"].get()
            kutumba = candidate["kutumba"].get().strip()
            if self.is_sports_role(role):
                kutumba = ""
            if not name or not id_no:
                return
            candidate_rows.append((name, id_no, kutumba, role))
        db.step2_add_many(self.election_id, candidate_rows)
        self.show_step(2)

    def finish(self):
        self.reset()
        self.switch_page("home")

    def build_steps(self):
        self.build_step1()
        self.build_step2()
        self.build_step3()

    def build_step1(self):
        step = ctk.CTkFrame(self, fg_color="transparent")
        step.grid_columnconfigure(0, weight=1)
        self.step_frames[0] = step

        ctk.CTkLabel(step, text="Create Election", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=32, pady=(32, 4))
        ctk.CTkLabel(step, text="Step 1 of 3 - Basic info", font=ctk.CTkFont(size=13), text_color=GRAY, anchor="w").grid(row=1, column=0, sticky="w", padx=32, pady=(0, 24))
        ctk.CTkLabel(step, text="Election title", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=2, column=0, sticky="w", padx=32)

        self.title_entry = ctk.CTkEntry(step, placeholder_text="e.g. School Elections", fg_color=SPACE_CADET, border_color=DARK_GRAY, text_color=WHITE, height=40, font=ctk.CTkFont(size=14))
        self.title_entry.grid(row=3, column=0, sticky="ew", padx=32, pady=(4, 16))

        ctk.CTkLabel(step, text="Description", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=4, column=0, sticky="w", padx=32)

        self.description_box = ctk.CTkTextbox(step, height=120, fg_color=SPACE_CADET, border_color=DARK_GRAY, text_color=WHITE, font=ctk.CTkFont(size=14))
        self.description_box.grid(row=5, column=0, sticky="ew", padx=32, pady=(4, 0))

        ctk.CTkButton(step, text="Next", fg_color=BLUE, hover_color=DARK_BLUE, font=ctk.CTkFont(size=13, weight="bold"), height=40, corner_radius=8, command=self.next_step1).grid(row=6, column=0, sticky="e", padx=32, pady=24)

    def build_step2(self):
        step = ctk.CTkFrame(self, fg_color="transparent")
        step.grid_columnconfigure(0, weight=1)
        step.grid_rowconfigure(1, weight=1)
        self.step_frames[1] = step

        ctk.CTkLabel(step, text="Step 2 of 3 - Add candidates", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=32, pady=(32, 4))

        self.candidates_frame = ctk.CTkScrollableFrame(step, fg_color=NAVY)
        self.candidates_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.candidates_frame.grid_columnconfigure(0, weight=1)

        self.candidates = []
        self.add_candidate_row()

        ctk.CTkButton(step, text="Add candidate", fg_color=SPACE_CADET, text_color=BLUE, command=self.add_candidate_row).grid(row=2, column=0, sticky="w", padx=32, pady=(0, 8))

        btn_frame = ctk.CTkFrame(step, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=32, pady=16)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="Back", fg_color=SPACE_CADET, text_color=GRAY, command=lambda: self.show_step(0)).grid(row=0, column=0)
        ctk.CTkButton(btn_frame, text="Next", fg_color=BLUE, command=self.next_step2).grid(row=0, column=2)

    def add_candidate_row(self):
        row_frame = ctk.CTkFrame(self.candidates_frame, fg_color=SPACE_CADET, corner_radius=12)
        row_frame.grid_columnconfigure(1, weight=1)

        id_entry = ctk.CTkEntry(row_frame, placeholder_text="ID No.", width=110)
        name_entry = ctk.CTkEntry(row_frame, placeholder_text="Full name")

        kutumba_var = ctk.StringVar(value="Atri")
        kutumba_menu = ctk.CTkOptionMenu(row_frame, values=["Atri", "Gautama", "Vashista", "Kashyappa"], variable=kutumba_var, fg_color=NAVY, button_color=NAVY, button_hover_color=DARK_GRAY)

        role_var = ctk.StringVar(value="Boy Captain")
        role_menu = ctk.CTkOptionMenu(row_frame, values=["Boy Captain", "Girl Captain", "Boy Sports Captain", "Girl Sports Captain"], variable=role_var, fg_color=NAVY, button_color=NAVY, button_hover_color=DARK_GRAY)

        def sync_kutumba(*_): # trace_add returns 3 args that we wanna ignore
            if self.is_sports_role(role_var.get()):
                kutumba_var.set("")
                kutumba_menu.configure(state="disabled")
            else:
                kutumba_menu.configure(state="normal")
                if not kutumba_var.get().strip():
                    kutumba_var.set("Atri")

        role_var.trace_add("write", sync_kutumba) # method in tkinter that reacts to wt the user chooses
        sync_kutumba()

        candidate = {"frame": row_frame, "id_no": id_entry, "name": name_entry, "kutumba": kutumba_var, "role": role_var}

        def delete_row():
            self.candidates.remove(candidate)
            row_frame.destroy()
            self.refresh_candidate_grid()

        del_btn = ctk.CTkButton(row_frame, text="Delete", fg_color="transparent", hover_color=DARK_GRAY, text_color=RED, border_width=1, border_color=DARK_GRAY, height=32, corner_radius=10, command=delete_row)

        id_entry.grid(row=0, column=0, padx=(10, 6), pady=10, sticky="w")
        name_entry.grid(row=0, column=1, padx=6, pady=10, sticky="ew")
        kutumba_menu.grid(row=0, column=2, padx=6, pady=10, sticky="w")
        role_menu.grid(row=0, column=3, padx=6, pady=10, sticky="w")
        del_btn.grid(row=0, column=4, padx=(6, 10), pady=10, sticky="e")

        self.candidates.append(candidate)
        self.refresh_candidate_grid()

    def refresh_candidate_grid(self):
        for i, c in enumerate(self.candidates):
            c["frame"].grid(row=i, column=0, padx=10, pady=6, sticky="ew")

    def build_step3(self):
        step = ctk.CTkFrame(self, fg_color="transparent")
        step.grid_columnconfigure(0, weight=1)
        step.grid_rowconfigure(1, weight=1)
        self.step_frames[2] = step

        ctk.CTkLabel(step, text="Step 3 of 3 - Review and Import Voters", font=ctk.CTkFont(size=28, weight="bold"), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=32, pady=(32, 4))

        self.review_frame = ctk.CTkScrollableFrame(step, fg_color=NAVY)
        self.review_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.review_frame.grid_columnconfigure(0, weight=1)

        self.review_content = ctk.CTkFrame(self.review_frame, fg_color="transparent")
        self.review_content.grid(row=0, column=0, sticky="ew")
        self.review_content.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(step, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=16)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="Back", fg_color=SPACE_CADET, text_color=GRAY, command=lambda: self.show_step(1)).grid(row=0, column=0)
        ctk.CTkButton(btn_frame, text="Finish", fg_color=GREEN, hover_color="#1aa368", text_color=WHITE, font=ctk.CTkFont(size=13, weight="bold"), command=self.finish).grid(row=0, column=2)

    def refresh_step3(self):
        for w in self.review_content.winfo_children():
            w.destroy()

        row = 0

        id_card = ctk.CTkFrame(self.review_content, fg_color=SPACE_CADET, corner_radius=12)
        id_card.grid(row=row, column=0, sticky="ew", padx=8, pady=(16, 8))
        id_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(id_card, text="ELECTION ID", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=GRAY, anchor="w").grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")
        ctk.CTkLabel(id_card, text=str(self.election_id) if self.election_id else "-", font=ctk.CTkFont(size=26, weight="bold"), text_color=BLUE, anchor="w").grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")
        ctk.CTkLabel(id_card, text="Share this ID with voters so they can log in.", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=1, column=1, padx=14, pady=(0, 10), sticky="w")
        row += 1

        ctk.CTkLabel(self.review_content, text="ELECTION INFO", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=GRAY, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=(16, 6))
        row += 1
        ctk.CTkLabel(self.review_content, text=f"Title:  {self.title_entry.get().strip()}", font=ctk.CTkFont(size=13), text_color=WHITE, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=2)
        row += 1
        ctk.CTkLabel(self.review_content, text=f"Description:  {self.description_box.get('0.0', 'end').strip()}", font=ctk.CTkFont(size=13), text_color=WHITE, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=2)
        row += 1

        ctk.CTkLabel(self.review_content, text=f"CANDIDATES  ({len(self.candidates)})", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=GRAY, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=(24, 6))
        row += 1

        for c in self.candidates:
            card = ctk.CTkFrame(self.review_content, fg_color=SPACE_CADET, corner_radius=8)
            card.grid(row=row, column=0, sticky="ew", padx=8, pady=4)
            card.grid_columnconfigure(0, weight=1)
            kutumba_txt = c["kutumba"].get().strip() or "-"
            ctk.CTkLabel(card, text=f"{c['name'].get().strip()}  .  {c['role'].get()}  .  {kutumba_txt}", font=ctk.CTkFont(size=13), text_color=WHITE, anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=6)
            ctk.CTkLabel(card, text=f"ID: {c['id_no'].get().strip()}", font=ctk.CTkFont(size=12), text_color=GRAY, anchor="w").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))
            row += 1

        ctk.CTkLabel(self.review_content, text="VOTERS", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=GRAY, anchor="w").grid(row=row, column=0, sticky="w", padx=8, pady=(24, 6))
        row += 1

        voter_card = ctk.CTkFrame(self.review_content, fg_color=SPACE_CADET, corner_radius=12)
        voter_card.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 16))
        voter_card.grid_columnconfigure(0, weight=1)

        if self.voter_import_count == 0:
            status_text = "No voters imported yet."
            status_color = GRAY
        else:
            status_text = f"{self.voter_import_count} voters imported."
            status_color = GREEN

        self.voter_status_lbl = ctk.CTkLabel(voter_card, text=status_text, font=ctk.CTkFont(size=13), text_color=status_color, anchor="w")
        self.voter_status_lbl.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        ctk.CTkLabel(voter_card, text="File must have columns: id_no and kutumba. Other columns are ignored.", font=ctk.CTkFont(size=11), text_color=GRAY, anchor="w").grid(row=1, column=0, padx=14, pady=(0, 6), sticky="w")
        ctk.CTkButton(voter_card, text="Import voters file", fg_color=BLUE, hover_color=DARK_BLUE, text_color=WHITE, height=36, corner_radius=10, font=ctk.CTkFont(size=12, weight="bold"), command=self.import_voters).grid(row=2, column=0, padx=14, pady=(4, 14), sticky="w")

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
        imported, skipped = db.import_voters_for_election(self.election_id, voter_rows)
        self.voter_import_count += imported
        self.voter_status_lbl.configure(text=f"{self.voter_import_count} voters imported. ({skipped} skipped)", text_color=GREEN)