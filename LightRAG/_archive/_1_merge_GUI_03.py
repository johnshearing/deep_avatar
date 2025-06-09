import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
        self.entity_descriptions = {}
        self.entity_types_map = {}
        self.check_vars = {}

        # Entity Frame
        frame = tk.Frame(root)
        frame.grid(row=0, column=0, rowspan=10, padx=10, pady=10, sticky="ns")

        self.canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        for ent in self.entity_list:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.scrollable_frame, text=ent, variable=var, command=self.update_targets_and_types)
            chk.pack(anchor="w")
            self.check_vars[ent] = var

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Target Entity Dropdown
        ttk.Label(root, text="Target Entity:").grid(row=0, column=1)
        self.target_entry = ttk.Combobox(root, values=[], width=40)
        self.target_entry.grid(row=0, column=2)

        # Merge Strategies
        ttk.Label(root, text="Merge Strategy - Description:").grid(row=1, column=1)
        self.strategy_desc = ttk.Combobox(root, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_desc.set("join_unique")
        self.strategy_desc.grid(row=1, column=2)

        ttk.Label(root, text="Merge Strategy - Source ID:").grid(row=2, column=1)
        self.strategy_srcid = ttk.Combobox(root, values=["concatenate", "keep_first", "join_unique"])
        self.strategy_srcid.set("join_unique")
        self.strategy_srcid.grid(row=2, column=2)

        # Entity Type Dropdown
        ttk.Label(root, text="Entity Type:").grid(row=3, column=1)
        self.entity_type = ttk.Combobox(root, values=[], width=37)
        self.entity_type.grid(row=3, column=2)

        # Buttons
        self.merge_button = ttk.Button(root, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=4, column=2, sticky="e")

        # Show Descriptions
        self.desc_button = ttk.Button(root, text="Show Descriptions", command=self.show_descriptions)
        self.desc_button.grid(row=4, column=1, sticky="w")

    def update_targets_and_types(self):
        sel = [label for label, var in self.check_vars.items() if var.get()]
        self.target_entry["values"] = sel
        if sel:
            self.target_entry.set(sel[0])
        types = set()
        for label in sel:
            if label not in self.entity_descriptions:
                desc, typ = fetch_entity_details(label)
                self.entity_descriptions[label] = desc
                self.entity_types_map[label] = typ
            types.add(self.entity_types_map[label])
        self.entity_type["values"] = list(types)
        if types:
            self.entity_type.set(next(iter(types)))

    def show_descriptions(self):
        sel = [label for label, var in self.check_vars.items() if var.get()]
        for label in sel:
            if label not in self.entity_descriptions:
                desc, typ = fetch_entity_details(label)
                self.entity_descriptions[label] = desc
                self.entity_types_map[label] = typ
            top = tk.Toplevel(self.root)
            top.title(label)
            text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, width=60, height=15)
            text_area.pack(padx=10, pady=10, fill="both", expand=True)
            text_area.insert(tk.END, self.entity_descriptions[label])
            text_area.config(state="disabled")
            top.attributes("-topmost", True)

    def submit_merge(self):
        sel = [label for label, var in self.check_vars.items() if var.get()]
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
