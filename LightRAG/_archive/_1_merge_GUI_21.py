import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import asyncio
import requests
import os
import json
import platform # Import platform module

from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc
from llama_index.embeddings.openai import OpenAIEmbedding

# Configuration
WORKING_DIR = "_0_jack_work_dir_01"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 3072))
API_KEY = os.getenv("EMBEDDING_BINDING_API_KEY")
MAX_TOKEN_SIZE = int(os.getenv("MAX_TOKEN_SIZE", 8192))

# --- LightRAG Server API Configuration ---
LIGHTRAG_SERVER_URL = "http://localhost:9621" # Default LightRAG server address


async def initialize_rag():
    embed_model = OpenAIEmbedding(
        model=EMBEDDING_MODEL,
        api_key=API_KEY,
        dimensions=EMBEDDING_DIM
    )
    async def async_embedding_func(texts):
        return embed_model.get_text_embedding_batch(texts)
    embedding_func = EmbeddingFunc(
        embedding_dim=EMBEDDING_DIM,
        max_token_size=MAX_TOKEN_SIZE,
        func=async_embedding_func
    )
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=embedding_func,
        llm_model_func=gpt_4o_mini_complete
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

def fetch_entities():
    try:
        response = requests.get(f"{LIGHTRAG_SERVER_URL}/graph/label/list")
        response.raise_for_status()
        return sorted(response.json(), key=lambda x: x.lower())
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", "Could not connect to LightRAG server. Is it running?")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch entities from server: {e}")
        return []

def fetch_entity_details(label):
    try:
        response = requests.get(f"{LIGHTRAG_SERVER_URL}/graphs?label={label}&max_depth=1&max_nodes=1000")
        response.raise_for_status()
        data = response.json()
        for node in data.get("nodes", []):
            if node.get("id") == label:
                return node["properties"].get("description", "No description found."), node["properties"].get("entity_type", ""), node["properties"].get("source_id", "")
        return "No description found.", "", ""
    except requests.exceptions.ConnectionError:
        # Do not show a messagebox here, as it can be called frequently during updates
        print("Connection Error: Could not connect to LightRAG server to fetch entity details.")
        return "Error: Server not reachable.", "", ""
    except Exception as e:
        print(f"Error fetching entity details for {label}: {e}")
        return f"Error: {e}", "", ""

