import cv2
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import os
from collections import defaultdict

# --- CONFIGURATION ---
VIDEO_PATH = "../traffic_video.mp4"  # Path to input video (adjust as needed)
OUTPUT_DIR = "output_task2"
MODEL_PATH = "yolov8n.pt"           # Model choice
START_FRAME = 0
END_FRAME = 500
TRACKER = "bytetrack.yaml"
TRAIL_LENGTH = 30

# Traffic-related classes in COCO: car(2), truck(3), bus(5), motorcycle(7)
VEHICLE_CLASSES = [2, 3, 5, 7]

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video {VIDEO_PATH}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    actual_end_frame = END_FRAME if END_FRAME is not None else total_frames
    actual_end_frame = min(actual_end_frame, total_frames)
    
    output_video_path = os.path.join(OUTPUT_DIR, "annotated_video_filtered.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME)

    trajectory_data = []
    track_history = defaultdict(lambda: [])

    pbar = tqdm(total=actual_end_frame - START_FRAME, desc="Processing Video (Task 2 - Filtered)")

    frame_count = START_FRAME
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count >= actual_end_frame:
            break

        # Run YOLO tracking with class filtering
        results = model.track(
            source=frame, 
            persist=True, 
            tracker=TRACKER, 
            classes=VEHICLE_CLASSES, # TASK 2: Filter classes
            verbose=False
        )

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            names = results[0].names

            for box, track_id, cls in zip(boxes, track_ids, clss):
                x1, y1, x2, y2 = box
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                class_name = names[cls]

                trajectory_data.append({
                    "frame": frame_count,
                    "track_id": track_id,
                    "class": class_name,
                    "bbox_x1": x1, "bbox_y1": y1, "bbox_x2": x2, "bbox_y2": y2,
                    "centroid_x": cx, "centroid_y": cy
                })

                track = track_history[track_id]
                track.append((float(cx), float(cy)))
                if len(track) > TRAIL_LENGTH: track.pop(0)

                # Visuals
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)
                cv2.putText(frame, f"ID:{track_id} {class_name}", (int(x1), int(y1)-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                if len(track) > 1:
                    for i in range(1, len(track)):
                        cv2.line(frame, (int(track[i-1][0]), int(track[i-1][1])), 
                                 (int(track[i][0]), int(track[i][1])), (0, 165, 255), 2)

        out.write(frame)
        frame_count += 1
        pbar.update(1)

    cap.release()
    out.release()
    pbar.close()

    if trajectory_data:
        pd.DataFrame(trajectory_data).to_csv(os.path.join(OUTPUT_DIR, "trajectories_filtered.csv"), index=False)
        print(f"\nTask 2 complete. Outputs in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
