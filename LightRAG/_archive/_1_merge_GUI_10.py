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
    try:
        response = requests.get("http://localhost:9621/graph/label/list")
        response.raise_for_status()
        entities = sorted(response.json(), key=lambda x: x.lower())
        print(f"Fetched {len(entities)} entities: {entities[:5]}...")  # Debugging
        return entities
    except requests.RequestException as e:
        print(f"Error fetching entities: {e}")
        return []

def fetch_entity_details(label):
    try:
        response = requests.get(f"http://localhost:9621/graphs?label={label}&max_depth=1&max_nodes=1000")
        response.raise_for_status()
        data = response.json()
        for node in data.get("nodes", []):
            if node.get("id") == label:
                return (
                    node["properties"].get("description", "No description found."),
                    node["properties"].get("entity_type", ""),
                    node["properties"].get("source_id", "")
                )
        return "No description found.", "", ""
    except requests.RequestException as e:
        print(f"Error fetching details for {label}: {e}")
        return "No description found.", "", ""

class MergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LightRAG Entity Merger")
        self.entity_list = fetch_entities()
        self.description_windows = {}
        self.selected_entities = {}
        self.entity_data = {}

        # Main Frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Scrollable Listbox with Checkbuttons and Radio buttons
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, rowspan=8, sticky="ns")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Bind canvas resizing to ensure proper width
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Variables for entity selection
        self.check_vars = {}
        self.first_entity_var = tk.StringVar(value="")  # Radio button variable

        # Check if entity list is empty
        if not self.entity_list:
            messagebox.showerror(
                "No Entities",
                "No entities found. Ensure the LightRAG server is running at http://localhost:9621."
            )
            return

        # Add header for the entity list
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(
            header_frame, text="Select Entities", font=("TkDefaultFont", 9, "bold"), width=40
        ).pack(side="left", padx=5)
        ttk.Label(
            header_frame, text="First Entity", font=("TkDefaultFont", 9, "bold"), width=10
        ).pack(side="right", padx=5)

        for ent in self.entity_list:
            # Create a frame for each entity row
            ent_frame = ttk.Frame(self.scrollable_frame)
            ent_frame.pack(fill="x", padx=5, pady=2)

            # Checkbox for selection
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(ent_frame, text=ent, variable=var, command=self.update_selection)
            cb.pack(side="left", padx=(0, 10))
            self.check_vars[ent] = var

            # Radio button for "first entity" selection
            rb = ttk.Radiobutton(
                ent_frame, text="First", variable=self.first_entity_var, value=ent
            )
            rb.pack(side="right", padx=(10, 0))
            print(f"Created radio button for entity: {ent}")  # Debugging

        # Target Entity and Strategy
        ttk.Label(self.main_frame, text="Target Entity:").grid(row=0, column=2, sticky="e", padx=5)
        self.target_entry = ttk.Combobox(self.main_frame, values=[], width=40)
        self.target_entry.grid(row=0, column=3, sticky="w", padx=5)

        ttk.Label(self.main_frame, text="Merge Strategy - Description:").grid(
            row=1, column=2, sticky="e", padx=5
        )
        self.strategy_desc = ttk.Combobox(
            self.main_frame, values=["concatenate", "keep_first", "join_unique"]
        )
        self.strategy_desc.set("join_unique")
        self.strategy_desc.grid(row=1, column=3, sticky="w", padx=5)

        ttk.Label(self.main_frame, text="Merge Strategy - Source ID:").grid(
            row=2, column=2, sticky="e", padx=5
        )
        self.strategy_srcid = ttk.Combobox(
            self.main_frame, values=["concatenate", "keep_first", "join_unique"]
        )
        self.strategy_srcid.set("join_unique")
        self.strategy_srcid.grid(row=2, column=3, sticky="w", padx=5)

        ttk.Label(self.main_frame, text="Entity Type:").grid(row=3, column=2, sticky="e", padx=5)
        self.entity_type = ttk.Combobox(self.main_frame, values=[], width=37)
        self.entity_type.grid(row=3, column=3, sticky="w", padx=5)

        # Info label about "First Entity" selection
        info_label = ttk.Label(
            self.main_frame,
            text="Note: 'First Entity' is used when 'keep_first' strategy is selected",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        info_label.grid(row=4, column=2, columnspan=2, sticky="w", padx=5)

        # Buttons
        self.toggle_desc_button = ttk.Button(
            self.main_frame, text="Show Descriptions", command=self.toggle_descriptions
        )
        self.toggle_desc_button.grid(row=5, column=3, sticky="e", padx=5)

        self.merge_button = ttk.Button(
            self.main_frame, text="Merge Entities", command=self.submit_merge
        )
        self.merge_button.grid(row=6, column=3, sticky="e", padx=5)

    def on_canvas_configure(self, event):
        """Adjust canvas window width to match canvas width."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_selection(self):
        selected = [label for label, var in self.check_vars.items() if var.get()]
        self.target_entry["values"] = selected

        # Fetch entity details for selected entities and collect their types
        types = set()
        for label in selected:
            if label not in self.entity_data:
                desc, typ, srcid = fetch_entity_details(label)
                self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
            types.add(self.entity_data[label]["type"])

        self.entity_type["values"] = list(types)

        if self.target_entry.get() not in selected:
            self.target_entry.set("")
        if self.entity_type.get() not in self.entity_type["values"]:
            self.entity_type.set("")

        # Clear first entity selection if not in selected list
        if self.first_entity_var.get() not in selected:
            self.first_entity_var.set("")

    def toggle_descriptions(self):
        any_open = bool(self.description_windows)
        if any_open:
            for win in self.description_windows.values():
                win.destroy()
            self.description_windows.clear()
            self.toggle_desc_button["text"] = "Show Descriptions"
        else:
            selected = [label for label, var in self.check_vars.items() if var.get()]
            for idx, label in enumerate(selected):
                if label in self.description_windows:
                    self.description_windows[label].lift()
                    continue
                desc, typ, srcid = fetch_entity_details(label)
                self.entity_data[label] = {"desc": desc, "type": typ, "srcid": srcid}
                win = tk.Toplevel(self.root)
                win.title(label)
                win.geometry(f"400x300+{100 + idx * 410}+100")

                text = tk.Text(win, wrap="word", height=10)
                text.insert(
                    "1.0",
                    f"Description:\n{desc}\n\nSource ID:\n{srcid}"
                )
                text.config(state="disabled")
                text.pack(expand=True, fill="both")

                self.description_windows[label] = win
            self.toggle_desc_button["text"] = "Close Descriptions"

    def submit_merge(self):
        if not self.entity_type.get() or not self.target_entry.get():
            messagebox.showerror("Missing info", "Please select a target entity and entity type.")
            return
        selected = [label for label, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("No entities", "Select at least one source entity.")
            return

        # Close description windows
        for win in self.description_windows.values():
            win.destroy()
        self.description_windows.clear()
        self.toggle_desc_button["text"] = "Show Descriptions"

        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }

        # For keep_first strategy, reorder source list to put first entity first
        if strategy["description"] == "keep_first" or strategy["source_id"] == "keep_first":
            first_entity = self.first_entity_var.get()
            if not first_entity:
                messagebox.showerror(
                    "Missing Selection",
                    "Please select which entity should be 'first' using the radio buttons when using 'keep_first' strategy."
                )
                return
            if first_entity not in selected:
                messagebox.showerror(
                    "Invalid Selection",
                    "The selected 'first' entity must be in the list of selected entities."
                )
                return
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
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.check_vars.clear()

            # Recreate header
            header_frame = ttk.Frame(self.scrollable_frame)
            header_frame.pack(fill="x", padx=5, pady=5)
            ttk.Label(
                header_frame, text="Select Entities", font=("TkDefaultFont", 9, "bold"), width=40
            ).pack(side="left", padx=5)
            ttk.Label(
                header_frame, text="First Entity", font=("TkDefaultFont", 9, "bold"), width=10
            ).pack(side="right", padx=5)

            # Recreate entity list
            for ent in self.entity_list:
                ent_frame = ttk.Frame(self.scrollable_frame)
                ent_frame.pack(fill="x", padx=5, pady=2)

                var = tk.BooleanVar()
                cb = ttk.Checkbutton(ent_frame, text=ent, variable=var, command=self.update_selection)
                cb.pack(side="left", padx=(0, 10))
                self.check_vars[ent] = var

                rb = ttk.Radiobutton(
                    ent_frame, text="First", variable=self.first_entity_var, value=ent
                )
                rb.pack(side="right", padx=(10, 0))
                print(f"Recreated radio button for entity: {ent}")  # Debugging

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set a reasonable window size
    app = MergeGUI(root)
    root.mainloop()