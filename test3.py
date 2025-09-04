import json
import sys
import os

import os

# 读取环境变量
variable_name = "GOOD_PASS"
value = os.environ.get(variable_name)

if value is not None:
    print(f"The value of {variable_name} is {value}")
else:
    print(f"{variable_name} is not set")
    value = "good"

def build_compile_cmd(params):
    cmd = [
        f"mkdir -p /root/good/{params['name']} &&",
        "/root/openvino/bin/intel64/Release/compile_tool",
        f"-m {params['model']}",
        f"-o /root/good/{params['name']}/{params['output_blob']}",
        # f"-ip {params['input_precision']}",
        # f"-op {params['output_precision']}",
        f"-d NPU",
        f"-c /root/configs/{params['config']}",
        "-log_level LOG_TRACE",
        f"> /root/good/{params['name']}/{params['log_file']}"
    ]
    
    # Conditionally add parameters if they are not empty
    if params['input_precision']:
        cmd.insert(3, f"-ip {params['input_precision']}")
    if params['output_precision']:
        cmd.insert(4, f"-op {params['output_precision']}")    
    if params['input_output_precision']:
        cmd.insert(5, f"-iop {params['input_output_precision']}")
    if params['input_layout']:
        cmd.insert(6, f"-il {params['input_layout']}")
    if params['output_layout']:
        cmd.insert(7, f"-ol {params['output_layout']}")
    if params['input_output_layout']:
        cmd.insert(8, f"-iol {params['input_output_layout']}")
    if params['model_input_layout']:
        cmd.insert(9, f"-iml {params['model_input_layout']}")
    if params['model_output_layout']:
        cmd.insert(10, f"-oml {params['model_output_layout']}")
    if params['model_input_output_layout']:
        cmd.insert(11, f"-ioml {params['model_input_output_layout']}")
    
    return " \\\n  ".join(cmd)

def parse_json(json_path):
    with open(json_path, 'r') as f:
        config = json.load(f)

    cmds = []
    
    for network in config["networks"]:
        compile_cfg = network.get("Compile", {})
        # 替换路径中的 `..` 为 `/root/public_models`
        model_path = network.get("ir", "").replace("..", "/root/npu_public_models")
        params = {
            "model": model_path,
            "output_blob": f"{network.get('name', 'output')}.blob",
            "input_precision": compile_cfg.get("input_precision", ""),
            "output_precision": compile_cfg.get("output_precision", ""),
            "input_output_precision": compile_cfg.get("input_output_precision", ""),
            "input_layout": compile_cfg.get("input_layout", ""),
            "output_layout": compile_cfg.get("output_layout", ""),
            "input_output_layout": compile_cfg.get("input_output_layout", ""),
            "model_input_layout": compile_cfg.get("model_input_layout", ""),
            "model_output_layout": compile_cfg.get("model_output_layout", ""),
            "model_input_output_layout": compile_cfg.get("model_input_output_layout", ""),
            "config": f"{network.get('name', 'output')}.config",
            "log_file": f"{network.get('name', 'output')}.log",
            "name": network.get('name', 'output')
        }
        cmds.append(build_compile_cmd(params))
    return cmds

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("用法: python test3.py public_models_5020.json")
    #     exit(1)
    cmds = parse_json("public_models_5010.json")
    for cmd in cmds:
        print(cmd)
        print()  # 命令之间空一行
        
    # 创建 output_file 的目录（如果不存在）
    output_file = "output_file.txt"
    
    with open(output_file, 'w') as f:
        for cmd in cmds:
            f.write(cmd + "\n\n")
    
    print(f"命令已写入 {output_file}")
