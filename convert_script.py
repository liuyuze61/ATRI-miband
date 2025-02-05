import os
import json
import re

def convert_script(input_text):
    lines = input_text.strip().split('\n')
    output = []
    current_character = ""  # 默认角色名为 ""
    current_background = "none.png"  # 默认背景图片

    for line in lines:
        # 检测背景图片信息
        image_match = re.search(r'\[Images: ([^\]]+)\]', line)
        if image_match:
            # 提取背景图片的第一项
            images = image_match.group(1).split(',')
            current_background = images[0].strip() + ".png"
            line = re.sub(r'\[Images: [^\]]+\]', '', line).strip()  # 去掉背景图片信息

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

    return output, current_background

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        input_text = f.read()

    # 转换剧本
    lines = input_text.strip().split('\n')
    scenes = []
    current_scene = []
    current_background = "none.png"

    for line in lines:
        # 检测背景图片信息
        image_match = re.search(r'\[Images: ([^\]]+)\]', line)
        if image_match:
            # 如果检测到新的背景图片，保存当前场景并开始新场景
            if current_scene:
                scenes.append({
                    "background": current_background,
                    "dialogues": current_scene
                })
                current_scene = []

            # 提取背景图片的第一项
            images = image_match.group(1).split(',')
            current_background = images[0].strip() + ".png"
            line = re.sub(r'\[Images: [^\]]+\]', '', line).strip()  # 去掉背景图片信息

        if '\t' not in line:
            # 如果没有角色名，使用默认角色名 ""
            current_scene.append({
                "character": "",
                "text": line.strip()
            })
        else:
            # 如果有角色名，更新当前角色名
            character, text = line.split('\t')
            current_scene.append({
                "character": character.strip() if character.strip() else "",
                "text": text.strip()
            })

    # 保存最后一个场景
    if current_scene:
        scenes.append({
            "background": current_background,
            "dialogues": current_scene
        })

    # 将结果保存为JSON格式
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

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