import json
import os
import argparse
from tqdm import tqdm
import csv
import re


def parse(input_file, trans_language, audio_format):
    results = []
    last_image_files = set()  # 用于存储上一个翻译文本中的图片信息
    with open(input_file, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    scn_length = len(data['scenes'])
    pattern = re.compile(r'[「」『』（）"]|(\[.*])|(\\n)')
    for i in range(scn_length):
        texts = data['scenes'][i].get('texts')
        if texts:
            for text in texts:
                character = ""
                image_files = set()  # 当前翻译文本中的图片信息

                try:
                    character = text[0] or ""
                except TypeError:
                    pass

                try:
                    sentence_ori = text[2][0][1] or ""
                    sentence_ori = pattern.sub('', sentence_ori)
                    sentence_trans = text[2][trans_language][1] or ""
                    sentence_trans = pattern.sub('', sentence_trans)
                except TypeError:
                    continue

                try:
                    voice = text[3][0].get("voice") or ""
                    if voice:
                        voice += f".{audio_format}"
                except TypeError:
                    voice = ""

                # Extract imageFile.file information
                env_data = text[-1].get('data', [])
                for item in env_data:
                    if isinstance(item, list) and len(item) == 3:
                        obj_type, obj_class, obj_info = item
                        if obj_class in ["stage", "event", "item"]:
                            image_file = obj_info.get('redraw', {}).get('imageFile', {}).get('file')
                            if image_file and (image_file.startswith('bg') or image_file.startswith('ev') or image_file.startswith('item')):
                                # Remove 'l' suffix if present
                                if image_file.endswith('ll'):
                                    image_file = image_file[:-2]  # Remove the last 'll'
                                if image_file.endswith('l'):
                                    image_file = image_file[:-1]  # Remove the last 'l'
                                image_files.add(image_file)

                # Compare with the last image files
                if image_files != last_image_files:
                    # Append image files to the translation
                    if image_files:
                        image_files_str = ", ".join(sorted(image_files))  # 排序并转换为字符串
                        sentence_trans += f" [Images: {image_files_str}]"
                    last_image_files = image_files  # 更新上一个翻译文本中的图片信息
                # results.append([character, sentence_ori, sentence_trans, voice])
                results.append([character, sentence_trans])  # 只保留角色和中文翻译
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default=os.getcwd(), help='Path to the input directory.')
    parser.add_argument('-o', '--output', type=str, default=os.path.join(os.getcwd(), "parsed"), help='Path to the output directory.')
    parser.add_argument('-l', '--language', type=int, default=2, help='Language of translation, 0: JP; 1:EN; 2:ZHS; 3:ZHT, default is 2.')
    parser.add_argument('-d', '--delimiter', type=str, default="\t",
                        help='Delimiter of input data file, default is \\t')
    parser.add_argument('-af', '--audio_format', type=str, default="mp3",
                        help='Audio file name suffix, default is mp3')
    parser.add_argument('-s', '--single_file', action='store_true', default=False,
                        help='Merge all text into a single file.')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.single_file:
        results = []
        for f in tqdm(os.listdir(args.input)):
            file = os.path.join(args.input, f)
            if os.path.isfile(f) and (f.split('.')[-1].upper() == "JSON"):
                results += parse(f, args.language, args.audio_format)
        with open(os.path.join(args.output, "all_in_one_parsed.txt"), "w", encoding="utf8", newline="") as tsvfile:
            writer = csv.writer(tsvfile, delimiter=args.delimiter)
            writer.writerows(results)

    else:
        for f in tqdm(os.listdir(args.input)):
            file = os.path.join(args.input, f)
            if os.path.isfile(f) and (f.split('.')[-1].upper() == "JSON"):
                results = parse(f, args.language, args.audio_format)
                with open(os.path.join(args.output, f + "_parsed.txt"), "w", encoding="utf8", newline="") as tsvfile:
                    writer = csv.writer(tsvfile, delimiter=args.delimiter)
                    writer.writerows(results)
