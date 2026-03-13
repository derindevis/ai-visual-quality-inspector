import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from database import save_inspection
import datetime
import os

# Load model
@st.cache_resource
def load_model():
    return YOLO("model/magnetic_tile_detector/weights/best.pt")

def get_severity(defect_type, confidence):
    if defect_type in ["MT_Crack", "MT_Break"] and confidence > 0.7:
        return "HIGH 🔴"
    elif confidence > 0.4:
        return "MEDIUM 🟡"
    elif defect_type == "MT_Free":
        return "NONE ✅"
    else:
        return "LOW 🟢"

def get_recommendation(severity):
    if "HIGH" in severity:
        return "REJECT — Do not use"
    elif "MEDIUM" in severity:
        return "REVIEW — Manual inspection needed"
    elif "NONE" in severity:
        return "PASS — No defects found"
    else:
        return "MONITOR — Minor defect detected"

def get_region(x_center, y_center, img_width, img_height):
    vertical   = "Upper" if y_center < img_height / 2 else "Lower"
    horizontal = "Left"  if x_center < img_width  / 2 else "Right"
    return f"{vertical}-{horizontal}"

def run_detection(image):
    model  = load_model()
    img_array = np.array(image)
    results   = model(img_array, conf=0.3)

    detections = []
    annotated  = img_array.copy()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get details
            cls        = int(box.cls[0])
            conf       = float(box.conf[0])
            defect     = result.names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Calculate region
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            region   = get_region(x_center, y_center,
                                  img_array.shape[1], img_array.shape[0])

            severity       = get_severity(defect, conf)
            recommendation = get_recommendation(severity)

            detections.append({
                "defect_type"   : defect,
                "confidence"    : round(conf, 3),
                "severity"      : severity,
                "recommendation": recommendation,
                "region"        : region
            })

            # Draw bounding box
            color = (0, 255, 0)
            if "HIGH"   in severity: color = (0, 0, 255)
            elif "MEDIUM" in severity: color = (0, 165, 255)

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label = f"{defect} {conf:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return annotated, detections

def webcam_page():
    st.title("📷 Live Defect Detection")
    st.markdown("**Capture an image and detect defects in real time!**")
    st.markdown("---")

    # Camera input
    # Camera input with toggle button
    st.subheader("📸 Take a Photo")

    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if not st.session_state.camera_on:
            if st.button("📷 Start Camera", use_container_width=True):
                st.session_state.camera_on = True
                st.rerun()
        else:
            if st.button("⏹️ Stop Camera", use_container_width=True):
                st.session_state.camera_on = False
                st.rerun()

    camera_image = None
    if st.session_state.camera_on:
        camera_image = st.camera_input("Point camera at surface to inspect")
    else:
        st.info("👆 Click 'Start Camera' to begin inspection!")

    if camera_image is not None:
        # Load image
        image = Image.open(camera_image)

        st.markdown("---")
        st.subheader("🔍 Running Detection...")

        # Run detection
        annotated, detections = run_detection(image)

        # Show results
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Image:**")
            st.image(image, use_container_width=True)

        with col2:
            st.markdown("**Detection Result:**")
            st.image(annotated, use_container_width=True)

        st.markdown("---")

        # Show detection details
        if not detections:
            st.success("✅ No defects detected! Surface looks good!")
            # Save to database
            save_inspection(
                image_name     = f"webcam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                defect_type    = "None",
                confidence     = 0.0,
                severity       = "NONE ✅",
                recommendation = "PASS — No defects found",
                region         = "N/A",
                result         = "PASS"
            )
            st.info("✅ Saved to database!")

        else:
            for i, det in enumerate(detections):
                severity = det["severity"]

                if "HIGH" in severity:
                    st.error(f"🔴 Defect {i+1}: {det['defect_type']}")
                elif "MEDIUM" in severity:
                    st.warning(f"🟡 Defect {i+1}: {det['defect_type']}")
                else:
                    st.info(f"🟢 Defect {i+1}: {det['defect_type']}")

                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Confidence",     f"{det['confidence']:.1%}")
                col_b.metric("Severity",       severity)
                col_c.metric("Region",         det["region"])
                col_d.metric("Recommendation", det["recommendation"])

                # Save to database
                result = "FAIL" if "HIGH" in severity or "MEDIUM" in severity else "PASS"
                save_inspection(
                    image_name     = f"webcam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    defect_type    = det["defect_type"],
                    confidence     = det["confidence"],
                    severity       = det["severity"],
                    recommendation = det["recommendation"],
                    region         = det["region"],
                    result         = result
                )

            st.info("✅ Results saved to database!")
            st.markdown("---")
            st.success("📊 Check your dashboard to see updated results!")