import os
import glob
from report_generator import generate_report
from email_alerts import send_daily_summary

# Paths
model_path = r"C:\Users\derin\OneDrive\Desktop\visual\model\magnetic_tile_detector\weights\best.pt"
val_images_path = r"C:\Users\derin\OneDrive\Desktop\visual\archive\images\val"

print("=" * 60)
print("   AI VISUAL QUALITY INSPECTOR — BATCH PROCESSING")
print("=" * 60)

# Get all images from all classes
all_images = []
classes = ["MT_Blowhole", "MT_Break", "MT_Crack", "MT_Fray", "MT_Free"]

for cls in classes:
    cls_path = os.path.join(val_images_path, cls)
    images = glob.glob(os.path.join(cls_path, "*.jpg"))
    images += glob.glob(os.path.join(cls_path, "*.png"))
    images += glob.glob(os.path.join(cls_path, "*.bmp"))
    all_images.extend(images)

print(f"\n✅ Found {len(all_images)} images to inspect")
print("Starting batch inspection...\n")

# Process each image
passed = 0
failed = 0

for i, image_path in enumerate(all_images):
    print(f"\n[{i+1}/{len(all_images)}] Inspecting: {os.path.basename(image_path)}")
    try:
        report = generate_report(image_path, model_path)
        if "PASS" in report:
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"⚠️ Skipped {os.path.basename(image_path)}: {e}")

print("\n" + "=" * 60)
print("   BATCH INSPECTION COMPLETE!")
print("=" * 60)
print(f"✅ Total Inspected : {len(all_images)}")
print(f"✅ Passed          : {passed}")
print(f"❌ Failed          : {failed}")
print(f"📊 Pass Rate       : {passed/len(all_images)*100:.1f}%")
print("=" * 60)
print("\n🚀 Open dashboard to see full analytics:")
print("   streamlit run dashboard.py")
send_daily_summary(
    total     = len(all_images),
    passed    = passed,
    failed    = failed,
    pass_rate = passed/len(all_images)*100
)