import cv2
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import os
from collections import defaultdict

# --- CONFIGURATION ---
VIDEO_PATH = "traffic_video.mp4"  # Path to input video
OUTPUT_DIR = "output"
MODEL_PATH = "yolov8n.pt"        # Model choice (yolov8n, yolov8s, etc.)
START_FRAME = 0                 # Process from this frame
END_FRAME = 500                 # Process until this frame (None for end of video)
TRACKER = "bytetrack.yaml"      # built-in trackers: "botsort.yaml" or "bytetrack.yaml"
TRAIL_LENGTH = 30               # Length of the trajectory trail in frames

def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Initialize model
    model = YOLO(MODEL_PATH)

    # Open video
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video {VIDEO_PATH}")
        return

    # Video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Determine end frame
    actual_end_frame = END_FRAME if END_FRAME is not None else total_frames
    actual_end_frame = min(actual_end_frame, total_frames)
    
    # Set video writer
    output_video_path = os.path.join(OUTPUT_DIR, "annotated_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Seek to START_FRAME
    cap.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME)

    # Data storage
    trajectory_data = []
    track_history = defaultdict(lambda: []) # Stores last 30 centroids for trails

    # Progress bar
    pbar = tqdm(total=actual_end_frame - START_FRAME, desc="Processing Video")

    frame_count = START_FRAME
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count >= actual_end_frame:
            break

        # Run YOLO tracking
        # persist=True maintains IDs across frames
        results = model.track(source=frame, persist=True, tracker=TRACKER, verbose=False)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            names = results[0].names

            for box, track_id, cls in zip(boxes, track_ids, clss):
                x1, y1, x2, y2 = box
                
                # Centroid math
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                
                class_name = names[cls]

                # Store data for CSV
                trajectory_data.append({
                    "frame": frame_count,
                    "track_id": track_id,
                    "class": class_name,
                    "bbox_x1": x1,
                    "bbox_y1": y1,
                    "bbox_x2": x2,
                    "bbox_y2": y2,
                    "centroid_x": cx,
                    "centroid_y": cy
                })

                # Update track history for trails
                track = track_history[track_id]
                track.append((float(cx), float(cy)))
                if len(track) > TRAIL_LENGTH:
                    track.pop(0)

                # Visualization: Bounding Box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
                # Visualization: Track ID and Class
                label = f"ID: {track_id} {class_name}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Visualization: Trajectory Trail
                if len(track) > 1:
                    for i in range(1, len(track)):
                        pt1 = (int(track[i-1][0]), int(track[i-1][1]))
                        pt2 = (int(track[i][0]), int(track[i][1]))
                        cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

        # Save annotated frame
        out.write(frame)
        
        frame_count += 1
        pbar.update(1)

    # Cleanup
    cap.release()
    out.release()
    pbar.close()

    # Export to CSV
    if trajectory_data:
        df = pd.DataFrame(trajectory_data)
        csv_path = os.path.join(OUTPUT_DIR, "trajectories.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nProcessing complete. Outputs saved in {OUTPUT_DIR}/")
    else:
        print("\nNo detections were made.")

if __name__ == "__main__":
    main()
