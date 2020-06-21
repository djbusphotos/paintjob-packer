import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser, sys, configparser, os, math, re, traceback
import library.paintjob as pj

version = "1.3"
forum_link = "https://forum.scssoft.com/viewtopic.php?f=33&t=282956"
github_link = "https://github.com/carsmaniac/paintjob-packer"
mod_link_page_link = "https://github.com/Carsmaniac/paintjob-packer/blob/master/library/mod%20links.md"

# set the path depending on how Paintjob Packer is bundled
try:
    base_path = sys._MEIPASS # packaged into executable
    using_executable = True
except AttributeError:
    base_path = os.path.abspath(".") # loose .py
    using_executable = False
os.chdir(base_path)

desktop_path = os.path.expanduser("~/Desktop")

class PackerApp:

    def __init__(self, master):
        # container to hold setup/main screen
        self.container = ttk.Frame(master)
        self.container.pack(fill = "both")

        self.image_packer = tk.PhotoImage(file = "library/packer images/packer.png")
        self.image_ats = tk.PhotoImage(file = "library/packer images/ats.png")
        self.image_ets = tk.PhotoImage(file = "library/packer images/ets.png")
        self.image_single_paintjob = tk.PhotoImage(file = "library/packer images/single paintjob.png")
        self.image_paintjob_pack = tk.PhotoImage(file = "library/packer images/paintjob pack.png")
        self.image_all_cabins = tk.PhotoImage(file = "library/packer images/all cabins.png")
        self.image_large_cabins = tk.PhotoImage(file = "library/packer images/large cabins.png")
        self.image_separate_cabins = tk.PhotoImage(file = "library/packer images/separate cabins.png")
        self.image_combined_cabins = tk.PhotoImage(file = "library/packer images/combined cabins.png")
        self.image_spacer_100 = tk.PhotoImage(file = "library/packer images/spacer 100.png")
        self.image_spacer_200 = tk.PhotoImage(file = "library/packer images/spacer 200.png")

        # load appropriate cursor for OS, used when mousing over links
        if sys.platform.startswith("win"):
            self.cursor = "hand2"
        elif sys.platform.startswith("darwin"): # macOS
            self.cursor = "pointinghand"
        elif sys.platform.startswith("linux"):
            self.cursor = "hand2"

        self.total_vehicles = 0 # used in the vehicle selector when making a paintjob pack

        # second window displayed when generating mod, mostly useless as it generates so quickly
        self.loading_window = tk.Toplevel(master)
        self.loading_window.title("Generating Mod")
        self.loading_window.state("withdrawn")
        self.loading_window.resizable(False, False)
        self.loading_label = ttk.Label(self.loading_window, text = "Generating mod, please wait...")
        self.loading_label.grid(row = 0, column = 0, pady = 20)
        self.loading_value = tk.DoubleVar(None, 5.0)
        self.loading_bar = ttk.Progressbar(self.loading_window, orient = "horizontal", length = 200, mode = "determinate", variable = self.loading_value)
        self.loading_bar.grid(row = 1, column = 0, padx = 45)
        self.loading_current = tk.StringVar(None, "DAF XF 105")
        self.loading_current_label = ttk.Label(self.loading_window, textvariable = self.loading_current)
        self.loading_current_label.grid(row = 2, column = 0, pady = 20)

        # setup screen and immediate contents
        self.setup_screen = ttk.Frame(self.container)
        self.tab_selector = ttk.Notebook(self.setup_screen)
        self.tab_selector.pack(fill = "both")
        self.tab_welcome = ttk.Frame(self.tab_selector)
        self.tab_selector.add(self.tab_welcome, text = " Welcome ", sticky = "nsew")
        self.tab_game = ttk.Frame(self.tab_selector)
        self.tab_selector.add(self.tab_game, text = " Game ")
        self.tab_paintjob = ttk.Frame(self.tab_selector)
        self.tab_selector.add(self.tab_paintjob, text = " Paintjobs ")

        # Welcome tab
        self.tab_welcome_title = ttk.Label(self.tab_welcome, text = "Welcome to Paintjob Packer")
        self.tab_welcome_title.grid(row = 0, column = 0, columnspan = 2, pady = 20)
        self.tab_welcome_image = ttk.Label(self.tab_welcome, image = self.image_packer)
        self.tab_welcome_image.grid(row = 1, column = 0, columnspan = 2)
        self.tab_welcome_link_forum = ttk.Label(self.tab_welcome, text = "Forum thread", foreground = "blue", cursor = self.cursor)
        self.tab_welcome_link_forum.grid(row = 2, column = 0, pady = 20)
        self.tab_welcome_link_forum.bind("<1>", lambda e: webbrowser.open_new(forum_link))
        self.tab_welcome_link_github = ttk.Label(self.tab_welcome, text = "GitHub page", foreground = "blue", cursor = self.cursor)
        self.tab_welcome_link_github.grid(row = 2, column = 1, pady = 20)
        self.tab_welcome_link_github.bind("<1>", lambda e: webbrowser.open_new(github_link))
        self.tab_welcome_message = ttk.Label(self.tab_welcome, text = "If this is your first time using Paintjob Packer, please read the guide on the GitHub page")
        self.tab_welcome_message.grid(row = 3, column = 0, columnspan = 2, pady = (25, 0))
        self.tab_welcome_button_prev = ttk.Label(self.tab_welcome, text = " ") # to keep everything centred
        self.tab_welcome_button_prev.grid(row = 5, column = 0, sticky = "sw")
        self.tab_welcome_button_next = ttk.Button(self.tab_welcome, text = "Next >", command = lambda : self.tab_selector.select(1))
        self.tab_welcome_button_next.grid(row = 5, column = 1, sticky = "se", pady = 10, padx = 10)
        self.tab_welcome.rowconfigure(5, weight = 1)
        self.tab_welcome.columnconfigure(0, weight = 1)
        self.tab_welcome.columnconfigure(1, weight = 1)

        # Game tab
        self.tab_game_title = ttk.Label(self.tab_game, text = "Which game are you making a mod for?")
        self.tab_game_title.grid(row = 0, column = 0, columnspan = 2, pady = 20)
        self.tab_game_image_ats = ttk.Label(self.tab_game, image = self.image_ats)
        self.tab_game_image_ats.grid(row = 1, column = 0, padx = 10)
        self.tab_game_image_ets = ttk.Label(self.tab_game, image = self.image_ets)
        self.tab_game_image_ets.grid(row = 1, column = 1, padx = 10)
        self.tab_game_variable = tk.StringVar(None, "ats")
        self.tab_game_option_ats = ttk.Radiobutton(self.tab_game, text = "American Truck Simulator", value = "ats", variable = self.tab_game_variable)
        self.tab_game_option_ats.grid(row = 2, column = 0, pady = 10)
        self.tab_game_image_ats.bind("<1>", lambda e: self.tab_game_variable.set("ats"))
        self.tab_game_option_ets = ttk.Radiobutton(self.tab_game, text = "Euro Truck Simulator 2", value = "ets", variable = self.tab_game_variable)
        self.tab_game_option_ets.grid(row = 2, column = 1, pady = 10)
        self.tab_game_image_ets.bind("<1>", lambda e: self.tab_game_variable.set("ets"))
        self.tab_game_dummy_desc = ttk.Label(self.tab_game, text = "  \n") # to space things out evenly
        self.tab_game_dummy_desc.grid(row = 3, column = 0)
        self.tab_game_button_prev = ttk.Button(self.tab_game, text = "< Prev", command = lambda : self.tab_selector.select(0))
        self.tab_game_button_prev.grid(row = 4, column = 0, sticky = "sw", pady = 10, padx = 10)
        self.tab_game_button_next = ttk.Button(self.tab_game, text = "Next >", command = lambda : self.tab_selector.select(2))
        self.tab_game_button_next.grid(row = 4, column = 1, sticky = "se", pady = 10, padx = 10)

        # Paintjobs tab
        self.tab_paintjob_title = ttk.Label(self.tab_paintjob, text = "How many paintjobs are you making?")
        self.tab_paintjob_title.grid(row = 0, column = 0, columnspan = 2, pady = 20)
        self.tab_paintjob_image_single = ttk.Label(self.tab_paintjob, image = self.image_single_paintjob)
        self.tab_paintjob_image_single.grid(row = 1, column = 0, padx = 10)
        self.tab_paintjob_image_pack = ttk.Label(self.tab_paintjob, image = self.image_paintjob_pack)
        self.tab_paintjob_image_pack.grid(row = 1, column = 1, padx = 10)
        self.tab_paintjob_variable = tk.StringVar(None, "pack")
        self.tab_paintjob_option_single = ttk.Radiobutton(self.tab_paintjob, text = "Single paintjob", value = "single", variable = self.tab_paintjob_variable)
        self.tab_paintjob_option_single.grid(row = 2, column = 0, pady = 10)
        self.tab_paintjob_image_single.bind("<1>", lambda e: self.tab_paintjob_variable.set("single"))
        self.tab_paintjob_option_pack = ttk.Radiobutton(self.tab_paintjob, text = "Paintjob pack", value = "pack", variable = self.tab_paintjob_variable)
        self.tab_paintjob_option_pack.grid(row = 2, column = 1, pady = 10)
        self.tab_paintjob_image_pack.bind("<1>", lambda e: self.tab_paintjob_variable.set("pack"))
        self.tab_paintjob_desc_single = ttk.Label(self.tab_paintjob, text = "A single paintjob for a single vehicle\n", wraplength = 300)
        self.tab_paintjob_desc_single.grid(row = 3, column = 0, padx = 10, sticky = "n")
        self.tab_paintjob_desc_pack = ttk.Label(self.tab_paintjob, text = "One paintjob that supports multiple vehicles", wraplength = 300)
        self.tab_paintjob_desc_pack.grid(row = 3, column = 1, padx = 10, sticky = "n")
        self.tab_paintjob_button_prev = ttk.Button(self.tab_paintjob, text = "< Prev", command = lambda : self.tab_selector.select(1))
        self.tab_paintjob_button_prev.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = "w")
        self.tab_paintjob_button_next = ttk.Button(self.tab_paintjob, text = "Continue", command = lambda : self.switch_to_main_screen())
        self.tab_paintjob_button_next.grid(row = 4, column = 1, padx = 10, pady = 10, sticky = "e")

        self.setup_screen.grid(row = 0, column = 0, padx = 10, pady = 10)

        # main screen and immediate contents
        self.main_screen = ttk.Frame(self.container)
        self.panel_mod = ttk.LabelFrame(self.main_screen, text = "Mod Info")
        self.panel_mod.grid(row = 0, column = 0, sticky = "ew")
        self.panel_ingame = ttk.LabelFrame(self.main_screen, text = "In-Game Paintjob Info")
        self.panel_ingame.grid(row = 1, column = 0, sticky = "ew")
        self.panel_internal = ttk.LabelFrame(self.main_screen, text = "Internal (Hidden) Info and Other Settings")
        self.panel_internal.grid(row = 2, column = 0, sticky = "new")
        self.panel_vehicles_pack = ttk.LabelFrame(self.main_screen, text = "Vehicles Supported (0)")
        self.panel_vehicles_single = ttk.LabelFrame(self.main_screen, text = "Vehicle Supported")
        self.panel_buttons = ttk.Frame(self.main_screen)
        self.panel_buttons.grid(row = 3, column = 0, columnspan = 2, sticky = "ew")
        self.panel_buttons.columnconfigure(1, weight = 1)
        self.main_screen.rowconfigure(2, weight = 1) # keeps things tidy if too many mods get added

        # Mod Info panel
        self.panel_mod_name_variable = tk.StringVar()
        self.panel_mod_name_label = ttk.Label(self.panel_mod, text = "Name:")
        self.panel_mod_name_label.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.panel_mod_name_input = ttk.Entry(self.panel_mod, width = 30, textvariable = self.panel_mod_name_variable)
        self.panel_mod_name_input.grid(row = 0, column = 1, padx = 5, sticky = "w")
        self.panel_mod_name_help = ttk.Button(self.panel_mod, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Mod Name", message = "The name of your mod, as it appears in the in-game mod manager\n\ne.g. Transit Co. Paintjob Pack"))
        self.panel_mod_name_help.grid(row = 0, column = 2, padx = (0, 5))
        self.panel_mod_version_variable = tk.StringVar(None, "1.0")
        self.panel_mod_version_label = ttk.Label(self.panel_mod, text = "Version:")
        self.panel_mod_version_label.grid(row = 1, column = 0, padx = 5, sticky = "w")
        self.panel_mod_version_input = ttk.Entry(self.panel_mod, width = 7, textvariable = self.panel_mod_version_variable)
        self.panel_mod_version_input.grid(row = 1, column = 1, padx = 5, sticky = "w")
        self.panel_mod_version_help = ttk.Button(self.panel_mod, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Mod Version", message = "The version of your mod, as it appears in the in-game mod manager\n\ne.g. 1.0"))
        self.panel_mod_version_help.grid(row = 1, column = 2, padx = (0, 5))
        self.panel_mod_author_variable = tk.StringVar()
        self.panel_mod_author_label = ttk.Label(self.panel_mod, text = "Author:")
        self.panel_mod_author_label.grid(row = 2, column = 0, padx = 5, sticky = "w")
        self.panel_mod_author_input = ttk.Entry(self.panel_mod, width = 30, textvariable = self.panel_mod_author_variable)
        self.panel_mod_author_input.grid(row = 2, column = 1, padx = 5, sticky = "w")
        self.panel_mod_author_help = ttk.Button(self.panel_mod, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Author", message = "The author of your mod, as it appears in the in-game mod manager\n\ne.g. Carsmaniac"))
        self.panel_mod_author_help.grid(row = 2, column = 2, padx = (0, 5))
        self.panel_mod_spacer_label = ttk.Label(self.panel_mod, image = self.image_spacer_100)
        self.panel_mod_spacer_label.grid(row = 3, column = 0)
        self.panel_mod_spacer_input = ttk.Label(self.panel_mod, image = self.image_spacer_200)
        self.panel_mod_spacer_input.grid(row = 3, column = 1)

        # In-Game Paintjob Info panel
        self.panel_ingame_name_variable = tk.StringVar()
        self.panel_ingame_name_label = ttk.Label(self.panel_ingame, text = "Name:")
        self.panel_ingame_name_label.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.panel_ingame_name_input = ttk.Entry(self.panel_ingame, width = 30, textvariable = self.panel_ingame_name_variable)
        self.panel_ingame_name_input.grid(row = 0, column = 1, padx = 5, sticky = "w")
        self.panel_ingame_name_help = ttk.Button(self.panel_ingame, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: In-Game Name", message = "The name of your paintjob as it appears in-game in the vehicle purchase/upgrade screen\n\ne.g. Transit Co. Paintjob"))
        self.panel_ingame_name_help.grid(row = 0, column = 2, padx = (0, 5))
        self.panel_ingame_price_variable = tk.StringVar()
        self.panel_ingame_price_label = ttk.Label(self.panel_ingame, text = "Price:")
        self.panel_ingame_price_label.grid(row = 1, column = 0, padx = 5, sticky = "w")
        self.panel_ingame_price_input = ttk.Entry(self.panel_ingame, width = 7, textvariable = self.panel_ingame_price_variable)
        self.panel_ingame_price_input.grid(row = 1, column = 1, padx = 5, sticky = "w")
        self.panel_ingame_price_help = ttk.Button(self.panel_ingame, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: In-Game Price", message = "How much your paintjob costs in-game, in {}.\n\ne.g. 6000".format(self.currency)))
        self.panel_ingame_price_help.grid(row = 1, column = 2, padx = (0, 5))
        self.panel_ingame_default_variable = tk.BooleanVar(None, True)
        self.panel_ingame_default_checkbox = ttk.Checkbutton(self.panel_ingame, text = "Unlocked by default", variable = self.panel_ingame_default_variable, command = lambda : self.toggle_unlock_level())
        self.panel_ingame_default_checkbox.grid(row = 2, column = 0, columnspan = 2, padx = 5, sticky = "w")
        self.panel_ingame_default_help = ttk.Button(self.panel_ingame, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Unlocked By Default", message = "Whether or not your paintjob can be bought from level 0, for example on a brand new profile"))
        self.panel_ingame_default_help.grid(row = 2, column = 2, padx = (0, 5))
        self.panel_ingame_unlock_variable = tk.StringVar()
        self.panel_ingame_unlock_label = ttk.Label(self.panel_ingame, text = "Unlock level:")
        self.panel_ingame_unlock_label.grid(row = 3, column = 0, padx = 5, sticky = "w")
        self.panel_ingame_unlock_input = ttk.Entry(self.panel_ingame, width = 5, textvariable = self.panel_ingame_unlock_variable)
        self.panel_ingame_unlock_input.grid(row = 3, column = 1, padx = 5, sticky = "w")
        self.panel_ingame_unlock_input.state(["disabled"]) # disabled by default, as the "unlocked by default" checkbox is checked by default
        self.panel_ingame_unlock_help = ttk.Button(self.panel_ingame, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Unlock Level", message = "If not unlocked by default, what level your paintjob is made purchasable at\n\ne.g. 11"))
        self.panel_ingame_unlock_help.grid(row = 3, column = 2, padx = (0, 5))
        self.panel_ingame_spacer_label = ttk.Label(self.panel_ingame, image = self.image_spacer_100)
        self.panel_ingame_spacer_label.grid(row = 4, column = 0)
        self.panel_ingame_spacer_input = ttk.Label(self.panel_ingame, image = self.image_spacer_200)
        self.panel_ingame_spacer_input.grid(row = 4, column = 1)

        # Internal Paintjob Info panel
        self.panel_internal_name_variable = tk.StringVar()
        self.panel_internal_name_label = ttk.Label(self.panel_internal, text = "Internal name:")
        self.panel_internal_name_label.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.panel_internal_name_input = ttk.Entry(self.panel_internal, width = 15, textvariable = self.panel_internal_name_variable)
        self.panel_internal_name_input.grid(row = 0, column = 1, padx = 5, sticky = "w")
        self.panel_internal_name_help = ttk.Button(self.panel_internal, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Internal Name", message = "A unique name used by the game to identify your paintjob. Mod users will NOT see this name.\n\nMust be {} characters or fewer, and only contain letters, numbers and underscores.\n\nMust also be unique, if two different mods use the same internal name they will be incompatible with each other.\n\ne.g. transit_co".format(self.internal_name_length)))
        self.panel_internal_name_help.grid(row = 0, column = 2, padx = (0, 5))
        self.panel_internal_workshop_variable = tk.BooleanVar(None, False)
        self.panel_internal_workshop_checkbox = ttk.Checkbutton(self.panel_internal, text = "Generate files for Steam Workshop upload", variable = self.panel_internal_workshop_variable)
        self.panel_internal_workshop_checkbox.grid(row = 3, column = 0, columnspan = 2, padx = 5, sticky = "w")
        self.panel_internal_workshop_help = ttk.Button(self.panel_internal, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Workshop Upload", message = "Generates additional files needed when uploading to Steam Workshop, including a workshop image, an uploading folder and a workshop description with working links to any modded vehicles you support\n\nRequires the SCS Workshop Uploader, which only supports Windows"))
        self.panel_internal_workshop_help.grid(row = 3, column = 2, padx = (0, 5))
        self.panel_internal_supported_variable = tk.StringVar(None, "Largest cabin only")
        self.panel_internal_supported_variable.trace("w", self.update_cabin_dropdowns)
        self.panel_internal_supported_label = ttk.Label(self.panel_internal, text = "Supported cabins:")
        self.panel_internal_supported_label.grid(row = 4, column = 0, padx = (5, 0), sticky = "w")
        self.panel_internal_supported_dropdown = ttk.Combobox(self.panel_internal, state = "readonly", textvariable = self.panel_internal_supported_variable, values = ["Largest cabin only", "All cabins"], width = 20)
        self.panel_internal_supported_dropdown.grid(row = 4, column = 1, padx = 5, sticky = "w")
        self.panel_internal_supported_help = ttk.Button(self.panel_internal, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Supported Cabins", message = "Whether your paintjob supports only the largest cabin for each truck, or all cabins.\n\nNote that the 8x4 chassis uses a separate cabin in some cases, which would not be supported if you choose largest cabin only.\n\ne.g. If you're making a paintjob for the Scania Streamline, a \"largest cabin only\" paintjob would only support the Topline cabin, whereas an \"all cabins\" paintjob would support the Normal, Highline and Topline cabins, as well as the separate Topline 8x4 cabin."))
        self.panel_internal_supported_help.grid(row = 4, column = 2, padx = (0, 5))
        self.panel_internal_handling_variable = tk.StringVar(None, "Combined paintjob")
        self.panel_internal_handling_variable.trace("w", self.update_cabin_dropdowns)
        self.panel_internal_handling_label = ttk.Label(self.panel_internal, text = "Cabin handling:")
        # self.panel_internal_handling_label.grid(row = 5, column = 0, padx = 5, sticky = "w")
        self.panel_internal_handling_dropdown = ttk.Combobox(self.panel_internal, state = "readonly", textvariable = self.panel_internal_handling_variable, values = ["Combined paintjob", "Separate paintjobs"], width = 20)
        # self.panel_internal_handling_dropdown.grid(row = 5, column = 1, padx = 5, sticky = "w")
        self.panel_internal_handling_help = ttk.Button(self.panel_internal, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Cabin Handling", message = "Whether multiple cabins should be combined into a single paintjob, or separated into multiple paintjobs.\n\nA single combined paintjob requires less work and results in a smaller mod size, as you only need to make a single cabin texture for each truck. However, your design might not work across all the different cabin sizes, for example your design could look correct on large cabins, but be positioned incorrectly/stretched/cut off on smaller cabins.\n\nSeparate paintjobs allow you to tweak your design to work for each cabin, but require more work and result in a larger mod size, as you need to make separate textures for every cabin whether they need them or not.\n\nThe optional cabin unifier system gives you the benefits of both options, but is a little trickier to use and requires a hex editor. To use the cabin unifier, choose \"separate paintjobs\"."))
        # self.panel_internal_handling_help.grid(row = 5, column = 2, padx = (0, 5))
        self.panel_internal_unifier_variable = tk.BooleanVar(None, False)
        self.panel_internal_unifier_variable.trace("w", self.update_cabin_dropdowns)
        self.panel_internal_unifier_checkbox = ttk.Checkbutton(self.panel_internal, text = "Use the cabin unifier system", variable = self.panel_internal_unifier_variable)
        # self.panel_internal_unifier_checkbox.grid(row = 6, column = 0, columnspan = 2, padx = 5, sticky = "w")
        self.panel_internal_unifier_help = ttk.Button(self.panel_internal, text = "?", width = 3, command = lambda : messagebox.showinfo(title = "Help: Cabin Unifier", message = "All separate paintjobs for each truck are changed so that they point to a single cabin texture. You can then add additional textures if needed by editing .tobj files using a hex editor. Once you've finished making your mod, the unifier program will then combine any paintjobs that point to the same texture.\n\ne.g. If you have one texture used for Cabin A, and another texture used for both Cabin B and Cabin C, you'll end up with only 2 paintjobs after unifying, instead of 3.\n\nRequires a hex editor to use."))
        # self.panel_internal_unifier_help.grid(row = 6, column = 2, padx = (0, 5))
        self.panel_internal_unifier_warning = ttk.Label(self.panel_internal, text = "Please read this guide before using the cabin unifier", foreground = "blue", cursor = self.cursor)
        self.panel_internal_unifier_warning.bind("<1>", lambda e: webbrowser.open_new(github_link))
        # self.panel_internal_unifier_warning.grid(row = 7, column = 0, columnspan = 3, padx = 5, sticky = "w")
        self.panel_internal_spacer_label = ttk.Label(self.panel_internal, image = self.image_spacer_100)
        self.panel_internal_spacer_label.grid(row = 8, column = 0)
        self.panel_internal_spacer_input = ttk.Label(self.panel_internal, image = self.image_spacer_200)
        self.panel_internal_spacer_input.grid(row = 8, column = 1)

        # Vehicle Supported panel (single paintjob)
        self.panel_single_type_variable = tk.StringVar(None, "Truck")
        self.panel_single_type_variable.trace("w", self.change_displayed_vehicle_dropdown)
        self.panel_single_type_label = ttk.Label(self.panel_vehicles_single, text = "Type:")
        self.panel_single_type_label.grid(row = 0, column = 0, padx = 5, sticky = "w")
        self.panel_single_type_dropdown = ttk.Combobox(self.panel_vehicles_single, state = "readonly", textvariable = self.panel_single_type_variable, values = ["Truck", "Truck Mod", "Trailer", "Trailer Mod"], width = 12)
        self.panel_single_type_dropdown.grid(row = 1, column = 0, padx = 5, sticky = "w")
        self.panel_single_vehicle_variable = tk.StringVar()
        self.panel_single_vehicle_label = ttk.Label(self.panel_vehicles_single, text = "Vehicle:")
        self.panel_single_vehicle_label.grid(row = 2, column = 0, padx = 5, pady = (5, 0), sticky = "w")
        self.panel_single_vehicle_dropdown = ttk.Combobox(self.panel_vehicles_single, state = "readonly", textvariable = self.panel_single_vehicle_variable, values = [], width = 30)
        self.panel_single_vehicle_dropdown.grid(row = 3, column = 0, padx = 5, sticky = "w")
        self.panel_single_link = ttk.Label(self.panel_vehicles_single, text = "Download links for all mods", foreground = "blue", cursor = self.cursor)
        self.panel_single_link.bind("<1>", lambda e: webbrowser.open_new(mod_link_page_link))
        # self.panel_single_link.grid(row = 4, column = 0, pady = 5, padx = 5, sticky = "w")

        # Vehicles Supported panel (paintjob pack)
        self.panel_pack_selector = ttk.Notebook(self.panel_vehicles_pack)
        self.panel_pack_selector.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = (0, 5))
        self.tab_trucks = ttk.Frame(self.panel_pack_selector)
        self.panel_pack_selector.add(self.tab_trucks, text = "Trucks")
        self.tab_trailers = ttk.Frame(self.panel_pack_selector)
        self.panel_pack_selector.add(self.tab_trailers, text = "Trailers")
        self.tab_truck_mods = ttk.Frame(self.panel_pack_selector)
        self.panel_pack_selector.add(self.tab_truck_mods, text = "Truck Mods")
        self.tab_trailer_mods = ttk.Frame(self.panel_pack_selector)
        self.panel_pack_selector.add(self.tab_trailer_mods, text = "Trailer Mods")
        self.panel_pack_link_truck = ttk.Label(self.tab_truck_mods, text = "Download links for all mods", foreground = "blue", cursor = self.cursor)
        self.panel_pack_link_truck.bind("<1>", lambda e: webbrowser.open_new(mod_link_page_link))
        self.panel_pack_link_trailer = ttk.Label(self.tab_trailer_mods, text = "Download links for all mods", foreground = "blue", cursor = self.cursor)
        self.panel_pack_link_trailer.bind("<1>", lambda e: webbrowser.open_new(mod_link_page_link))

        # buttons along the bottom
        self.panel_buttons_setup = ttk.Button(self.panel_buttons, text = "< Back to setup", command = lambda : self.switch_to_setup_screen(), width = 15)
        self.panel_buttons_setup.grid(row = 1, column = 0, pady = (5, 0), sticky = "w")
        self.panel_buttons_feedback = ttk.Label(self.panel_buttons, text = "Leave feedback or get support", foreground = "blue", cursor = self.cursor)
        self.panel_buttons_feedback.grid(row = 1, column = 1, pady = (5, 0), padx = 10, sticky = "e")
        self.panel_buttons_feedback.bind("<1>", lambda e: webbrowser.open_new(forum_link))
        self.panel_buttons_generate = ttk.Button(self.panel_buttons, text = "Generate and save...", command = lambda : self.verify_all_inputs(), width = 20)
        self.panel_buttons_generate.grid(row = 1, column = 2, pady = (5, 0), sticky = "e")

    def update_cabin_dropdowns(self, *args):
        self.internal_name_length = 12
        if self.panel_internal_supported_variable.get() == "Largest cabin only":
            self.panel_internal_handling_label.grid_forget()
            self.panel_internal_handling_dropdown.grid_forget()
            self.panel_internal_handling_help.grid_forget()
            self.panel_internal_unifier_checkbox.grid_forget()
            self.panel_internal_unifier_help.grid_forget()
            self.panel_internal_unifier_warning.grid_forget()
        elif self.panel_internal_supported_variable.get() == "All cabins":
            self.panel_internal_handling_label.grid(row = 5, column = 0, padx = 5, sticky = "w")
            self.panel_internal_handling_dropdown.grid(row = 5, column = 1, padx = 5, sticky = "w")
            self.panel_internal_handling_help.grid(row = 5, column = 2, padx = (0, 5))

            if self.panel_internal_handling_variable.get() == "Combined paintjob":
                self.panel_internal_unifier_checkbox.grid_forget()
                self.panel_internal_unifier_help.grid_forget()
                self.panel_internal_unifier_warning.grid_forget()
            elif self.panel_internal_handling_variable.get() == "Separate paintjobs":
                self.panel_internal_unifier_checkbox.grid(row = 6, column = 0, columnspan = 2, padx = 5, sticky = "w")
                self.panel_internal_unifier_help.grid(row = 6, column = 2, padx = (0, 5))
                self.internal_name_length = 10

                if not self.panel_internal_unifier_variable.get():
                    self.panel_internal_unifier_warning.grid_forget()
                elif self.panel_internal_unifier_variable.get():
                    self.panel_internal_unifier_warning.grid(row = 7, column = 0, columnspan = 3, padx = 5, sticky = "w")

    def switch_to_setup_screen(self):
        if self.tab_paintjob_variable.get() == "single":
            self.panel_vehicles_single.grid_forget()
        elif self.tab_paintjob_variable.get() == "pack":
            self.panel_vehicles_pack.grid_forget()
        self.main_screen.grid_forget()
        self.setup_screen.grid(row = 0, column = 0, padx = 10, pady = 10)

        for veh in self.truck_list_1 + self.truck_list_2 + self.truck_mod_list_1 + self.truck_mod_list_2 + self.trailer_list_1 + self.trailer_list_2 + self.trailer_mod_list_1 + self.trailer_mod_list_2:
            veh.check.grid_forget()

        self.panel_pack_link_truck.grid_forget() # just in case it changes location
        self.panel_pack_link_trailer.grid_forget()

    def switch_to_main_screen(self):
        self.setup_screen.grid_forget()
        self.main_screen.grid(row = 0, column = 0, padx = 10, pady = 10)
        if self.tab_paintjob_variable.get() == "single":
            self.panel_vehicles_single.grid(row = 0, column = 1, rowspan = 3, sticky = "ns", padx = (5, 0))
        elif self.tab_paintjob_variable.get() == "pack":
            self.panel_vehicles_pack.grid(row = 0, column = 1, rowspan = 3, sticky = "ns", padx = (5, 0))
        self.load_main_screen_variables()
        self.update_cabin_dropdowns()

    def load_main_screen_variables(self): # also grids and ungrids stuff depending on said variables
        if self.tab_game_variable.get() == "ats":
            self.currency = "dollars"
        elif self.tab_game_variable.get() == "ets":
            self.currency = "euro"

        (self.truck_list, self.truck_mod_list, self.trailer_list, self.trailer_mod_list) = self.load_list_of_vehicles(self.tab_game_variable.get())
        self.truck_list_1 = self.truck_list[:math.ceil(len(self.truck_list)/2)] # lists need to be split for multiple vehicle selection, it's easier if it's done here
        self.truck_list_2 = self.truck_list[math.ceil(len(self.truck_list)/2):]
        self.truck_mod_list_1 = self.truck_mod_list[:math.ceil(len(self.truck_mod_list)/2)]
        self.truck_mod_list_2 = self.truck_mod_list[math.ceil(len(self.truck_mod_list)/2):]
        self.trailer_list_1 = self.trailer_list[:math.ceil(len(self.trailer_list)/2)]
        self.trailer_list_2 = self.trailer_list[math.ceil(len(self.trailer_list)/2):]
        self.trailer_mod_list_1 = self.trailer_mod_list[:math.ceil(len(self.trailer_mod_list)/2)]
        self.trailer_mod_list_2 = self.trailer_mod_list[math.ceil(len(self.trailer_mod_list)/2):]

        for i in range(len(self.truck_list_1)):
            self.truck_list_1[i].check.grid(row = i, column = 0, sticky = "w", padx = 5)
        for i in range(len(self.truck_list_2)):
            self.truck_list_2[i].check.grid(row = i, column = 1, sticky = "w", padx = 5)
        for i in range(len(self.truck_mod_list_1)):
            self.truck_mod_list_1[i].check.grid(row = i, column = 0, sticky = "w", padx = 5)
        for i in range(len(self.truck_mod_list_2)):
            self.truck_mod_list_2[i].check.grid(row = i, column = 1, sticky = "w", padx = 5)
        for i in range(len(self.trailer_list_1)):
            self.trailer_list_1[i].check.grid(row = i, column = 0, sticky = "w", padx = 5)
        for i in range(len(self.trailer_list_2)):
            self.trailer_list_2[i].check.grid(row = i, column = 1, sticky = "w", padx = 5)
        for i in range(len(self.trailer_mod_list_1)):
            self.trailer_mod_list_1[i].check.grid(row = i, column = 0, sticky = "w", padx = 5)
        for i in range(len(self.trailer_mod_list_2)):
            self.trailer_mod_list_2[i].check.grid(row = i, column = 1, sticky = "w", padx = 5)

        self.panel_pack_link_truck.grid(row = len(self.truck_mod_list_2), column = 1, sticky = "w", padx = 5)
        self.panel_pack_link_trailer.grid(row = len(self.trailer_mod_list_2), column = 1, sticky = "w", padx = 5)

        self.change_displayed_vehicle_dropdown()
        self.update_total_vehicles_supported()

    def toggle_unlock_level(self):
        if self.panel_ingame_default_variable.get():
            self.panel_ingame_unlock_input.state(["disabled"])
        else:
            self.panel_ingame_unlock_input.state(["!disabled"])

    def load_list_of_vehicles(self, game):
        complete_list = []
        for file_name in os.listdir("library/vehicles/{}".format(game)):
            complete_list.append(VehSelection(game, file_name))
        truck_list = []
        truck_mod_list = []
        trailer_list = []
        trailer_mod_list = []
        for veh in complete_list:
            if veh.trailer:
                if veh.mod:
                    veh.check = ttk.Checkbutton(self.tab_trailer_mods, text = veh.name, command = lambda : self.update_total_vehicles_supported())
                    veh.check.state(["!alternate","!selected"])
                    trailer_mod_list.append(veh)
                else:
                    veh.check = ttk.Checkbutton(self.tab_trailers, text = veh.name, command = lambda : self.update_total_vehicles_supported())
                    veh.check.state(["!alternate","!selected"])
                    trailer_list.append(veh)
            else:
                if veh.mod:
                    veh.check = ttk.Checkbutton(self.tab_truck_mods, text = veh.name, command = lambda : self.update_total_vehicles_supported())
                    veh.check.state(["!alternate","!selected"])
                    truck_mod_list.append(veh)
                else:
                    veh.check = ttk.Checkbutton(self.tab_trucks, text = veh.name, command = lambda : self.update_total_vehicles_supported())
                    veh.check.state(["!alternate","!selected"])
                    truck_list.append(veh)
        return (truck_list, truck_mod_list, trailer_list, trailer_mod_list)

    def change_displayed_vehicle_dropdown(self, *args):
        type = self.panel_single_type_variable.get()
        self.panel_single_vehicle_variable.set("")
        new_values = []
        if type == "Truck":
            for veh in self.truck_list: new_values.append(veh.name)
        elif type == "Truck Mod":
            for veh in self.truck_mod_list: new_values.append(veh.name)
        elif type == "Trailer":
            for veh in self.trailer_list: new_values.append(veh.name)
        elif type == "Trailer Mod":
            for veh in self.trailer_mod_list: new_values.append(veh.name)
        self.panel_single_vehicle_dropdown.config(values = new_values)

        if type in ["Truck Mod", "Trailer Mod"]:
            self.panel_single_link.grid(row = 4, column = 0, pady = 5, padx = 5, sticky = "w")
        else:
            self.panel_single_link.grid_forget()

    def update_total_vehicles_supported(self):
        self.total_vehicles = 0
        for veh in self.truck_list_1 + self.truck_list_2 + self.truck_mod_list_1 + self.truck_mod_list_2 + self.trailer_list_1 + self.trailer_list_2 + self.trailer_mod_list_1 + self.trailer_mod_list_2:
            if "selected" in veh.check.state():
                self.total_vehicles += 1
        self.panel_vehicles_pack.configure(text = "Vehicles Supported ({})".format(self.total_vehicles))

    def verify_all_inputs(self):
        inputs_verified = True
        all_errors = []

        # mod info
        if len(self.panel_mod_name_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No mod name", "Please enter a mod name"])
        if "\"" in self.panel_mod_name_variable.get():
            inputs_verified = False
            all_errors.append(["Quotation marks in mod name", "Mod names cannot contain \""])
        if len(self.panel_mod_version_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No mod version", "Please enter a mod version"])
        if "\"" in self.panel_mod_version_variable.get():
            inputs_verified = False
            all_errors.append(["Quotation marks in mod version", "Mod versions cannot contain \""])
        if len(self.panel_mod_author_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No mod author", "Please enter a mod author"])
        if "\"" in self.panel_mod_author_variable.get():
            inputs_verified = False
            all_errors.append(["Quotation marks in mod author", "Mod authors cannot contain \""])

        # in-game paintjob info
        if len(self.panel_ingame_name_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No paintjob name", "Please enter a paintjob name"])
        if "\"" in self.panel_ingame_name_variable.get():
            inputs_verified = False
            all_errors.append(["Quotation marks in paintjob name", "Paintjob names cannot contain \""])
        if len(self.panel_ingame_price_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No paintjob price", "Please enter a paintjob price"])
        if not re.match("^[0-9]*$", self.panel_ingame_price_variable.get()):
            inputs_verified = False
            all_errors.append(["Invalid paintjob price", "Paintjob price must be a number, with no decimal points, currency signs, spaces or letters"])
        if not self.panel_ingame_default_variable.get():
            if len(self.panel_ingame_unlock_variable.get()) < 1:
                inputs_verified = False
                all_errors.append(["No unlock level", "Please enter an unlock level"])
            if not re.match("^[0-9]*$", self.panel_ingame_unlock_variable.get()):
                inputs_verified = False
                all_errors.append(["Invalid unlock level", "Unlock level must be a number, with no other characters or spaces"])

        # internal paintjob info
        if len(self.panel_internal_name_variable.get()) < 1:
            inputs_verified = False
            all_errors.append(["No internal name", "Please enter an internal name"])
        if len(self.panel_internal_name_variable.get()) > self.internal_name_length:
            inputs_verified = False
            all_errors.append(["Internal name too long", "Internal name too long, it must be {} characters or fewer".format(self.internal_name_length)])
        if not re.match("^[0-9a-z\_]*$", self.panel_internal_name_variable.get()):
            inputs_verified = False
            all_errors.append(["Invalid internal name", "Internal name must only contain lowercase letters, numbers and underscores"]) # I think uppercase letters might work, but no paintjobs in the base game/DLCs use them, so best practice to avoid them

        # vehicle selection
        if self.tab_paintjob_variable.get() == "pack":
            if self.total_vehicles < 1:
                inputs_verified = False
                all_errors.append(["No vehicles selected", "Please select at least one truck, trailer or truck mod"])
        elif self.tab_paintjob_variable.get() == "single":
            if self.panel_single_vehicle_variable.get() == "":
                inputs_verified = False
                all_errors.append(["No vehicle selected", "Please select a vehicle to support"])

        if inputs_verified:
            self.ask_save_location()
        else:
            if len(all_errors) == 1:
                messagebox.showerror(title = all_errors[0][0], message = all_errors[0][1])
            elif len(all_errors) > 1:
                total_message = ""
                for error in all_errors:
                    total_message += error[0]+":\n"
                    total_message += error[1]+"\n\n"
                messagebox.showerror(title = "{} errors".format(len(all_errors)), message = total_message)

    def ask_save_location(self):
        save_directory = filedialog.askdirectory(title = "Save Mod (subfolder will be created)", initialdir = desktop_path)
        if save_directory != "":
            output_path = save_directory + "/Paintjob Packer Output"
            folder_clear = True
            if os.path.exists(output_path):
                if len(os.listdir(output_path)) > 0:
                    folder_clear = False # I don't want to be on the receiving end of an irate user who lost their important report the night before it was due, because they happened to store it in the paintjob packer folder
                    messagebox.showerror(title = "Output folder not clear", message = "A folder called \"Paintjob Packer Output\" already exists in the directory that you chose, and it contains files.\n\nPlease delete the \"Paintjob Packer Output\" folder, or delete everything inside it.")
            if folder_clear:
                self.make_paintjob(output_path)

    def make_paintjob(self, output_path):
        truck_list = []
        for veh in self.truck_list_1 + self.truck_list_2:
            if "selected" in veh.check.state():
                truck_list.append(veh)
        truck_mod_list = []
        for veh in self.truck_mod_list_1 + self.truck_mod_list_2:
            if "selected" in veh.check.state():
                truck_mod_list.append(veh)
        trailer_list = []
        for veh in self.trailer_list_1 + self.trailer_list_2:
            if "selected" in veh.check.state():
                trailer_list.append(veh)
        trailer_mod_list = []
        for veh in self.trailer_mod_list_1 + self.trailer_mod_list_2:
            if "selected" in veh.check.state():
                trailer_mod_list.append(veh)

        vehicle_list = []
        for veh in truck_list + truck_mod_list + trailer_list + trailer_mod_list:
            vehicle_list.append(pj.Vehicle(veh.file_name, self.tab_game_variable.get()))

        single_veh_name = self.panel_single_vehicle_variable.get()
        for veh in self.truck_list_1 + self.truck_list_2 + self.truck_mod_list_1 + self.truck_mod_list_2 + self.trailer_list_1 + self.trailer_list_2 + self.trailer_mod_list_1 + self.trailer_mod_list_2:
            if veh.name == single_veh_name:
                single_veh = pj.Vehicle(veh.file_name, self.tab_game_variable.get())

        game = self.tab_game_variable.get()

        mod_name = self.panel_mod_name_variable.get()
        mod_version = self.panel_mod_version_variable.get()
        mod_author = self.panel_mod_author_variable.get()

        ingame_name = self.panel_ingame_name_variable.get()
        ingame_price = self.panel_ingame_price_variable.get()
        if self.panel_ingame_default_variable.get():
            unlock_level = 0
        else:
            unlock_level = self.panel_ingame_unlock_variable.get()

        internal_name = self.panel_internal_name_variable.get()
        num_of_paintjobs = self.tab_paintjob_variable.get()
        workshop_upload = self.panel_internal_workshop_variable.get()

        cabins_supported = self.panel_internal_supported_variable.get()
        cabin_handling = self.panel_internal_handling_variable.get()
        using_unifier = self.panel_internal_unifier_variable.get()

        if cabins_supported == "Largest cabin only": # this shouldn't be needed, but it might be, so I'm doing it for safe measure
            cabin_handling = "Combined paintjob"
        if cabin_handling == "Combined paintjob":
            using_unifier = False

        out_path = output_path+"/"+mod_name

        if num_of_paintjobs == "single":
            if single_veh.trailer:
                if single_veh.mod:
                    trailer_mod_list.append(single_veh)
                else:
                    trailer_list.append(single_veh)
            else:
                if single_veh.mod:
                    truck_mod_list.append(single_veh)
                else:
                    truck_list.append(single_veh)
            vehicle_list.append(single_veh)

        if not os.path.exists(out_path):
            os.makedirs(out_path)

        if workshop_upload:
            if not os.path.exists(output_path+"/Workshop uploading"):
                os.makedirs(output_path+"/Workshop uploading")

        self.loading_value.set(0.0)
        total_things_to_load = len(vehicle_list) + 1
        if using_unifier:
            total_things_to_load += 1
        self.loading_bar.config(maximum = float(total_things_to_load))
        self.loading_window.state("normal")
        self.loading_window.lift()

        self.loading_value.set(self.loading_value.get()+1.0)
        self.loading_current.set("Loose files")

        pj.make_manifest_sii(out_path, mod_version, mod_name, mod_author)

        pj.copy_mod_manager_image(out_path)

        pj.make_description(out_path, truck_list, truck_mod_list, trailer_list, trailer_mod_list, num_of_paintjobs)

        pj.make_material_folder(out_path)

        pj.copy_paintjob_icon(out_path, internal_name)

        pj.make_paintjob_icon_tobj(out_path, internal_name)

        pj.make_paintjob_icon_mat(out_path, internal_name)

        for veh in vehicle_list:
            self.loading_value.set(self.loading_value.get()+1.0)
            self.loading_current.set(veh.name)
            pj.make_def_folder(out_path, veh)
            pj.make_settings_sui(out_path, veh, internal_name, ingame_name, ingame_price, unlock_level)
            pj.make_vehicle_folder(out_path, veh, internal_name)
            if cabin_handling == "Combined paintjob" or veh.type == "trailer_owned" or not veh.separate_paintjobs:
                paintjob_name = internal_name
                pj.make_def_sii(out_path, veh, paintjob_name, internal_name)
                pj.copy_main_dds(out_path, veh, internal_name, paintjob_name, using_unifier)
                pj.make_main_tobj(out_path, veh, internal_name, paintjob_name, using_unifier)
                if veh.uses_accessories:
                    pj.make_accessory_sii(out_path, veh, internal_name, paintjob_name)
            elif cabins_supported == "Largest cabin only":
                paintjob_name = internal_name
                pj.make_def_sii(out_path, veh, paintjob_name, internal_name, veh.cabins["a"], "a", True)
                pj.copy_main_dds(out_path, veh, internal_name, paintjob_name, using_unifier)
                pj.make_main_tobj(out_path, veh, internal_name, paintjob_name, using_unifier)
                if veh.uses_accessories:
                    pj.make_accessory_sii(out_path, veh, internal_name, paintjob_name)
            else:
                for cab_size in veh.cabins:
                    paintjob_name = internal_name + "_" + cab_size
                    pj.make_def_sii(out_path, veh, paintjob_name, internal_name, veh.cabins[cab_size], cab_size)
                    pj.copy_main_dds(out_path, veh, internal_name, paintjob_name, using_unifier)
                    pj.make_main_tobj(out_path, veh, internal_name, paintjob_name, using_unifier)
                    if veh.uses_accessories:
                        pj.make_accessory_sii(out_path, veh, internal_name, paintjob_name)
            if veh.uses_accessories:
                pj.copy_accessory_dds(out_path, veh, internal_name)
                pj.make_accessory_tobj(out_path, veh, internal_name)

        if using_unifier:
            self.loading_value.set(self.loading_value.get()+1.0)
            self.loading_current.set("Cabin unifier")
            if using_executable:
                unifier_name = "Cabin Unifier.exe"
            else:
                unifier_name = "unifier.py"
            pj.make_unifier_ini(out_path, internal_name, vehicle_list, unifier_name)

        if workshop_upload:
            pj.copy_versions_sii(output_path+"/Workshop uploading")
            pj.copy_workshop_image(output_path)
            self.make_workshop_readme(truck_list, truck_mod_list, trailer_list, trailer_mod_list, num_of_paintjobs)

        self.make_readme_file(output_path, internal_name, using_unifier, game, mod_name)

        self.loading_current.set("Complete!")
        self.loading_window.state("withdrawn")

        exit_now = messagebox.showinfo(title = "Mod generation complete", message = "Your mod has been generated successfully! It's been placed in the directory you chose, inside a folder called Paintjob Packer Output.\n\nYour mod is not yet finished, refer to the text file inside the folder for instructions. There is also a guide on the GitHub page.\n\nThanks for using Paintjob Packer! :)")
        sys.exit()

    def make_readme_file(self, output_path, internal_name, using_unifier, game, mod_name):
        file = open(output_path+"/How to complete your mod.txt", "w")
        file.write("Thanks for using Paintjob Packer!\n")
        file.write("\n")
        file.write("At the moment the \"{}\" folder contains a mod with placeholder textures and images, you now need to replace those with your own files.\n".format(mod_name))
        file.write("\n")
        file.write("For more info, see the guide on the GitHub page: {}\n".format(github_link))
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("To test your mod, move the \"{}\" folder (the folder itself, not just the files inside it) to your mod folder:\n".format(mod_name))
        if game == "ets":
            game_name = "Euro Truck Simulator 2"
        elif game == "ats":
            game_name = "American Truck Simulator"
        if sys.platform.startswith("win"):
            mod_folder_location = "C:\\Users\\(username)\\Documents\\{}\\mod\n".format(game_name)
        elif sys.platform.startswith("darwin"):
            mod_folder_location = "/Users/(username)/Library/Application Support/{}/mod\n".format(game_name)
        elif sys.platform.startswith("linux"):
            mod_folder_location = "/home/(username)/.local/share/{}/mod\n".format(game_name)
        file.write(mod_folder_location)
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("== Mod manager image ==\n")
        file.write("mod_manager_image.jpg\n")
        file.write("276 x 162 JPEG image\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("== Mod manager description ==\n")
        file.write("mod_manager_description.txt\n")
        file.write("This contains an auto-generated list of vehicles supported by your mod.\n")
        file.write("You may want to add some extra description to it, maybe explaining your mod a bit.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("== In-game paintjob icon ==\n")
        file.write("material/ui/accessory/{}_icon.dds\n".format(internal_name))
        file.write("256 x 64 DDS image (saved in DXT5 format with mipmaps), see the placeholder for recommended size/shape.\n")
        file.write("This is the icon you see when you go to buy your paintjob in-game.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("== Vehicle textures ==\n")
        file.write("All of the .dds files in:")
        file.write("vehicle/truck/upgrade/paintjob/{}/<vehicle>/\n".format(internal_name))
        file.write("and/or\n")
        file.write("vehicle/trailer_owned/upgrade/paintjob/{}/<vehicle>/\n".format(internal_name))
        file.write("DDS images (saved in DXT5 format with mipmaps), height and width need to be powers of 2 (e.g. 16, 64, 1024, 2048, 4096)\n")
        file.write("\n")
        file.write("The \"cabin\" images in the truck folders are the main files of your paintjob,\n")
        file.write("that's where you'll put the designs you make based off templates. All other\n")
        file.write("images refer to accessory parts, which are found on trailers and some newer\n")
        file.write("trucks. You can either create full-on textures for them using templates, or\n")
        file.write("simply re-colour the placeholder files. For example, if you want to make one\n")
        file.write("of the accessories red, you don't have to download a template for that specific\n")
        file.write("part, you can just take the existing 4x4 file and make it red instead of white.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        if using_unifier:
            file.write("Note: you don't have to change any .mat files, or anything in the def folder.\n")
            file.write("\n")
            file.write("\n")
            file.write("\n")
            file.write("Since you're using the cabin unifier, you will need to change cabin .tobj files\n")
            file.write("to add additional textures. If your cabin_a.dds doesn't work on Cabin B of a truck,\n")
            file.write("for example, you'll need to create a second .dds file called cabin_b.dds, then edit\n")
            file.write("cabin_b.tobj to point to it. You can link multiple .tobjs to the same .dds, e.g. you\n")
            file.write("could also point cabin_c.tobj to cabin_b.dds. After you've added all the extra files\n")
            file.write("you need, run the Cabin Unifier. If it completes successfully you can delete it and\n")
            file.write("unifier.ini, if not it will tell you what went wrong.\n")
        else:
            file.write("Note: you don't have to change any .tobj files, any .mat files, or anything in the def folder\n")
        file.close()

    def make_workshop_readme(self, truck_list, truck_mod_list, trailer_list, trailer_mod_list, num_of_paintjobs):
        file = open(output_path+"/How to upload your mod to Steam Workshop.txt", "w")
        file.write("In order to upload your mod to Steam Workshop, you'll need to use the SCS Workshop Uploader, which only runs on Windows.\n")
        file.write("To download it, you'll need to own ETS 2 or ATS on Steam. Then go to View > Hidden Games, tick \"Tools\" in the dropdown on\n")
        file.write("the left, then scroll down to find the SCS Workshop Uploader.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("Once your mod is complete, compress all of its files into a zip file. Name it universal.zip, and move it to the \"Workshop\n")
        file.write("uploading\" folder, which should already contain a file called versions.sii.\n")
        file.write("\n")
        file.write("You'll also need to create a workshop image, which is a 640 x 360 JPEG, that will represent your mod when people search\n")
        file.write("for it on the Workshop. There is a placeholder Workshop image.jpg with the correct dimensions.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("Open the SCS Workshop Uploader and select your game. In the Mod data section browse to the \"Workshop uploading\" folder\n")
        file.write("and your workshop image. Enter your mod name, change the visibility to Public if you wish, then enter your description.\n")
        file.write("There's an automatically generated Workshop description at the bottom of this text file that you can copy-paste. On the right,\n")
        file.write("select \"Truck parts\" under Type, then scroll down and check \"Paintjobs\". Select all the brands applicable to your mod, and\n")
        file.write("enter a change note if you wish.\n")
        file.write("\n")
        file.write("When you upload your mod, assuming everything else is okay, you'll get a warning mentioning display_name. This is normal, and it\n")
        file.write("appears because Workshop mods don't use the mod name that you specified when initially generating the mod files, but instead use\n")
        file.write("the name that you enter in the Workshop Uploader. This warning can be safely ignored.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        file.write("Below is a workshop description. It's identical to the mod manager description, but with clickable links for any modded vehicles you support.\n")
        file.write("\n")
        file.write("\n")
        file.write("\n")
        if num_of_paintjobs == "single":
            for veh in truck_list + trailer_list:
                file.write("This paintjob supports the {}\n".format(veh.name))
            for veh in truck_mod_list + trailer_mod_list:
                file.write("This paintjob supports {}'s [url={}]{}[/url]\n".format(veh.mod_author, veh.mod_link, veh.name))
        else:
            if len(truck_list) + len(truck_mod_list) > 0:
                file.write("Trucks supported:\n")
                for veh in truck_list:
                    file.write(veh.name+"\n")
                for veh in truck_mod_list:
                    file.write("{}'s [url={}]{}[/url]\n".format(veh.mod_author, veh.mod_link, veh.name))
                file.write("\n")
            if len(trailer_list) + len(trailer_mod_list) > 0:
                file.write("Trailers supported:\n")
                for veh in trailer_list:
                    file.write(veh.name+"\n")
                for veh in trailer_mod_list:
                    file.write("{}'s [url={}]{}[/url]\n".format(veh.mod_author, veh.mod_link, veh.name))
        file.close()

class VehSelection:

    def __init__(self, _game, _file_name):
        self.file_name = _file_name
        self.game = _game
        veh_ini = configparser.ConfigParser(allow_no_value = True)
        veh_ini.read("library/vehicles/{}/{}".format(self.game, self.file_name), encoding="utf-8")
        self.name = veh_ini["vehicle info"]["name"]
        self.trailer = veh_ini["vehicle info"].getboolean("trailer")
        self.mod = veh_ini["vehicle info"].getboolean("mod")
        self.mod_author = veh_ini["vehicle info"]["mod author"]
        self.mod_link = veh_ini["vehicle info"]["mod link"]

def show_unhandled_error(error_type, error_message, error_traceback):
    # there's probably a neater way to do this, but this works
    messagebox.showerror(title = "Unhandled exception", message = "Something has gone very wrong!\n\nPlease send this error message (the entire thing, including the lengthy traceback) to the developer!\n\nError type: {}\nError: {}\n\nTraceback:\n{}".format(error_type.__name__, str(error_message), "\n".join(traceback.format_list(traceback.extract_tb(error_traceback)))))


def main():
    root = tk.Tk()
    root.title("Paintjob Packer v{}".format(version))
    root.iconphoto(True, tk.PhotoImage(file = "library/packer images/icon.png"))
    root.resizable(False, False)
    root.report_callback_exception = show_unhandled_error
    packer = PackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
