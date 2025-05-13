import os
import logging
import ollama
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag.base import BaseKVStorage
from nano_graphrag._utils import compute_args_hash

logging.basicConfig(level=logging.WARNING)
logging.getLogger("nano-graphrag").setLevel(logging.INFO)

# !!! qwen2-7B maybe produce unparsable results and cause the extraction of graph to fail.
MODEL = "qwen2.5:7b"


async def ollama_model_if_cache(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    # remove kwargs that are not supported by ollama
    kwargs.pop("max_tokens", None)
    kwargs.pop("response_format", None)

    ollama_client = ollama.AsyncClient()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Get the cached response if having-------------------
    hashing_kv: BaseKVStorage = kwargs.pop("hashing_kv", None)
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    if hashing_kv is not None:
        args_hash = compute_args_hash(MODEL, messages)
        if_cache_return = await hashing_kv.get_by_id(args_hash)
        if if_cache_return is not None:
            return if_cache_return["return"]
    # -----------------------------------------------------
    response = await ollama_client.chat(model=MODEL, messages=messages, **kwargs)

    result = response["message"]["content"]
    # Cache the response if having-------------------
    if hashing_kv is not None:
        await hashing_kv.upsert({args_hash: {"return": result, "model": MODEL}})
    # -----------------------------------------------------
    return result


def remove_if_exist(file):
    if os.path.exists(file):
        os.remove(file)


WORKING_DIR = "./nano_graphrag_cache_ollama_TEST"


def query(query_text = "请总结一下交通事故发生的原因"):
    rag = GraphRAG(
        working_dir=WORKING_DIR,
        best_model_func=ollama_model_if_cache,
        cheap_model_func=ollama_model_if_cache,
    )
    print(
        rag.query(
            "请总结一下交通事故发生的原因", param=QueryParam(mode="global")
        )
    )

def query_accidents(data_path = "./data/output"):
    os.makedirs(data_path, exist_ok=True)
    
    output_file = os.path.join(data_path, "accidents.txt")
    
    if not os.path.exists(output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            pass
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        current_parent = None
        for root, dirs, files in os.walk(data_path):
            if root == data_path:
                continue
                
            # If we're in a new parent directory, add a newline
            if current_parent != root:
                if current_parent is not None:  # Don't add newline before first file
                    outfile.write("\n\n")
                current_parent = root
                
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Successfully combined all txt files into {output_file}")

def insert():
    from time import time

    # First ensure the accidents.txt file exists and is populated
    query_accidents()

    accidents_path = "./data/output/accidents.txt"
    with open(accidents_path, encoding="utf-8-sig") as f:
        FAKE_TEXT = f.read()

    remove_if_exist(f"{WORKING_DIR}/vdb_entities.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_full_docs.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_text_chunks.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_community_reports.json")
    remove_if_exist(f"{WORKING_DIR}/graph_chunk_entity_relation.graphml")

    rag = GraphRAG(
        working_dir=WORKING_DIR,
        enable_llm_cache=True,
        best_model_func=ollama_model_if_cache,
        cheap_model_func=ollama_model_if_cache,
    )
    start = time()
    rag.insert(FAKE_TEXT)
    print("indexing time:", time() - start)


if __name__ == "__main__":
    insert()
    query("请总结一下交通事故发生的原因")
