import os
import shutil

import torch
from ultralytics import YOLO

GROUP = "aespa"


def update_model_with_additional_dataset(group=GROUP):
    # GPUが有効かチェック
    if torch.cuda.is_available():
        device = "cuda:0"
        print("CUDA:0 が有効です。")
    else:
        device = "cpu"  # noqa F841
        print("CPU を使用します。")

    ## ../dataset/{GROUP}/を../dataset_copy/{GROUP}/にコピーする(../dataset/{GROUP}は読み取り専用)

    # コピー元とコピー先のパス
    source_dir = f"../dataset/{GROUP}/"
    destination_dir = f"../dataset_copy/{GROUP}/"

    # コピー先ディレクトリが存在しない場合は作成
    os.makedirs(destination_dir, exist_ok=True)

    # ディレクトリの内容を再帰的にコピー
    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

    # ../additional_dataset/{GROUP}の中身は.txtと.jpgの組み合わせの集合
    # .txtを ../dataset_copy/{GROUP}/train/labels にコピーする
    # .jpgを ../dataset_copy/{GROUP}/train/images にコピーする

    # 追加データのディレクトリ
    source_dir = os.path.abspath(f"../additional_dataset/{GROUP}/")

    # コピー先ディレクトリ
    txt_destination = os.path.abspath(f"../dataset_copy/{GROUP}/train/labels/")
    jpg_destination = os.path.abspath(f"../dataset_copy/{GROUP}/train/images/")

    # .txt と .jpg ファイルをそれぞれ対応するディレクトリにコピー
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if filename.endswith(".txt"):
            shutil.copy(file_path, txt_destination)
            print(f"{filename} を {txt_destination} にコピーしました。")
        elif filename.endswith(".jpg"):
            shutil.copy(file_path, jpg_destination)
            print(f"{filename} を {jpg_destination} にコピーしました。")

    # 追加されたデータを用いて最初から学習し直す
    model = YOLO("yolo11n.pt")
    model.train(data=os.path.abspath(f"../dataset_copy/{GROUP}/data.yaml"), epochs=100, imgsz=640)

    # 最新のトレーニングディレクトリからbest.ptを探してカレントディレクトリにコピー
    runs_dir = os.path.join("runs", "detect")
    latest_train_dir = max(
        [d for d in os.listdir(runs_dir) if d.startswith("train")],
        key=lambda x: os.path.getctime(os.path.join(runs_dir, x)),
    )
    best_pt_path = os.path.join("runs", "detect", latest_train_dir, "weights", "best.pt")

    if os.path.exists(best_pt_path):
        shutil.copy(best_pt_path, os.getcwd())  # カレントディレクトリにコピー
        print(f"best.pt を {best_pt_path} からカレントディレクトリにコピーしました。")
    else:
        print("best.pt ファイルが見つかりませんでした。")


if __name__ == "__main__":
    update_model_with_additional_dataset()
