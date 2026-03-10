import datetime
from ultralytics import YOLO
import cv2
from database import save_inspection
from email_alerts import send_defect_alert 

# Severity rules
def get_severity(defect_class, confidence):
    high_risk = ["MT_Crack", "MT_Break"]
    if defect_class in high_risk and confidence > 0.7:
        return "HIGH 🔴"
    elif defect_class in high_risk and confidence > 0.4:
        return "MEDIUM 🟡"
    elif defect_class == "MT_Free":
        return "NONE ✅"
    else:
        return "LOW 🟢"

# Recommendation rules
def get_recommendation(severity):
    if "HIGH" in severity:
        return "REJECT — Immediately remove from production line"
    elif "MEDIUM" in severity:
        return "REVIEW — Send for manual inspection"
    elif "NONE" in severity:
        return "PASS — Product cleared for shipment"
    else:
        return "MONITOR — Flag for further observation"

# Region detection
def get_region(box, img_width, img_height):
    x_center = (box[0] + box[2]) / 2
    y_center = (box[1] + box[3]) / 2
    horizontal = "Left" if x_center < img_width/2 else "Right"
    vertical = "Upper" if y_center < img_height/2 else "Lower"
    return f"{vertical}-{horizontal}"

# Main report generator
def generate_report(image_path, model_path):
    # Load model
    model = YOLO(model_path)
    
    # Run detection
    results = model.predict(source=image_path, conf=0.3, save=False)
    
    # Get image dimensions
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # Get current time
    now = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    
    # Build report
    report = []
    report.append("=" * 60)
    report.append("   AI VISUAL QUALITY INSPECTION REPORT")
    report.append("=" * 60)
    report.append(f"Date & Time     : {now}")
    report.append(f"Image           : {image_path.split('/')[-1]}")
    report.append(f"Model           : YOLOv8 Magnetic Tile Detector")
    report.append("-" * 60)
    
    detections = results[0].boxes
    
    
    if len(detections) == 0:
        report.append("Result          : NO DEFECTS DETECTED ✅")
        report.append("Recommendation  : PASS — Product cleared for shipment")
        image_name = image_path.split("\\")[-1]
        save_inspection(
            image_name     = image_name,
            defect_type    = "None",
            confidence     = 0.0,
            severity       = "NONE",
            recommendation = "PASS — Product cleared for shipment",
            region         = "N/A",
            result         = "PASS"
        )
    else:
        report.append(f"Total Defects   : {len(detections)}")
        report.append("-" * 60)
        
        highest_severity = "LOW"
        
        for i, box in enumerate(detections):
            cls_id = int(box.cls)
            cls_name = results[0].names[cls_id]
            confidence = float(box.conf)
            coords = box.xyxy[0].tolist()
            region = get_region(coords, w, h)
            severity = get_severity(cls_name, confidence)
            
            report.append(f"Defect #{i+1}")
            report.append(f"  Type          : {cls_name}")
            report.append(f"  Confidence    : {confidence*100:.1f}%")
            report.append(f"  Location      : {region} region")
            report.append(f"  Severity      : {severity}")
            report.append("")
            
            if "HIGH" in severity:
                highest_severity = "HIGH"
            elif "MEDIUM" in severity and highest_severity != "HIGH":
                highest_severity = "MEDIUM"
            image_name = image_path.split("\\")[-1]
            recommendation = get_recommendation(severity)
            result = "PASS" if cls_name == "MT_Free" else "FAIL"
            save_inspection(
                image_name     = image_name,
                defect_type    = cls_name,
                confidence     = confidence,
                severity       = severity,
                recommendation = recommendation,
                region         = region,
                result         = result
            )
            if "HIGH" in severity:
             send_defect_alert(
                image_name     = image_name,
                defect_type    = cls_name,
                confidence     = confidence,
                severity       = severity,
                region         = region,
                recommendation = recommendation
            )
        
        report.append("-" * 60)
        recommendation = get_recommendation(highest_severity + " 🔴")
        report.append(f"Overall Severity: {highest_severity}")
        report.append(f"Recommendation  : {recommendation}")
    
    report.append("=" * 60)
    report.append("         Powered by  AI")
    report.append("=" * 60)
    
    # Print report
    final_report = "\n".join(report)
    print(final_report)
    
    # Save report to file
    report_path = f"reports/report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    import os
    os.makedirs("reports", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    print(f"\n✅ Report saved to: {report_path}")
    return final_report

# Run it!
if __name__ == "__main__":
    model_path = r"C:\Users\derin\OneDrive\Desktop\visual\model\magnetic_tile_detector\weights\best.pt"
    
    # Test with one image from your dataset
    test_image = r"C:\Users\derin\OneDrive\Desktop\visual\archive\images\val\MT_Crack\exp4_num_265677.jpg"
    
    generate_report(test_image, model_path)