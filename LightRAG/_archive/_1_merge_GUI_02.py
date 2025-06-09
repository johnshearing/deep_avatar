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
            return node["properties"].get("description", "No description found."), node["properties"].get("entity_type", "")
    return "No description found.", ""

class MergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LightRAG Entity Merger")
        self.entity_list = fetch_entities()
        self.selected_entities = set()
        self.entity_descriptions = {}
        self.entity_types = set()

        # Left panel with scrollbar
        self.list_frame = ttk.Frame(root)
        self.list_frame.grid(row=0, column=0, rowspan=8, padx=10, pady=10, sticky="nswe")
        self.listbox_scroll = ttk.Scrollbar(self.list_frame, orient="vertical")
        self.listbox = tk.Listbox(self.list_frame, selectmode=tk.MULTIPLE, width=50, yscrollcommand=self.listbox_scroll.set)
        self.listbox_scroll.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox_scroll.pack(side="right", fill="y")
        for ent in self.entity_list:
            self.listbox.insert(tk.END, ent)
        self.listbox.bind("<Double-Button-1>", self.show_description)

        # Make listbox resizable
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Right panel
        ttk.Label(root, text="Target Entity:").grid(row=0, column=1)
        self.target_entry = ttk.Combobox(root, values=[], width=40)
        self.target_entry.grid(row=0, column=2)

        ttk.Label(root, text="Merge Strategy - Description:").grid(row=1, column=1)
        self.strategy_desc = ttk.Combobox(root, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_desc.set("join_unique")
        self.strategy_desc.grid(row=1, column=2)

        ttk.Label(root, text="Merge Strategy - Source ID:").grid(row=2, column=1)
        self.strategy_srcid = ttk.Combobox(root, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_srcid.set("join_unique")
        self.strategy_srcid.grid(row=2, column=2)

        ttk.Label(root, text="Entity Type:").grid(row=3, column=1)
        self.entity_type = ttk.Combobox(root, values=[], width=37)
        self.entity_type.grid(row=3, column=2)

        self.update_type_button = ttk.Button(root, text="Update Types", command=self.update_entity_types)
        self.update_type_button.grid(row=4, column=2, sticky="e")

        self.update_targets_button = ttk.Button(root, text="Update Targets", command=self.update_target_options)
        self.update_targets_button.grid(row=5, column=2, sticky="e")

        self.merge_button = ttk.Button(root, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=6, column=2, sticky="e")

    def show_description(self, event):
        sel = self.listbox.curselection()
        if sel:
            label = self.listbox.get(sel[0])
            desc, typ = fetch_entity_details(label)
            self.entity_descriptions[label] = desc
            self.entity_types.add(typ)
            messagebox.showinfo(label, desc)

    def update_entity_types(self):
        sel = [self.listbox.get(i) for i in self.listbox.curselection()]
        types = set()
        for label in sel:
            _, typ = fetch_entity_details(label)
            types.add(typ)
        self.entity_type["values"] = list(types)
        if types:
            self.entity_type.set(next(iter(types)))

    def update_target_options(self):
        sel = [self.listbox.get(i) for i in self.listbox.curselection()]
        self.target_entry["values"] = sel
        if sel:
            self.target_entry.set(sel[0])

    def submit_merge(self):
        sel = [self.listbox.get(i) for i in self.listbox.curselection()]
        target = self.target_entry.get().strip()
        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }
        etype = self.entity_type.get().strip()
        if not target or not sel or not etype:
            messagebox.showerror("Missing info", "Please fill all fields.")
            return
        asyncio.run(self.run_merge(sel, target, strategy, etype))

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
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages()

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeGUI(root)
    root.mainloop()
