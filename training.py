from ultralytics import YOLO

# Load YOLOv8 small model
model = YOLO("yolov8s.pt")

# Train!
results = model.train(
    data=r"C:\Users\derin\OneDrive\Desktop\visual\archive\data.yaml",
    epochs=50,
    imgsz=224,
    batch=8,
    name="magnetic_tile_detector",
    project=r"C:\Users\derin\OneDrive\Desktop\visual\model",
    patience=10,
    save=True,
    plots=True,
    augment=True,   # helps with MT_Fray low images
    degrees=10.0,   # rotation augmentation
    fliplr=0.5,     # horizontal flip
    flipud=0.2,     # vertical flip
    hsv_h=0.015,    # color augmentation
    hsv_s=0.7,
    hsv_v=0.4
)

print(f"\n✅ Training Complete!")
print(f"Best model saved at: models/magnetic_tile_detector/weights/best.pt")