import os
import shutil

import torch
from ultralytics import YOLO


def update_model_with_additional_dataset(DATASETS_DIR, MODELS_DIR, group):
    # Epoch数の指定
    EPOCHS = 100
    # パスの設定
    source_dir = os.path.join(DATASETS_DIR, "predefined_dataset", group)
    tmp_dir = os.path.join(DATASETS_DIR, "tmp")
    destination_dir = os.path.join(DATASETS_DIR, "tmp", "copy_dataset", group)
    additional_dataset_dir = os.path.join(DATASETS_DIR, "additional_dataset", group)
    txt_destination_train = os.path.join(destination_dir, "train", "labels")
    jpg_destination_train = os.path.join(destination_dir, "train", "images")
    txt_destination_test = os.path.join(destination_dir, "test", "labels")
    jpg_destination_test = os.path.join(destination_dir, "test", "images")
    txt_destination_val = os.path.join(destination_dir, "valid", "labels")
    jpg_destination_val = os.path.join(destination_dir, "valid", "images")

    data_yaml_path = os.path.join(destination_dir, "data.yaml")
    models_dir = os.path.join(MODELS_DIR, "YOLOv11", group)
    runs_dir = os.path.join(tmp_dir, "train", "runs", "detect")

    # modelを書き込む先のディレクトリの作成
    os.makedirs(models_dir, exist_ok=True)

    # GPUが有効かチェック
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    print(f"{device} が有効です。")

    # データセットのコピー
    # 注: additional_dataset_dir = datasets/additional_dataset/{group}がないとうまくいかない(<- ここをos.makedirsで作る)
    os.makedirs(additional_dataset_dir, exist_ok=True)
    os.makedirs(destination_dir, exist_ok=True)
    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

    # 追加データのコピー - valに1枚、testに1枚、残りはtrainにコピー
    additional_files = os.listdir(additional_dataset_dir)
    txt_files = [f for f in additional_files if f.endswith(".txt")]
    jpg_files = [f for f in additional_files if f.endswith(".jpeg")]

    # 1枚目をvalに、2枚目をtestに、残りをtrainにコピー
    for i, (txt_file, jpg_file) in enumerate(zip(txt_files, jpg_files, strict=True)):
        txt_path = os.path.join(additional_dataset_dir, txt_file)
        jpg_path = os.path.join(additional_dataset_dir, jpg_file)

        if i == 0:
            shutil.copy(txt_path, txt_destination_val)
            shutil.copy(jpg_path, jpg_destination_val)
            print(f"{txt_file} と {jpg_file} を val ディレクトリにコピーしました。")
        elif i == 1:
            shutil.copy(txt_path, txt_destination_test)
            shutil.copy(jpg_path, jpg_destination_test)
            print(f"{txt_file} と {jpg_file} を test ディレクトリにコピーしました。")
        else:
            shutil.copy(txt_path, txt_destination_train)
            shutil.copy(jpg_path, jpg_destination_train)
            print(f"{txt_file} と {jpg_file} を train ディレクトリにコピーしました。")

    # モデルのトレーニング
    model = YOLO(f"{MODELS_DIR}/YOLOv11/yolo11n.pt").to(device)
    model.train(data=data_yaml_path, epochs=EPOCHS, imgsz=640, device=device, project=runs_dir)

    # best.ptのコピー
    latest_train_dir = max(
        [d for d in os.listdir(runs_dir) if d.startswith("train")],
        key=lambda x: os.path.getctime(os.path.join(runs_dir, x)),
    )
    best_pt_path = os.path.join(runs_dir, latest_train_dir, "weights", "best.pt")
    new_pt_path = os.path.join(models_dir, "hackv11i.pt")

    if os.path.exists(best_pt_path):
        shutil.copy(best_pt_path, new_pt_path)
        print(f"best.pt を {best_pt_path} からhackv11i.ptに名前を変え {new_pt_path} にコピーしました。")
        # shutil.copy(best_pt_path, models_dir)
        # print(f"best.pt を {best_pt_path} から {models_dir} にコピーしました。")
    else:
        print("best.pt ファイルが見つかりませんでした。")

    # 処理が完了したらtmpディレクトリを削除
    shutil.rmtree(tmp_dir)
    print(f"{tmp_dir} を削除しました。")
