import json
import os

# Input JSON file path
JSON_FILE = "public_models_5010.json"
# Output directory for config files
OUTPUT_DIR = "configs"

EXTRA_LINES = [
    "PERF_COUNT YES",
    "NPU_COMPILATION_MODE_PARAMS write-strategy-to-json=true dpu-profiling=true dma-profiling=true sw-profiling=true enable-schedule-trace=true dump-task-stats=true"
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    networks = data.get("networks", [])
    for net in networks:
        name = net.get("name")
        extra_config = net.get("extra_config", {})
        config_lines = []

        # 无论原来是什么，都强制设置 NPU_COMPILER_TYPE 为 MLIR
        modified_config = extra_config.copy()
        modified_config["NPU_COMPILER_TYPE"] = "MLIR"

        # 写入 extra_config 的 key-value
        for k, v in modified_config.items():
            config_lines.append(f"{k} {v}")

        config_lines.extend(EXTRA_LINES)

        config_filename = os.path.join(OUTPUT_DIR, f"{name}.config")
        with open(config_filename, "w", encoding="utf-8") as cf:
            cf.write("\n".join(config_lines) + "\n")

        print(f"Generated: {config_filename}")

if __name__ == "__main__":
    main()