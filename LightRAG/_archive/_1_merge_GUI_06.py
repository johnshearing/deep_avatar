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
keep_first_selections = {"description": None, "source_id": None}

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

        # Main Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Scrollable Listbox with Checkbuttons
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, rowspan=8, sticky="ns")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.check_vars = {}

        for ent in self.entity_list:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_selection)
            cb.pack(anchor="w")
            self.check_vars[ent] = var

        # Target Entity and Strategy
        ttk.Label(self.main_frame, text="Target Entity:").grid(row=0, column=2)
        self.target_entry = ttk.Combobox(self.main_frame, values=[], width=40)
        self.target_entry.grid(row=0, column=3)

        ttk.Label(self.main_frame, text="Merge Strategy - Description:").grid(row=1, column=2)
        self.strategy_desc = ttk.Combobox(self.main_frame, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_desc.set("join_unique")
        self.strategy_desc.grid(row=1, column=3)

        ttk.Label(self.main_frame, text="Merge Strategy - Source ID:").grid(row=2, column=2)
        self.strategy_srcid = ttk.Combobox(self.main_frame, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_srcid.set("join_unique")
        self.strategy_srcid.grid(row=2, column=3)

        ttk.Label(self.main_frame, text="Entity Type:").grid(row=3, column=2)
        self.entity_type = ttk.Combobox(self.main_frame, values=[], width=37)
        self.entity_type.grid(row=3, column=3)

        # Buttons
        self.toggle_desc_button = ttk.Button(self.main_frame, text="Show Descriptions", command=self.toggle_descriptions)
        self.toggle_desc_button.grid(row=4, column=3, sticky="e")

        self.merge_button = ttk.Button(self.main_frame, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=5, column=3, sticky="e")

    def update_selection(self):
        selected = [label for label, var in self.check_vars.items() if var.get()]
        self.target_entry["values"] = selected
        self.entity_type["values"] = list({self.entity_data[label]["type"] for label in selected if label in self.entity_data})
        if not self.target_entry.get() in selected:
            self.target_entry.set("")
        if not self.entity_type.get() in self.entity_type["values"]:
            self.entity_type.set("")

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
                text = tk.Text(win, wrap="word")
                text.insert("1.0", f"Description:\n{desc}\n\nSource ID:\n{srcid}")
                text.config(state="disabled")
                text.pack(expand=True, fill="both")
                btn_frame = ttk.Frame(win)
                btn_frame.pack(fill="x")
                ttk.Button(btn_frame, text="Keep This Description Only", command=lambda l=label: self.set_keep_only("description", l)).pack(side="left")
                ttk.Button(btn_frame, text="Keep This Source ID Only", command=lambda l=label: self.set_keep_only("source_id", l)).pack(side="right")
                self.description_windows[label] = win
            self.toggle_desc_button["text"] = "Close Descriptions"

    def set_keep_only(self, field, label):
        keep_first_selections[field] = label
        if field == "description":
            self.strategy_desc.set("keep_first")
        elif field == "source_id":
            self.strategy_srcid.set("keep_first")

    def submit_merge(self):
        if not self.entity_type.get() or not self.target_entry.get():
            messagebox.showerror("Missing info", "Please select a target entity and entity type.")
            return
        selected = [label for label, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("No entities", "Select at least one source entity.")
            return
        for win in self.description_windows.values():
            win.destroy()
        self.description_windows.clear()
        self.toggle_desc_button["text"] = "Show Descriptions"

        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }
        if strategy["description"] == "keep_first":
            strategy["description"] = keep_first_selections.get("description", selected[0])
        if strategy["source_id"] == "keep_first":
            strategy["source_id"] = keep_first_selections.get("source_id", selected[0])

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
            for var in self.check_vars.values():
                var.set(False)
            self.target_entry.set("")
            self.entity_type.set("")
            self.entity_list = fetch_entities()
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.check_vars.clear()
            for ent in self.entity_list:
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_selection)
                cb.pack(anchor="w")
                self.check_vars[ent] = var
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages()

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeGUI(root)
    root.mainloop()
