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

description_windows = {}
selected_description = None
selected_source_id = None

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

class MergeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LightRAG Entity Merger")
        self.entity_list = fetch_entities()
        self.entity_vars = {}
        self.entity_descriptions = {}
        self.entity_types = set()
        self.entity_source_ids = {}
        self.target_var = tk.StringVar()
        self.entity_type_var = tk.StringVar()

        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0, rowspan=10, sticky="nswe", padx=10, pady=10)
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.left_frame)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        for ent in self.entity_list:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.scroll_frame, text=ent, variable=var, command=self.update_selection)
            cb.pack(anchor="w")
            self.entity_vars[ent] = var

        # Right panel
        ttk.Label(root, text="Target Entity:").grid(row=0, column=1)
        self.target_entry = ttk.Combobox(root, textvariable=self.target_var, values=[], width=40)
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
        self.entity_type = ttk.Combobox(root, textvariable=self.entity_type_var, values=[], width=37)
        self.entity_type.grid(row=3, column=2)

        self.show_desc_button = ttk.Button(root, text="Show Descriptions", command=self.show_descriptions)
        self.show_desc_button.grid(row=4, column=2, sticky="e")

        self.close_desc_button = ttk.Button(root, text="Close All", command=self.close_all_descriptions)
        self.close_desc_button.grid(row=5, column=2, sticky="e")

        self.merge_button = ttk.Button(root, text="Merge Entities", command=self.submit_merge)
        self.merge_button.grid(row=6, column=2, sticky="e")

    def update_selection(self):
        selected = [k for k, v in self.entity_vars.items() if v.get()]
        self.target_entry["values"] = selected
        types = set()
        for label in selected:
            if label not in self.entity_descriptions:
                desc, typ, sid = fetch_entity_details(label)
                self.entity_descriptions[label] = desc
                self.entity_source_ids[label] = sid
            types.add(fetch_entity_details(label)[1])
        self.entity_type["values"] = list(types)

    def show_descriptions(self):
        for label in [k for k, v in self.entity_vars.items() if v.get()]:
            if label in description_windows:
                description_windows[label].lift()
                continue

            window = tk.Toplevel(self.root)
            window.title(label)
            window.geometry("400x300")

            desc, typ, sid = fetch_entity_details(label)

            text = scrolledtext.ScrolledText(window, wrap=tk.WORD)
            text.insert(tk.END, f"Description:\n{desc}\n\nSource ID:\n{sid}")
            text.pack(expand=True, fill="both")

            btn_frame = ttk.Frame(window)
            btn_frame.pack(fill="x")

            def select_description():
                nonlocal label
                global selected_description
                selected_description = label
                self.strategy_desc.set("keep_first")

            def select_source_id():
                nonlocal label
                global selected_source_id
                selected_source_id = label
                self.strategy_srcid.set("keep_first")

            ttk.Button(btn_frame, text="Keep This Description Only", command=select_description).pack(side="left")
            ttk.Button(btn_frame, text="Keep This Source ID Only", command=select_source_id).pack(side="right")

            description_windows[label] = window
            window.protocol("WM_DELETE_WINDOW", lambda l=label: self.close_description(l))

    def close_description(self, label):
        if label in description_windows:
            description_windows[label].destroy()
            del description_windows[label]

    def close_all_descriptions(self):
        for label in list(description_windows.keys()):
            self.close_description(label)

    def submit_merge(self):
        sel = [k for k, v in self.entity_vars.items() if v.get()]
        target = self.target_var.get().strip()
        etype = self.entity_type_var.get().strip()

        if not target or not sel or not etype:
            messagebox.showerror("Missing info", "Please fill all fields.")
            return

        if self.strategy_desc.get() == "keep_first" and selected_description not in sel:
            messagebox.showerror("Invalid Selection", "Selected description not in source entities.")
            return

        if self.strategy_srcid.get() == "keep_first" and selected_source_id not in sel:
            messagebox.showerror("Invalid Selection", "Selected source ID not in source entities.")
            return

        strategy = {
            "description": self.strategy_desc.get(),
            "source_id": self.strategy_srcid.get()
        }

        asyncio.run(self.run_merge(sel, target, strategy, etype))

    async def run_merge(self, sources, target, strategy, etype):
        self.close_all_descriptions()
        rag = await initialize_rag()
        try:
            await rag.amerge_entities(
                source_entities=sources,
                target_entity=target,
                merge_strategy=strategy,
                target_entity_data={"entity_type": etype}
            )
            messagebox.showinfo("Success", f"Entities merged into '{target}'")
            self.entity_list = fetch_entities()
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            self.entity_vars.clear()
            for ent in self.entity_list:
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(self.scroll_frame, text=ent, variable=var, command=self.update_selection)
                cb.pack(anchor="w")
                self.entity_vars[ent] = var
            self.target_var.set("")
            self.entity_type_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            await rag.finalize_storages()

if __name__ == "__main__":
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    app = MergeGUI(root)
    root.mainloop()
