import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), "propose_similar_kpop_idle"))

print(sys.path)
# import AdaFace.net as net
import net
import numpy as np
import torch
# from AdaFace.face_alignment import align
from face_alignment import align


def load_pretrained_model(architecture="ir_50", model_path="AdaFace/pretrained/adaface_ir50_ms1mv2.ckpt"):
    adaface_models = {
        "ir_50": model_path,
    }
    # load model and pretrained statedict
    assert architecture in adaface_models.keys()
    model = net.build_model(architecture)
    statedict = torch.load(adaface_models[architecture], map_location=torch.device("cpu"))["state_dict"]
    model_statedict = {key[6:]: val for key, val in statedict.items() if key.startswith("model.")}
    model.load_state_dict(model_statedict)
    model.eval()
    return model


def to_input(pil_rgb_image):
    np_img = np.array(pil_rgb_image)
    brg_img = ((np_img[:, :, ::-1] / 255.0) - 0.5) / 0.5
    tensor = torch.tensor([brg_img.transpose(2, 0, 1)]).float()
    return tensor


if __name__ == "__main__":
    model = load_pretrained_model("ir_50")

    test_image_path = "AdaFace/face_alignment/test_images"
    features = []
    print(sorted(os.listdir(test_image_path)))
    for fname in sorted(os.listdir(test_image_path)):
        path = os.path.join(test_image_path, fname)
        aligned_rgb_img = align.get_aligned_face(path)
        bgr_tensor_input = to_input(aligned_rgb_img)
        feature, _ = model(bgr_tensor_input)
        print(feature.shape)
        features.append(feature)

    similarity_scores = torch.cat(features) @ torch.cat(features).T
    print(similarity_scores)
