import os
import yaml

output_path = r"C:\Users\derin\OneDrive\Desktop\visual\archive"

classes = ["MT_Blowhole", "MT_Break", "MT_Crack", "MT_Fray", "MT_Free"]

# Generate YOLO label files
for split in ["train", "val"]:
    for cls_idx, cls in enumerate(classes):
        img_dir = os.path.join(output_path, "images", split, cls)
        lbl_dir = os.path.join(output_path, "labels", split, cls)
        os.makedirs(lbl_dir, exist_ok=True)

        for img_file in os.listdir(img_dir):
            if not img_file.endswith(('.jpg', '.png', '.bmp')):
                continue
            label = f"{cls_idx} 0.5 0.5 1.0 1.0\n"
            label_file = os.path.splitext(img_file)[0] + ".txt"
            with open(os.path.join(lbl_dir, label_file), "w") as f:
                f.write(label)

        print(f"✅ Labels generated for {cls} - {split}")

# Create data.yaml
data_config = {
    "path": output_path.replace("\\", "/"),
    "train": "images/train",
    "val": "images/val",
    "nc": 5,
    "names": classes
}

yaml_path = os.path.join(output_path, "data.yaml")
with open(yaml_path, "w") as f:
    yaml.dump(data_config, f, default_flow_style=False)

print("\n✅ data.yaml created!")
print(f"✅ All labels generated successfully!")