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

description_windows = {}

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
    response = requests.get("http://localhost:9621/graph/label/list")
    response.raise_for_status()
    return sorted(response.json(), key=lambda x: x.lower())

def fetch_entity_details(label):
    response = requests.get(f"http://localhost:9621/graphs?label={label}&max_depth=1&max_nodes=1000")
    response.raise_for_status()
    data = response.json()
    for node in data.get("nodes", []):
        if node.get("id") == label:
            return node["properties"].get("description", "No description found."), node["properties"].get("entity_type", ""), node["properties"].get("source_id", "")
    return "No description found.", "", ""

class MergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LightRAG Entity Merger")
        self.entity_list = fetch_entities()
        self.filtered_entity_list = self.entity_list.copy()  # Keep track of filtered list
        self.description_windows = {}
        self.description_frames = {}  # Store description frames in right panel
        self.selected_entities = {}
        self.entity_data = {}
        self.config_file = "merge_gui_config.json"
        
        # Load window configuration
        self.load_window_config()
        
        # Set up the main window
        self.setup_main_window()
        
        # Variables for entity selection
        self.check_vars = {}
        self.first_entity_var = tk.StringVar()  # Radio button variable for first entity selection
        
        # Create the UI
        self.create_ui()
        
        # Bind window close event to save configuration
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_window_config(self):
        """Load window size and position from config file"""
        self.window_config = {
            "geometry": "1200x800",
            "state": "normal",  # Start normal, then maximize if needed
            "paned_position": 300  # 25% of 1200px width
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.window_config.update(saved_config)
            except:
                pass  # Use defaults if config file is corrupted

    def set_initial_paned_position(self):
        """Set the initial position of the paned window splitter at 25% from left"""
        try:
            # Get the current window width
            self.root.update_idletasks()
            window_width = self.paned_window.winfo_width()
            
            # Set position to 25% of window width
            if window_width > 100:  # Make sure window is properly sized
                position = int(window_width * 0.25)  # 25% from left
            else:
                position = 300  # Fallback value
            
            self.paned_window.sashpos(0, position)
        except Exception as e:
            # Fallback to a fixed position if anything goes wrong
            self.paned_window.sashpos(0, 300)

    def save_window_config(self):
        """Save current window size and position to config file"""
        try:
            # Get current window geometry
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
            pass  # Don't crash if we can't save config

    def setup_main_window(self):
        """Set up the main window with saved configuration"""
        # Set window geometry
        self.root.geometry(self.window_config["geometry"])
        
        # Maximize the window based on OS
        if platform.system() == "Windows":
            try:
                self.root.state('zoomed')
            except tk.TclError:
                # Fallback if 'zoomed' fails, although it's usually supported on Windows
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        elif platform.system() == "Linux": # This will cover Ubuntu/WSL
            # For Linux, maximize by setting geometry to screen size
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            # Some window managers might also respect -zoomed or -fullscreen, but direct geometry is more reliable
            # self.root.attributes('-zoomed', True) # Might work on some WMs
            # self.root.attributes('-fullscreen', True) # If you want true fullscreen without borders
        else: # macOS or other Unix-like
            # For macOS, 'zoomed' often isn't supported. Fullscreen might be an option,
            # or manual sizing. A simple resize to screen dimensions is a good start.
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            # self.root.attributes('-fullscreen', True) # For macOS, this often works for true fullscreen
            
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_ui(self):
        """Create the main user interface"""
        # Create main paned window for resizable sections
        self.paned_window = ttk.PanedWindow(self.root, orient="horizontal")
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        
        # Left panel for entity list
        self.left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_panel, weight=1)
        
        # Right panel for controls and descriptions
        self.right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_panel, weight=3)
        
        # Set initial paned window position at 25% from left
        self.root.after(10, self.set_initial_paned_position)
        
        # Create right panel content first (contains target_entry and other controls)
        self.create_right_panel()
        
        # Create left panel content
        self.create_left_panel()

    def create_left_panel(self):
        """Create the left panel with filter and entity list"""
        # Configure grid weights for proper resizing
        self.left_panel.grid_rowconfigure(2, weight=1)  # Changed from row 1 to row 2
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Filter frame
        filter_frame = ttk.Frame(self.left_panel)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, padx=(0, 5))
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        self.filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.filter_var.trace('w', self.on_filter_change)
        
        # Clear filter button
        self.clear_filter_button = ttk.Button(filter_frame, text="✕", width=3, command=self.clear_filter)
        self.clear_filter_button.grid(row=0, column=2)
        
        # Header frame
        header_frame = ttk.Frame(self.left_panel)
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Label(header_frame, text="Desc", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="First", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="Select Entities", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.left_panel)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Show Descriptions button (column 0) - remove text label
        self.toggle_desc_button = ttk.Button(content_frame, text="", command=self.toggle_descriptions, width=3)
        self.toggle_desc_button.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        
        # Scrollable content frame that contains both radio buttons and checkboxes (column 1)
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas and scrollbar for the combined list
        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure the scrollable frame to have two columns: radio buttons and checkboxes
        self.scrollable_frame.grid_columnconfigure(0, weight=0)  # Radio button column
        self.scrollable_frame.grid_columnconfigure(1, weight=1)  # Checkbox column


        # Enhanced scroll handling function
        def _on_mousewheel(event):
            try:
                # Handle different platforms and event types
                if platform.system() == "Windows":
                    if hasattr(event, 'delta') and event.delta:
                        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif platform.system() == "Darwin":  # macOS
                    if hasattr(event, 'delta') and event.delta:
                        self.canvas.yview_scroll(int(-1 * event.delta), "units")
                else:  # Linux (including WSL)
                    if event.num == 4: # Scroll up
                        self.canvas.yview_scroll(-1, "units")
                    elif event.num == 5: # Scroll down
                        self.canvas.yview_scroll(1, "units")
                    elif hasattr(event, 'delta') and event.delta: # Fallback for some Linux mouse events
                        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass  # Ignore any scroll errors
            return "break"

        # Determine which events to bind based on platform
        scroll_events = []
        if platform.system() == "Windows":
            scroll_events = ["<MouseWheel>", "<Shift-MouseWheel>"]
        elif platform.system() == "Darwin":  # macOS
            scroll_events = ["<MouseWheel>", "<Button-4>", "<Button-5>"] # Button-4/5 for older mice
        else:  # Linux (including WSL)
            scroll_events = ["<Button-4>", "<Button-5>", "<MouseWheel>"] # Button-4/5 common for scroll up/down

        # Bind scroll events to canvas
        for event in scroll_events:
            try:
                self.canvas.bind(event, _on_mousewheel)
            except:
                pass

        # Add focus management for better event handling
        def on_canvas_enter(event):
            self.canvas.focus_set()

        def on_canvas_leave(event):
            self.root.focus_set()

        self.canvas.bind("<Enter>", on_canvas_enter)
        self.canvas.bind("<Leave>", on_canvas_leave)

        # Make canvas focusable (this works with tk.Canvas)
        self.canvas.config(takefocus=True)

        # Add keyboard scrolling as backup
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

        
        # Create entity list
        self.create_entity_list()

    def on_filter_change(self, *args):
        """Handle filter text changes"""
        filter_text = self.filter_var.get().lower()
        
        if not filter_text:
            # If filter is empty, show all entities
            self.filtered_entity_list = self.entity_list.copy()
        else:
            # Filter entities that contain the filter text
            self.filtered_entity_list = [
                entity for entity in self.entity_list 
                if filter_text in entity.lower()
            ]
        
        # Recreate the entity list with filtered results
        self.create_entity_list()

    def clear_filter(self):
        """Clear the filter and show all entities"""
        self.filter_var.set("")

    def create_right_panel(self):
        """Create the right panel with controls and description area"""
        # Configure grid weights
        self.right_panel.grid_rowconfigure(1, weight=1)  # Description area expands
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Control frame at the top
        control_frame = ttk.Frame(self.right_panel)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Target Entity and Strategy
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

        # Info label about "First Entity" selection
        info_label = ttk.Label(control_frame, text="Note: 'First Entity' is used when 'keep_first' strategy is selected", 
                                 font=("TkDefaultFont", 8), foreground="gray", wraplength=300)
        info_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        # Merge button
        self.merge_button = ttk.Button(control_frame, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=5, column=1, sticky="e", padx=5, pady=10)

        # Description area frame
        self.description_area = ttk.Frame(self.right_panel)
        self.description_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.description_area.grid_columnconfigure(0, weight=1)
        self.description_area.grid_rowconfigure(0, weight=1)

        # Scrollable frame for descriptions
        self.desc_canvas = tk.Canvas(self.description_area)
        self.desc_scrollbar = ttk.Scrollbar(self.description_area, orient="vertical", command=self.desc_canvas.yview)
        self.desc_scrollable_frame = ttk.Frame(self.desc_canvas)
        
        self.desc_scrollable_frame.bind("<Configure>", lambda e: self.desc_canvas.configure(scrollregion=self.desc_canvas.bbox("all")))
        self.desc_canvas.create_window((0, 0), window=self.desc_scrollable_frame, anchor="nw")
        self.desc_canvas.configure(yscrollcommand=self.desc_scrollbar.set)
        
        self.desc_canvas.grid(row=0, column=0, sticky="nsew")
        self.desc_scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind mouse wheel to description canvas
        def _on_desc_mousewheel(event):
            try:
                if platform.system() == "Windows":
                    if hasattr(event, 'delta') and event.delta:
                        self.desc_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif platform.system() == "Darwin":  # macOS
                    if hasattr(event, 'delta') and event.delta:
                        self.desc_canvas.yview_scroll(int(-1 * event.delta), "units")
                else:  # Linux (including WSL)
                    if event.num == 4: # Scroll up
                        self.desc_canvas.yview_scroll(-1, "units")
                    elif event.num == 5: # Scroll down
                        self.desc_canvas.yview_scroll(1, "units")
            except:
                pass
            return "break"

        # Bind scroll events to description canvas
        desc_scroll_events = []
        if platform.system() == "Windows":
            desc_scroll_events = ["<MouseWheel>", "<Shift-MouseWheel>"]
        elif platform.system() == "Darwin":  # macOS
            desc_scroll_events = ["<MouseWheel>", "<Button-4>", "<Button-5>"]
        else:  # Linux (including WSL)
            desc_scroll_events = ["<Button-4>", "<Button-5>", "<MouseWheel>"]

        for event in desc_scroll_events:
            try:
                self.desc_canvas.bind(event, _on_desc_mousewheel)
            except:
                pass

    def create_entity_list(self):
        """Create the entity list with radio buttons and checkboxes in the same scrollable area"""
        # Store current selections before clearing
        current_selections = {label: var.get() for label, var in self.check_vars.items()}
        current_first_entity = self.first_entity_var.get()
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.check_vars.clear()
        
        # Create entity rows with radio buttons and checkboxes side by side using filtered list
        for i, ent in enumerate(self.filtered_entity_list):
            # Radio button in column 0 of the scrollable frame
            rb = ttk.Radiobutton(self.scrollable_frame, text="", variable=self.first_entity_var, value=ent)
            rb.grid(row=i, column=0, padx=(5, 2), pady=1, sticky="w")
            
            # Checkbox in column 1 of the scrollable frame
            var = tk.BooleanVar()
            # Restore previous selection if it exists
            if ent in current_selections:
                var.set(current_selections[ent])
            cb = ttk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_selection)
            cb.grid(row=i, column=1, padx=(2, 5), pady=1, sticky="w")
            self.check_vars[ent] = var
        
        # Restore first entity selection if it's still in the filtered list
        if current_first_entity in self.filtered_entity_list:
            self.first_entity_var.set(current_first_entity)
        else:
            self.first_entity_var.set("")
        
        # Update the selection to refresh target entity and type dropdowns
        self.update_selection()

    def update_selection(self):
        selected = [label for label, var in self.check_vars.items() if var.get()]
        
        # Safety check to ensure UI elements exist
        if not hasattr(self, 'target_entry'):
            return
            
        self.target_entry["values"] = selected
        
        # Fetch entity details for selected entities and collect their types
        types = set()
        for label in selected:
            if label not in self.entity_data:
                try:
                    desc, typ, srcid = fetch_entity_details(label)
                    self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
                    types.add(typ)
                except Exception as e:
                    print(f"Error fetching details for {label}: {e}")
        
        self.entity_type["values"] = list(types)
        
        if self.target_entry.get() not in selected:
            self.target_entry.set("")
        if self.entity_type.get() not in self.entity_type["values"]:
            self.entity_type.set("")
        
        # Clear first entity selection if the selected entity is no longer in the list
        if self.first_entity_var.get() not in selected:
            self.first_entity_var.set("")

    def calculate_tile_layout(self, available_width, available_height, num_items, min_width=300, min_height=200):
        """Calculate optimal tiling layout for description frames"""
        if num_items == 0:
            return 0, 0, 0, 0
        
        # Calculate number of columns that can fit
        cols = max(1, available_width // min_width)
        
        # Calculate number of rows needed
        rows = (num_items + cols - 1) // cols  # Ceiling division
        
        # Calculate actual frame dimensions
        frame_width = available_width // cols
        frame_height = max(min_height, available_height // rows if rows > 0 else available_height)
        
        return cols, rows, frame_width, frame_height

    def toggle_descriptions(self):
        """Toggle description frames in the right panel"""
        any_open = bool(self.description_frames)
        if any_open:
            # Clear all description frames
            for frame in self.description_frames.values():
                frame.destroy()
            self.description_frames.clear()
            self.toggle_desc_button["text"] = ""
        else:
            selected = [label for label, var in self.check_vars.items() if var.get()]
            if not selected:
                messagebox.showinfo("No Selection", "Please select some entities first.")
                return
            
            # Update the canvas to get current size
            self.root.update_idletasks()
            
            # Get available space in the description area
            available_width = self.desc_scrollable_frame.winfo_width()
            if available_width <= 1:  # If not yet rendered, use a reasonable default
                available_width = 800
            
            available_height = 600  # Reasonable default height
            
            # Calculate layout
            cols, rows, frame_width, frame_height = self.calculate_tile_layout(
                available_width, available_height, len(selected), min_width=300, min_height=200
            )
            
            # Create description frames in a tiled layout
            for idx, label in enumerate(selected):
                try:
                    if label not in self.entity_data:
                        desc, typ, srcid = fetch_entity_details(label)
                        self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
                    
                    # Calculate position in grid
                    row = idx // cols
                    col = idx % cols
                    
                    # Create frame for this description
                    desc_frame = ttk.LabelFrame(self.desc_scrollable_frame, text=label, padding=5)
                    desc_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                    
                    # Configure the frame to have a specific size
                    desc_frame.config(width=frame_width-4, height=frame_height-4)
                    desc_frame.grid_propagate(False)  # Prevent frame from shrinking
                    
                    # Create text widget with scrollbar for this description
                    text_frame = ttk.Frame(desc_frame)
                    text_frame.pack(fill="both", expand=True)
                    
                    text_widget = tk.Text(text_frame, wrap="word", font=("TkDefaultFont", 9))
                    text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                    text_widget.configure(yscrollcommand=text_scrollbar.set)
                    
                    # Insert content
                    desc = self.entity_data[label]["desc"]
                    srcid = self.entity_data[label]["srcid"]
                    text_widget.insert("1.0", f"Description:\n{desc}\n\nSource ID:\n{srcid}")
                    text_widget.config(state="disabled")
                    
                    text_widget.pack(side="left", fill="both", expand=True)
                    text_scrollbar.pack(side="right", fill="y")
                    
                    self.description_frames[label] = desc_frame
                    
                except Exception as e:
                    print(f"Error showing description for {label}: {e}")
            
            # Configure grid weights for the scrollable frame
            for c in range(cols):
                self.desc_scrollable_frame.grid_columnconfigure(c, weight=1)
            
            # Update the canvas scroll region
            self.desc_scrollable_frame.update_idletasks()
            self.desc_canvas.configure(scrollregion=self.desc_canvas.bbox("all"))
            
            if self.description_frames:
                self.toggle_desc_button["text"] = "✓"

    def submit_merge(self):
        if not self.entity_type.get() or not self.target_entry.get():
            messagebox.showerror("Missing info", "Please select a target entity and entity type.")
            return
        selected = [label for label, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("No entities", "Select at least one source entity.")
            return
        
        # Close description frames
        for frame in self.description_frames.values():
            frame.destroy()
        self.description_frames.clear()
        self.toggle_desc_button["text"] = ""

        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }
        
        # For keep_first strategy, we need to reorder the source list to put the selected "first" entity first
        if (strategy["description"] == "keep_first" or strategy["source_id"] == "keep_first"):
            first_entity = self.first_entity_var.get()
            if not first_entity:
                messagebox.showerror("Missing Selection", "Please select which entity should be 'first' using the radio buttons when using 'keep_first' strategy.")
                return
            if first_entity not in selected:
                messagebox.showerror("Invalid Selection", "The selected 'first' entity must be in the list of selected entities.")
                return
            # Reorder selected list to put the "first" entity at the beginning
            selected = [first_entity] + [e for e in selected if e != first_entity]

        asyncio.run(self.run_merge(selected, self.target_entry.get(), strategy, self.entity_type.get()))

    async def run_merge(self, sources, target, strategy, etype):
        rag = await initialize_rag()
        try:
            await rag.amerge_entities(
                source_entities=sources,
                target_entity=target,
                merge_strategy=strategy,
                target_entity_data={"entity_type": etype}
            )
            messagebox.showinfo("Success", f"Entities merged into '{target}'")
            
            # Reset the form
            for var in self.check_vars.values():
                var.set(False)
            self.target_entry.set("")
            self.entity_type.set("")
            self.first_entity_var.set("")
            
            # Refresh the entity list
            self.entity_list = fetch_entities()
            self.filtered_entity_list = self.entity_list.copy()
            self.create_entity_list()
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages()

    def on_closing(self):
        """Handle window closing event"""
        self.save_window_config()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeGUI(root)
    root.mainloop()