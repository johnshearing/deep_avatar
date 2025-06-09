import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import asyncio
import requests
import os
import json

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
        self.description_windows = {}
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
            "state": "normal",
            "paned_position": 600
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.window_config.update(saved_config)
            except:
                pass  # Use defaults if config file is corrupted

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
        
        # Set window state (normal, zoomed, etc.)
        if self.window_config["state"] == "zoomed":
            self.root.state('zoomed')
        
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
        
        # Right panel for controls
        self.right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_panel, weight=0)
        
        # Set initial paned window position
        self.root.after(100, lambda: self.paned_window.sashpos(0, self.window_config["paned_position"]))
        
        # Create left panel content
        self.create_left_panel()
        
        # Create right panel content
        self.create_right_panel()

    def create_left_panel(self):
        """Create the left panel with entity list"""
        # Configure grid weights for proper resizing
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(self.left_panel)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Label(header_frame, text="Show Desc", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, padx=5)
        ttk.Label(header_frame, text="First", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, padx=5)
        ttk.Label(header_frame, text="Select Entities", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.left_panel)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)
        
        # Show Descriptions button (column 0)
        self.toggle_desc_button = ttk.Button(content_frame, text="Show\nDescriptions", command=self.toggle_descriptions)
        self.toggle_desc_button.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        
        # Radio buttons frame (column 1)
        self.radio_frame = ttk.Frame(content_frame)
        self.radio_frame.grid(row=0, column=1, sticky="ns", padx=(0, 5))
        
        # Scrollable entity list frame (column 2)
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=2, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas and scrollbar for entity list
        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Create entity list
        self.create_entity_list()

    def create_right_panel(self):
        """Create the right panel with controls"""
        # Configure grid weights
        self.right_panel.grid_columnconfigure(1, weight=1)
        
        # Add some padding to the right panel
        control_frame = ttk.Frame(self.right_panel)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
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

    def create_entity_list(self):
        """Create the entity list with proper layout for checkboxes and radio buttons"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.radio_frame.winfo_children():
            widget.destroy()
        
        self.check_vars.clear()
        
        # Create entity rows
        for i, ent in enumerate(self.entity_list):
            # Checkbox in the scrollable frame
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_selection)
            cb.pack(anchor="w", padx=5, pady=1)
            self.check_vars[ent] = var
            
            # Corresponding radio button in the radio frame
            rb = ttk.Radiobutton(self.radio_frame, text="", variable=self.first_entity_var, value=ent)
            rb.pack(pady=3)  # Adjust padding to align with checkboxes

    def update_selection(self):
        selected = [label for label, var in self.check_vars.items() if var.get()]
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

    def toggle_descriptions(self):
        any_open = bool(self.description_windows)
        if any_open:
            for win in list(self.description_windows.values()):
                try:
                    win.destroy()
                except:
                    pass
            self.description_windows.clear()
            self.toggle_desc_button["text"] = "Show\nDescriptions"
        else:
            selected = [label for label, var in self.check_vars.items() if var.get()]
            if not selected:
                messagebox.showinfo("No Selection", "Please select some entities first.")
                return
                
            for idx, label in enumerate(selected):
                if label in self.description_windows:
                    try:
                        self.description_windows[label].lift()
                    except:
                        pass
                    continue
                    
                try:
                    if label not in self.entity_data:
                        desc, typ, srcid = fetch_entity_details(label)
                        self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
                    
                    win = tk.Toplevel(self.root)
                    win.title(label)
                    win.geometry(f"400x300+{100 + idx * 410}+100")
                    
                    # Create text widget with description
                    text = tk.Text(win, wrap="word")
                    desc = self.entity_data[label]["desc"]
                    srcid = self.entity_data[label]["srcid"]
                    text.insert("1.0", f"Description:\n{desc}\n\nSource ID:\n{srcid}")
                    text.config(state="disabled")
                    text.pack(expand=True, fill="both")
                    
                    self.description_windows[label] = win
                    
                    # Handle window closing
                    def on_desc_close(window=win, entity=label):
                        if entity in self.description_windows:
                            del self.description_windows[entity]
                        window.destroy()
                        if not self.description_windows:
                            self.toggle_desc_button["text"] = "Show\nDescriptions"
                    
                    win.protocol("WM_DELETE_WINDOW", on_desc_close)
                    
                except Exception as e:
                    print(f"Error showing description for {label}: {e}")
                    
            if self.description_windows:
                self.toggle_desc_button["text"] = "Close\nDescriptions"

    def submit_merge(self):
        if not self.entity_type.get() or not self.target_entry.get():
            messagebox.showerror("Missing info", "Please select a target entity and entity type.")
            return
        selected = [label for label, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("No entities", "Select at least one source entity.")
            return
        
        # Close description windows
        for win in list(self.description_windows.values()):
            try:
                win.destroy()
            except:
                pass
        self.description_windows.clear()
        self.toggle_desc_button["text"] = "Show\nDescriptions"

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