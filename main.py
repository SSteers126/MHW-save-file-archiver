from pathlib import Path
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import *
import sys

from tktooltip import ToolTip

import py7zr
import showinfm

import save_tools


class MHWSaveCopier(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("MHW Save Backup Tool")

        # Get the icon from the executable file, and use it for windows within the app
        self.iconbitmap(sys.executable)

        # User account selection box
        self.found_valid_saves = save_tools.get_steam_mhw_saves()
        self.save_frame = Labelframe(self, text="Archive Save Data", padding=5)
        self.save_frame.grid(row=0, column=0, sticky=NSEW)
        # Selection Combo Box label
        self.save_label = Label(self.save_frame, text="Steam User ID: ")
        self.save_label.grid(row=0, column=0)
        # Combo Box for user to select
        self.save_variable = StringVar()
        self.save_dropdown = Combobox(self.save_frame, textvariable=self.save_variable)
        ToolTip(self.save_dropdown, msg="Selects the user to archive Save Data for.", delay=0.75,
                follow=True)
        # Set options to user IDs with found save files
        self.save_dropdown["state"] = "readonly"
        self.save_dropdown["values"] = list(self.found_valid_saves.keys())
        self.save_dropdown.grid(row=0, column=1)
        # Save source viewing
        self.view_save_button = Button(self.save_frame, text="View Selected Save Data", padding=5,
                                       command=self.view_selected_save)
        ToolTip(self.view_save_button, msg="Shows the folder that the user's Save Data is located within.", delay=0.75,
                follow=True)
        self.view_save_button.grid(row=1, column=0, columnspan=2, pady=5)
        # Save Archival button
        self.archive_button = Button(self.save_frame, text="Archive Save Data", padding=5, command=self.archive_save)
        ToolTip(self.archive_button,
                msg="Copies the user's save data to a compressed archive at a location of your choosing.",
                delay=0.75, follow=True)
        self.archive_button.grid(row=2, column=0, columnspan=2)
        weight_grid_equally(self.save_frame)

        # Archive Extraction
        self.extract_frame = Labelframe(self, text="Extract Save Data Archive", padding=5)
        self.extract_frame.grid(row=3, column=0, sticky=NSEW)
        self.extract_button = Button(self.extract_frame, text="Extract Save Data", padding=5, command=self.extract_save)
        ToolTip(self.extract_button,
                msg="Extracts a Save Data archive to a directory of your choosing."
                    "\n(opens a file manager window for selection)",
                delay=0.75, follow=True)
        self.extract_button.grid(row=0, column=0)
        weight_grid_equally(self.extract_frame)

        weight_grid_equally(self)

        self.resizable(False, False)

    def get_selected_save_path(self) -> Path:
        return self.found_valid_saves[self.save_dropdown.get()]

    def view_selected_save(self):
        selected_save = self.save_dropdown.get()

        if not selected_save:
            messagebox.showwarning("No Save Selected",
                                   r"Please select a user from the 'Steam User ID' drop-down "
                                   r"before attempting to view save data.")

        else:
            # Slightly slower by getting the save value twice but keeps better consistency
            showinfm.show_in_file_manager(str(self.get_selected_save_path()))

    def archive_save_files(self, archive_directory: Path, user_id: str) -> None:
        with py7zr.SevenZipFile(archive_directory, "w") as archive:
            archive.writeall(self.get_selected_save_path(), arcname=f"Save Data (User ID - {user_id})")

    def archive_save(self):
        try:
            selected_save = self.save_dropdown.get()

            if not selected_save:
                messagebox.showwarning("No Save Selected",
                                       r"Please select a user from the 'Steam User ID' drop-down "
                                       r"before attempting to archive save data.")

            else:
                archive_path = filedialog.asksaveasfilename(defaultextension=".7z",
                                                            filetypes=[("7-Zip Archive File", "*.7z"),
                                                                       ("All Files", "*.*")],
                                                            confirmoverwrite=True)

                # If a path was chosen (i.e action not cancelled)
                if archive_path:
                    self.archive_save_files(Path(archive_path), selected_save)

                # Otherwise, tell the user nothing has happened
                else:
                    messagebox.showinfo("Archive Cancelled",
                                        "Archival has been cancelled - no action has been taken.")

        except Exception as e:
            messagebox.showerror("Save Archival Error", str(e))

    def extract_save(self):
        try:
            action_resolved = False

            archive_path = filedialog.askopenfilename(defaultextension=".7z",
                                                      filetypes=[("7-Zip Archive Files", "*.7z")])
            # If an archive path was chosen
            if archive_path:
                # Open the archive

                if not py7zr.is_7zfile(Path(archive_path)):
                    messagebox.showerror("Corrupt Archive", "The chosen archive is either "
                                                            "not a 7zip archive or corrupt (No magic number present). "
                                                            "Data cannot be extracted.")
                    action_resolved = True

                else:
                    with py7zr.SevenZipFile(Path(archive_path), "r") as archive:
                        extract_path = filedialog.askdirectory(mustexist=True)
                        # If a valid extraction path was chosen
                        if extract_path:
                            # Extract to that path
                            archive.extractall(Path(extract_path))
                            action_resolved = True

            if not action_resolved:
                messagebox.showinfo("Extraction Cancelled",
                                    "Extraction has been cancelled - no action has been taken.")

        except Exception as e:
            messagebox.showerror("Save Extraction Error", str(e))


def weight_grid_equally(grid_object):
    for column in range(grid_object.grid_size()[0]):
        grid_object.columnconfigure(column, weight=1)
    for row in range(grid_object.grid_size()[1]):
        grid_object.rowconfigure(row, weight=1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = MHWSaveCopier()
    app.mainloop()
