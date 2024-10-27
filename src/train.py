from ultralytics import YOLO


model = YOLO("yolov8n.pt")
## batchが大きいと動かない
model.train(data="/Users/watanabeseiya/Desktop/Develop_開発/tk_2420/aespa_dataset_watanabe/data.yaml", epochs=10, batch=20, device='mps')  # 作成したデータセット内のyamlファイルまでのパスを指定