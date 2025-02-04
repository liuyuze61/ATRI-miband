import os
import json

def convert_script(input_text):
    lines = input_text.strip().split('\n')
    output = []
    current_character = ""  # 默认角色名为 ""
    
    for line in lines:
        if '\t' not in line:
            # 如果没有角色名，使用默认角色名 ""
            output.append({
                "character": current_character,
                "text": line.strip()
            })
        else:
            # 如果有角色名，更新当前角色名
            character, text = line.split('\t')
            current_character = character.strip() if character.strip() else ""
            output.append({
                "character": current_character,
                "text": text.strip()
            })
    
    return output

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()
    
    # 转换剧本
    converted_script = convert_script(input_text)
    
    # 将结果嵌套在指定的结构中
    final_output = [{
        "background": "none.png",
        "dialogues": converted_script
    }]
    
    # 将结果保存为JSON格式
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

def process_folder(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 遍历输入文件夹中的所有txt文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename.replace('.txt', '.json'))
            
            print(f"处理文件: {input_file} -> {output_file}")
            process_file(input_file, output_file)

if __name__ == "__main__":
    import argparse

    # 设置命令行参数
    parser = argparse.ArgumentParser(description="转换剧本格式")
    parser.add_argument("input_folder", help="输入文件夹路径，包含待处理的txt文件")
    parser.add_argument("output_folder", help="输出文件夹路径，用于保存转换后的JSON文件")
    args = parser.parse_args()

    # 处理文件夹
    process_folder(args.input_folder, args.output_folder)
    print("处理完成！")