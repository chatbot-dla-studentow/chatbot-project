import requests
import time
import json
import os
import platform
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

API_AGENT_URL = "http://localhost:8001/api/chat"
MODELS_TO_TEST = ["mistral:7b", "llama3:latest", "gemma2:latest", "phi3:latest"]
CACHE_FILE = "benchmarks/rag_context_cache.json"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
REPORTS_DIR = "benchmarks/reports"
REPORT_FILE = f"{REPORTS_DIR}/BENCHMARK_REPORT_{TIMESTAMP}.md"
PLOT_FILE = f"{REPORTS_DIR}/BENCHMARK_PLOT_{TIMESTAMP}.png"

TEST_CASES = [
    {"name": "Stypendium Rektora", "query": "Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?"},
    {"name": "Obrona pracy", "query": "Jak wygląda procedura obrony pracy dyplomowej krok po kroku?"},
    {"name": "Zmiana danych", "query": "W jaki sposób mogę zaktualizować swój numer telefonu i adres zamieszkania w systemie?"},
    {"name": "Urlop dziekański", "query": "Kiedy i na jakich zasadach student może ubiegać się o urlop dziekański?"}
]

def get_hw_info():
    """Zbiera informacje o sprzęcie."""
    info = {}
    try:
        info['os'] = f"{platform.system()} {platform.release()}"
        info['cpu'] = "Intel Core i9-12900KF (8 P-cores + 8 E-cores, 24 threads)"
        
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if "MemTotal" in line:
                        mem_kb = int(line.split()[1])
                        info['ram'] = f"{round(mem_kb / 1024 / 1024, 2)} GB"
                        break
        except:
            info['ram'] = "N/A"
            
        try:
            gpu_info = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                encoding='utf-8'
            ).strip()
            info['gpu'] = gpu_info
        except:
            info['gpu'] = "Nie wykryto NVIDIA GPU"
    except Exception as e:
        info['error'] = str(e)
    return info

def warm_up_model(model):
    """Ładuje model do GPU przed testem."""
    print(f" Rozgrzewanie modelu {model}...", end="", flush=True)
    try:
        requests.post(API_AGENT_URL, json={
            "model": model, 
            "messages": [{"role": "user", "content": "hi"}], 
            "stream": False
        }, timeout=60)
        print(" Gotowy!")
    except:
        print(" Błąd ładowania.")

def get_context_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def run_benchmark():
    if not os.path.exists(REPORTS_DIR): os.makedirs(REPORTS_DIR)
    context_cache = get_context_cache()
    hw_info = get_hw_info()
    
    all_results = []
    
    print(f" Start Benchmark -> {TIMESTAMP}")
    print(f" CPU: {hw_info['cpu']}")
    
    for model in MODELS_TO_TEST:
        warm_up_model(model)
        model_data = {"model": model, "times": []}
        
        for case in TEST_CASES:
            print(f"  [{model}] Testuję: {case['name']}...", end="", flush=True)
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": case["query"]}],
                "stream": False
            }
            
            start_time = time.time()
            try:
                r = requests.post(API_AGENT_URL, json=payload, timeout=180)
                duration = time.time() - start_time
                
                if r.status_code == 200:
                    ans = r.json().get("message", {}).get("content", "")
                    model_data["times"].append({
                        "case": case["name"],
                        "duration": round(duration, 2),
                        "answer": ans
                    })
                    print(f" OK ({round(duration, 2)}s)")
                else:
                    print(f" ERROR {r.status_code}")
            except Exception as e:
                print(f" FAIL {e}")
        
        all_results.append(model_data)
    
    generate_report(all_results, hw_info)
    generate_plot(all_results)

def generate_report(results, hw):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Raport Wydajności LLM\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("### Specyfikacja sprzętowa\n")
        f.write(f"- **System:** {hw.get('os')}\n")
        f.write(f"- **CPU:** {hw.get('cpu')}\n")
        f.write(f"- **RAM:** {hw.get('ram')}\n")
        f.write(f"- **GPU:** {hw.get('gpu')}\n\n")
        
        f.write("## Czasy odpowiedzi (Latency)\n\n| Model | " + " | ".join([c["name"] for c in TEST_CASES]) + " | Średnia |\n")
        f.write("| :--- | " + " | ".join([":---:"] * (len(TEST_CASES) + 1)) + " |\n")
        
        for res in results:
            times = [t["duration"] for t in res["times"]]
            avg = round(sum(times)/len(times), 2) if times else 0
            f.write(f"| **{res['model']}** | " + " | ".join([f"{t}s" for t in times]) + f" | **{avg}s** |\n")
        
        f.write(f"\n![Wykres porównawczy](BENCHMARK_PLOT_{TIMESTAMP}.png)\n\n")
        f.write("---\n\n## Pełne odpowiedzi modeli\n")
        
        for case_idx, case in enumerate(TEST_CASES):
            f.write(f"###  Pytanie: {case['name']}\n")
            f.write(f"> {case['query']}\n\n")
            for res in results:
                test = res["times"][case_idx] if case_idx < len(res["times"]) else None
                if test:
                    f.write(f"####  {res['model']} ({test['duration']}s)\n```text\n{test['answer']}\n```\n\n")
            f.write("---\n")

def generate_plot(results):
    try:
        labels = [c["name"] for c in TEST_CASES]
        x = np.arange(len(labels))
        width = 0.2
        fig, ax = plt.subplots(figsize=(12, 6))
        for i, res in enumerate(results):
            times = [t["duration"] for t in res["times"]]
            ax.bar(x + (i - len(results)/2 + 0.5) * width, times, width, label=res["model"])
        ax.set_ylabel('Czas odpowiedzi (s)')
        ax.set_title('Porównanie opóźnień (Latency) modeli LLM')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(PLOT_FILE)
        print(f" Wykres zapisany: {PLOT_FILE}")
    except Exception as e:
        print(f" Nie udało się wygenerować wykresu: {e}")

if __name__ == "__main__":
    run_benchmark()
