### 自動アノテーション
from ultralytics.data.annotator import auto_annotate


# 容量は、sam_l.pt > sam_b.pt
auto_annotate(data="../aespa_dataset/giselle", det_model="yolov8n.pt", sam_model='sam_b.pt', output_dir="../aespa_dataset/giselle_labels")
auto_annotate(data="../aespa_dataset/karina", det_model="yolov8n.pt", sam_model='sam_b.pt', output_dir="../aespa_dataset/karina_labels")
auto_annotate(data="../aespa_dataset/ningning", det_model="yolov8n.pt", sam_model='sam_b.pt', output_dir="../aespa_dataset/ningning_labels")
auto_annotate(data="../aespa_dataset/winter", det_model="yolov8n.pt", sam_model='sam_b.pt', output_dir="../aespa_dataset/winter_labels")

