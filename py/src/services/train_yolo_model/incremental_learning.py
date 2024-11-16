import os
import shutil

import torch
from ultralytics import YOLO


def update_model_with_additional_dataset(DATASETS_DIR, MODELS_DIR, group):
    # パスの設定
    source_dir = os.path.join(DATASETS_DIR, "predefined_dataset", group)
    tmp_dir = os.path.join(DATASETS_DIR, "tmp")
    destination_dir = os.path.join(DATASETS_DIR, "tmp", "copy_dataset", group)
    additional_dataset_dir = os.path.join(DATASETS_DIR, "additional_dataset", group)
    txt_destination = os.path.join(destination_dir, "train", "labels")
    jpg_destination = os.path.join(destination_dir, "train", "images")
    data_yaml_path = os.path.join(destination_dir, "data.yaml")
    models_dir = os.path.join(MODELS_DIR, "YOLOv11", group)
    runs_dir = os.path.join(tmp_dir, "train", "runs", "detect")

    # GPUが有効かチェック
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    print(f"{device} が有効です。")

    # データセットのコピー
    os.makedirs(destination_dir, exist_ok=True)
    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

    # 追加データのコピー
    for filename in os.listdir(additional_dataset_dir):
        file_path = os.path.join(additional_dataset_dir, filename)
        if filename.endswith(".txt"):
            shutil.copy(file_path, txt_destination)
            print(f"{filename} を {txt_destination} にコピーしました。")
        elif filename.endswith(".jpeg"):
            shutil.copy(file_path, jpg_destination)
            print(f"{filename} を {jpg_destination} にコピーしました。")

    # モデルのトレーニング
    model = YOLO(f"{MODELS_DIR}/YOLOv11/yolo11n.pt").to(device)
    model.train(data=data_yaml_path, epochs=2, imgsz=640, device=device, project=runs_dir)

    # best.ptのコピー
    latest_train_dir = max(
        [d for d in os.listdir(runs_dir) if d.startswith("train")],
        key=lambda x: os.path.getctime(os.path.join(runs_dir, x)),
    )
    best_pt_path = os.path.join(runs_dir, latest_train_dir, "weights", "best.pt")
    output_path = os.path.join(models_dir, "hackv11i.pt")

    if os.path.exists(best_pt_path):
        shutil.copy(best_pt_path, output_path)
        print(f"best.pt を {best_pt_path} から {output_path} にコピーしました。")
    else:
        print("best.pt ファイルが見つかりませんでした。")

    # 処理が完了したらtmpディレクトリを削除
    shutil.rmtree(tmp_dir)
    print(f"{tmp_dir} を削除しました。")