# Function to trigger server scan
def trigger_server_scan():
    try:
        print("Attempting to trigger LightRAG server scan...")
        response = requests.post(f"{LIGHTRAG_SERVER_URL}/documents/scan")
        response.raise_for_status()
        print("LightRAG server scan triggered successfully.")
        return True
    except requests.exceptions.ConnectionError:
        messagebox.showwarning("Server Not Running", "Could not connect to LightRAG server to trigger scan. Please ensure the server is running.")
        return False
    except requests.exceptions.HTTPError as e:
        messagebox.showwarning("API Error", f"Failed to trigger LightRAG server scan: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        messagebox.showwarning("Error", f"An unexpected error occurred while triggering LightRAG server scan: {e}")
        return False


class MergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LightRAG Entity Merger")
        self.entity_list = fetch_entities()
        self.filtered_entity_list = self.entity_list.copy()
        
        # Store all BooleanVars persistently
        self.all_check_vars = {entity: tk.BooleanVar() for entity in self.entity_list}

        self.description_windows = {} # This seems to be unused, description_frames is used
        self.description_frames = {} # Store description frames in right panel
        # self.selected_entities = {} # This can be removed, we use all_check_vars
        self.entity_data = {} # Cache for entity descriptions, types, source IDs
        self.config_file = "merge_gui_config.json"
        
        self.load_window_config()
        self.setup_main_window()
        
        # Variables for entity selection
        self.check_vars = {} # This will only hold references to visible checkboxes
        self.first_entity_var = tk.StringVar()
        
        self.create_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_window_config(self):
        """Load window size and position from config file"""
        self.window_config = {
            "geometry": "1200x800",
            "state": "normal",
            "paned_position": 300
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.window_config.update(saved_config)
            except:
                pass

    def set_initial_paned_position(self):
        """Set the initial position of the paned window splitter at 25% from left"""
        try:
            self.root.update_idletasks()
            window_width = self.paned_window.winfo_width()
            
            if window_width > 100:
                position = int(window_width * 0.25)
            else:
                position = 300
            
            self.paned_window.sashpos(0, position)
        except Exception as e:
            self.paned_window.sashpos(0, 300)

    def save_window_config(self):
        """Save current window size and position to config file"""
        try:
            geometry = self.root.geometry()
            state = self.root.state()
            paned_position = self.paned_window.sash_coord(0)[0]
            
            config = {
                "geometry": geometry,
                "state": state,
                "paned_position": paned_position
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass

    def setup_main_window(self):
        """Set up the main window with saved configuration"""
        self.root.geometry(self.window_config["geometry"])
        
        if platform.system() == "Windows":
            try:
                self.root.state('zoomed')
            except tk.TclError:
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        elif platform.system() == "Linux":
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        else:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_ui(self):
        """Create the main user interface"""
        self.paned_window = ttk.PanedWindow(self.root, orient="horizontal")
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        
        self.left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_panel, weight=1)
        
        self.right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_panel, weight=3)
        
        self.root.after(10, self.set_initial_paned_position)
        
        self.create_right_panel()
        self.create_left_panel()

    def create_left_panel(self):
        """Create the left panel with filter and entity list"""
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        top_controls_frame = ttk.Frame(self.left_panel)
        top_controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        top_controls_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(top_controls_frame, text="Filter:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(top_controls_frame, textvariable=self.filter_var)
        self.filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.filter_var.trace('w', self.on_filter_change)
        
        self.clear_filter_button = ttk.Button(top_controls_frame, text="✕", width=3, command=self.clear_filter)
        self.clear_filter_button.grid(row=0, column=2, padx=(0,5))

        action_buttons_frame = ttk.Frame(top_controls_frame)
        action_buttons_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5,0))
        action_buttons_frame.grid_columnconfigure(0, weight=1)
        action_buttons_frame.grid_columnconfigure(1, weight=1)

        self.show_selected_button = ttk.Button(action_buttons_frame, text="Selected Only", command=self.show_selected_only)
        self.show_selected_button.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.clear_all_button = ttk.Button(action_buttons_frame, text="Clear All", command=self.clear_all_selections)
        self.clear_all_button.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        header_frame = ttk.Frame(self.left_panel)
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Label(header_frame, text="Desc", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="First", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="Select Entities", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        
        content_frame = ttk.Frame(self.left_panel)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        self.toggle_desc_button = ttk.Button(content_frame, text="", command=self.toggle_descriptions, width=3)
        self.toggle_desc_button.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.scrollable_frame.grid_columnconfigure(0, weight=0)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        def _on_mousewheel(event):
            try:
                if platform.system() == "Windows":
                    if hasattr(event, 'delta') and event.delta:
                        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif platform.system() == "Darwin":
                    if hasattr(event, 'delta') and event.delta:
                        self.canvas.yview_scroll(int(-1 * event.delta), "units")
                else:
                    if event.num == 4:
                        self.canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.canvas.yview_scroll(1, "units")
                    elif hasattr(event, 'delta') and event.delta:
                        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
            return "break"

        scroll_events = []
        if platform.system() == "Windows":
            scroll_events = ["<MouseWheel>", "<Shift-MouseWheel>"]
        elif platform.system() == "Darwin":
            scroll_events = ["<MouseWheel>", "<Button-4>", "<Button-5>"]
        else:
            scroll_events = ["<Button-4>", "<Button-5>", "<MouseWheel>"]

        for event in scroll_events:
            try:
                self.canvas.bind(event, _on_mousewheel)
            except:
                pass

        def on_canvas_enter(event):
            self.canvas.focus_set()

        def on_canvas_leave(event):
            self.root.focus_set()

        self.canvas.bind("<Enter>", on_canvas_enter)
        self.canvas.bind("<Leave>", on_canvas_leave)
        self.canvas.config(takefocus=True)

        def _on_key(event):
            if event.keysym == "Up":
                self.canvas.yview_scroll(-1, "units")
                return "break"
            elif event.keysym == "Down":
                self.canvas.yview_scroll(1, "units")
                return "break"
            elif event.keysym == "Page_Up":
                self.canvas.yview_scroll(-5, "units")
                return "break"
            elif event.keysym == "Page_Down":
                self.canvas.yview_scroll(5, "units")
                return "break"

        self.canvas.bind("<Key>", _on_key)
        self.canvas.bind("<Button-1>", lambda e: e.widget.focus_set())
        
        self.create_entity_list()

    def on_filter_change(self, *args):
        """Handle filter text changes, preserving selections."""
        filter_text = self.filter_var.get().lower()
        
        if not filter_text:
            self.filtered_entity_list = self.entity_list.copy()
        else:
            self.filtered_entity_list = [
                entity for entity in self.entity_list 
                if filter_text in entity.lower()
            ]
        
        self.create_entity_list()

    def clear_filter(self):
        """Clear the filter and show all entities."""
        self.filter_var.set("")
        # The on_filter_change callback will handle recreating the list.

    def show_selected_only(self):
        """Filters the list to show only selected entities."""
        selected_entities = [label for label, var in self.all_check_vars.items() if var.get()]
        if not selected_entities:
            messagebox.showinfo("No Selection", "No entities are currently selected.")
            # If no items are selected, effectively clear the filter and show all,
            # or just show an empty list based on preference. Here, we show info and return.
            self.filter_var.set("") # Clear any existing filter text
            self.filtered_entity_list = self.entity_list.copy() # Show all if nothing is selected
            self.create_entity_list()
            return
        
        self.filter_var.set("") # Clear any existing filter text
        self.filtered_entity_list = sorted(selected_entities, key=lambda x: x.lower())
        self.create_entity_list()

    def clear_all_selections(self):
        """Clears all checkboxes and then shows all entities."""
        for var in self.all_check_vars.values():
            var.set(False)
        self.filter_var.set("") # Clear filter to show all
        self.filtered_entity_list = self.entity_list.copy()
        self.create_entity_list()
        self.first_entity_var.set("") # Also clear the first entity radio button

    def create_right_panel(self):
        """Create the right panel with controls and description area"""
        self.right_panel.grid_rowconfigure(1, weight=1) 
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        control_frame = ttk.Frame(self.right_panel)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(control_frame, text="Target Entity:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.target_entry = ttk.Combobox(control_frame, values=[], width=40)
        self.target_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(control_frame, text="Merge Strategy - Description:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.strategy_desc = ttk.Combobox(control_frame, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_desc.set("join_unique")
        self.strategy_desc.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(control_frame, text="Merge Strategy - Source ID:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.strategy_srcid = ttk.Combobox(control_frame, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_srcid.set("join_unique")
        self.strategy_srcid.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(control_frame, text="Entity Type:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entity_type = ttk.Combobox(control_frame, values=[], width=37)
        self.entity_type.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        info_label = ttk.Label(control_frame, text="Note: 'First Entity' is used when 'keep_first' strategy is selected", 
                                 font=("TkDefaultFont", 8), foreground="gray", wraplength=300)
        info_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        self.merge_button = ttk.Button(control_frame, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=5, column=1, sticky="e", padx=5, pady=10)

        self.description_area = ttk.Frame(self.right_panel)
        self.description_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.description_area.grid_columnconfigure(0, weight=1)
        self.description_area.grid_rowconfigure(0, weight=1)

        self.desc_canvas = tk.Canvas(self.description_area)
        self.desc_scrollbar = ttk.Scrollbar(self.description_area, orient="vertical", command=self.desc_canvas.yview)
        self.desc_scrollable_frame = ttk.Frame(self.desc_canvas)
        
        self.desc_scrollable_frame.bind("<Configure>", lambda e: self.desc_canvas.configure(scrollregion=self.desc_canvas.bbox("all")))
        self.desc_canvas.create_window((0, 0), window=self.desc_scrollable_frame, anchor="nw")
        self.desc_canvas.configure(yscrollcommand=self.desc_scrollbar.set)
        
        self.desc_canvas.grid(row=0, column=0, sticky="nsew")
        self.desc_scrollbar.grid(row=0, column=1, sticky="ns")

        def _on_desc_mousewheel(event):
            try:
                if platform.system() == "Windows":
                    if hasattr(event, 'delta') and event.delta:
                        self.desc_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif platform.system() == "Darwin":
                    if hasattr(event, 'delta') and event.delta:
                        self.desc_canvas.yview_scroll(int(-1 * event.delta), "units")
                else:
                    if event.num == 4:
                        self.desc_canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.desc_canvas.yview_scroll(1, "units")
                    elif hasattr(event, 'delta') and event.delta:
                        self.desc_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
            return "break"

        desc_scroll_events = []
        if platform.system() == "Windows":
            desc_scroll_events = ["<MouseWheel>", "<Shift-MouseWheel>"]
        elif platform.system() == "Darwin":
            desc_scroll_events = ["<MouseWheel>", "<Button-4>", "<Button-5>"]
        else:
            desc_scroll_events = ["<Button-4>", "<Button-5>", "<MouseWheel>"]

        for event in desc_scroll_events:
            try:
                self.desc_canvas.bind(event, _on_desc_mousewheel)
            except:
                pass

    def create_entity_list(self):
        """Create the entity list with radio buttons and checkboxes, preserving selection state."""
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Clear the mapping for currently visible checkboxes (these will be recreated)
        self.check_vars.clear() 
        
        # Create entity rows with radio buttons and checkboxes side by side using filtered list
        for i, ent in enumerate(self.filtered_entity_list):
            # Radio button in column 0 of the scrollable frame
            rb = ttk.Radiobutton(self.scrollable_frame, text="", variable=self.first_entity_var, value=ent)
            rb.grid(row=i, column=0, padx=(5, 2), pady=1, sticky="w")
            
            # Checkbox in column 1 of the scrollable frame
            # Retrieve the BooleanVar from all_check_vars to preserve its state
            var = self.all_check_vars.get(ent)
            if var is None: # This should ideally not happen if self.all_check_vars is initialized with all entities
                var = tk.BooleanVar()
                self.all_check_vars[ent] = var # Add it if somehow missing
            
            cb = ttk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_selection)
            cb.grid(row=i, column=1, padx=(2, 5), pady=1, sticky="w")
            self.check_vars[ent] = var # Store reference to the visible checkbox's var
        
        # Restore first entity selection if it's still in the filtered list
        current_first_entity = self.first_entity_var.get()
        if current_first_entity and current_first_entity in self.filtered_entity_list:
            self.first_entity_var.set(current_first_entity)
        else:
            self.first_entity_var.set("")
        
        # Update the selection to refresh target entity and type dropdowns
        self.update_selection()

    def update_selection(self):
        """Update target entity combobox and entity type combobox based on current selections."""
        # Get all selected entities from the persistent storage
        selected = [label for label, var in self.all_check_vars.items() if var.get()]
        
        if not hasattr(self, 'target_entry'):
            return
            
        self.target_entry["values"] = selected
        
        # Fetch entity details for selected entities and collect their types
        types = set()
        for label in selected:
            if label not in self.entity_data:
                # Fetch details if not already cached
                desc, typ, srcid = fetch_entity_details(label)
                self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
            
            # Add the type to the set if it's not empty/error
            if self.entity_data[label]["type"] and not self.entity_data[label]["type"].startswith("Error:"):
                types.add(self.entity_data[label]["type"])
        
        # Update the entity_type combobox
        current_entity_type = self.entity_type.get() # Store current selection
        self.entity_type["values"] = sorted(list(types))
        
        # Try to restore previous selection if it's still valid
        if current_entity_type and current_entity_type in self.entity_type["values"]:
            self.entity_type.set(current_entity_type)
        else:
            self.entity_type.set("") # Clear if previous selection is no longer valid or no items selected
        
        # Clear target if current value is no longer in selected list
        if self.target_entry.get() not in selected:
            self.target_entry.set("")
        
        # Clear first entity selection if the selected entity is no longer in the selected list
        if self.first_entity_var.get() and self.first_entity_var.get() not in selected:
            self.first_entity_var.set("")


    def calculate_tile_layout(self, available_width, available_height, num_items, min_height=200):
        """Calculate optimal tiling layout for description frames."""
        if num_items == 0:
            return 0, 0, 0, 0
        
        effective_min_width = max(300, (available_width // 2) - 10) 
        
        cols = max(1, available_width // effective_min_width)
            
        if available_width >= 2 * effective_min_width and num_items > 1:
            cols = 2
        elif num_items == 1:
            cols = 1 
        else:
            cols = 1 

        cols = min(cols, num_items)

        rows = (num_items + cols - 1) // cols
        
        frame_width = available_width // cols
        frame_height = max(min_height, available_height // rows if rows > 0 else available_height)
        
        return cols, rows, frame_width, frame_height

    def toggle_descriptions(self):
        """Toggle description frames in the right panel."""
        any_open = bool(self.description_frames)
        if any_open:
            for frame in self.description_frames.values():
                frame.destroy()
            self.description_frames.clear()
            self.toggle_desc_button["text"] = ""
        else:
            selected = [label for label, var in self.all_check_vars.items() if var.get()]
            if not selected:
                messagebox.showinfo("No Selection", "Please select some entities first.")
                return
            
            self.root.update_idletasks()
            
            self.desc_scrollable_frame.update_idletasks()
            available_width = self.desc_scrollable_frame.winfo_width()
            available_height = self.desc_scrollable_frame.winfo_height()

            if available_width < 100:
                available_width = self.right_panel.winfo_width() - 20 
                if available_width < 100: available_width = 800 
            if available_height < 100:
                 available_height = 600 

            cols, rows, frame_width, frame_height = self.calculate_tile_layout(
                available_width, available_height, len(selected), min_height=200
            )
            
            for c in range(cols):
                self.desc_scrollable_frame.grid_columnconfigure(c, weight=1)
            for r in range(rows):
                self.desc_scrollable_frame.grid_rowconfigure(r, weight=1)

            for idx, label in enumerate(selected):
                try:
                    if label not in self.entity_data:
                        desc, typ, srcid = fetch_entity_details(label)
                        self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
                    
                    row = idx // cols
                    col = idx % cols
                    
                    desc_frame = ttk.LabelFrame(self.desc_scrollable_frame, text=label, padding=5)
                    desc_frame.config(width=frame_width - 4, height=frame_height - 4)
                    desc_frame.grid_propagate(False)
                    
                    desc_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                    
                    text_frame = ttk.Frame(desc_frame)
                    text_frame.pack(fill="both", expand=True)
                    
                    text_widget = tk.Text(text_frame, wrap="word", font=("TkDefaultFont", 9))
                    text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                    text_widget.configure(yscrollcommand=text_scrollbar.set)
                    
                    desc = self.entity_data[label]["desc"]
                    srcid = self.entity_data[label]["srcid"]
                    text_widget.insert("1.0", f"Description:\n{desc}\n\nSource ID:\n{srcid}")
                    text_widget.config(state="disabled")
                    
                    text_widget.pack(side="left", fill="both", expand=True)
                    text_scrollbar.pack(side="right", fill="y")
                    
                    self.description_frames[label] = desc_frame
                    
                except Exception as e:
                    print(f"Error showing description for {label}: {e}")
            
            self.desc_scrollable_frame.update_idletasks()
            self.desc_canvas.configure(scrollregion=self.desc_canvas.bbox("all"))
            
            if self.description_frames:
                self.toggle_desc_button["text"] = "✓"

    def submit_merge(self):
        """Handle the merge operation."""
        if not self.entity_type.get() or not self.target_entry.get():
            messagebox.showerror("Missing info", "Please select a target entity and entity type.")
            return
        
        selected = [label for label, var in self.all_check_vars.items() if var.get()]

        if not selected:
            messagebox.showerror("No entities", "Select at least one source entity.")
            return
        
        for frame in self.description_frames.values():
            frame.destroy()
        self.description_frames.clear()
        self.toggle_desc_button["text"] = ""

        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }
        
        if (strategy["description"] == "keep_first" or strategy["source_id"] == "keep_first"):
            first_entity = self.first_entity_var.get()
            if not first_entity:
                messagebox.showerror("Missing Selection", "Please select which entity should be 'first' using the radio buttons when using 'keep_first' strategy.")
                return
            if first_entity not in selected:
                messagebox.showerror("Invalid Selection", "The selected 'first' entity must be in the list of selected entities.")
                return
            selected = [first_entity] + [e for e in selected if e != first_entity]

        asyncio.run(self.run_merge(selected, self.target_entry.get(), strategy, self.entity_type.get()))

    async def run_merge(self, sources, target, strategy, etype):
        """Execute the merge operation asynchronously."""
        rag = await initialize_rag()
        try:
            await rag.amerge_entities(
                source_entities=sources,
                target_entity=target,
                merge_strategy=strategy,
                target_entity_data={"entity_type": etype}
            )
            messagebox.showinfo("Success", f"Entities merged into '{target}'")
            
            print("Refreshing LightRAG server (via /documents/scan)...")
            if not trigger_server_scan():
                print("Server scan failed or server not running. Manual restart might still be needed if changes don't appear.")
            else:
                print("Server refresh attempted.")

            # Refresh the entity list from the server to see the latest changes
            newly_fetched_entities = fetch_entities()
            
            # Preserve existing checkbox states for entities that still exist
            new_all_check_vars = {}
            for entity in newly_fetched_entities:
                new_all_check_vars[entity] = self.all_check_vars.get(entity, tk.BooleanVar())
            self.all_check_vars = new_all_check_vars
            self.entity_list = newly_fetched_entities # Update the master list
            
            self.filter_var.set("") # Clear filter to show all entities for the refresh
            self.filtered_entity_list = self.entity_list.copy()
            self.create_entity_list() # Rebuild the visible list and update UI controls
            
            # Reset the form controls after merge
            self.target_entry.set("")
            self.entity_type.set("")
            self.first_entity_var.set("")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages() # Close RAG instance to release file handles

    def on_closing(self):
        """Handle window closing event."""
        self.save_window_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeGUI(root)
    root.mainloop()