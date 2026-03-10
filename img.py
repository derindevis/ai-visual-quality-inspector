import os
import shutil
import random
from PIL import Image

# ✅ Your exact dataset path
base_path = r"C:\Users\derin\OneDrive\Desktop\visual\archive\Magnetic-Tile-Defect"

output_path = r"C:\Users\derin\OneDrive\Desktop\visual\archive"

classes = ["MT_Blowhole", "MT_Break", "MT_Crack", "MT_Fray", "MT_Free"]

# Create output folders
for split in ["train", "val"]:
    for cls in classes:
        os.makedirs(os.path.join(output_path, "images", split, cls), exist_ok=True)
        os.makedirs(os.path.join(output_path, "labels", split, cls), exist_ok=True)

print("✅ Folders created!")

# Split images 80% train, 20% val
for cls in classes:
    img_dir = os.path.join(base_path, cls, "imgs")
    images = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png', '.bmp'))]
    random.shuffle(images)

    split_idx = int(0.8 * len(images))
    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    # Copy to train
    for img in train_imgs:
        shutil.copy(
            os.path.join(img_dir, img),
            os.path.join(output_path, "images", "train", cls, img)
        )

    # Copy to val
    for img in val_imgs:
        shutil.copy(
            os.path.join(img_dir, img),
            os.path.join(output_path, "images", "val", cls, img)
        )

    print(f"✅ {cls}: {len(train_imgs)} train | {len(val_imgs)} val")

print("\n✅ Dataset split complete!")