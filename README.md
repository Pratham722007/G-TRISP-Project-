# Vehicle Detection, Tracking, and Trajectory Extraction

This project uses YOLOv8/v10 for real-time vehicle detection and tracking, extracting trajectory data for further analysis.

## 1. Model Choice
The script uses **YOLOv8** (specifically `yolov8n.pt` by default) from the `ultralytics` library. YOLOv8 provides a state-of-the-art balance between speed and accuracy, making it ideal for traffic video analysis.

## 2. Tracking Logic
The project utilizes **ByteTrack** (or optionally **BoT-SORT**) integrated into the Ultralytics framework.
- **ByteTrack**: Focuses on associating almost every detection box instead of only the high-score ones, which helps in maintaining identities during occlusions.
- **Persistence**: The `persist=True` flag in `model.track()` ensures that unique IDs are maintained across consecutive frames.

## 3. How to Run the Script
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Prepare Video**:
    Place your traffic video in the root directory and rename it to `traffic_video.mp4` (or update `VIDEO_PATH` in `main.py`).
3.  **Configure Parameters**:
    Open `main.py` and adjust `START_FRAME` and `END_FRAME` if you only want to process a specific segment.
4.  **Execute**:
    ```bash
    python main.py
    ```

## 4. Output Column Definitions
The `trajectories.csv` file contains the following columns:
- **frame**: The frame number in the video sequence.
- **track_id**: Unique identifier assigned to each vehicle.
- **class**: The type of vehicle (e.g., car, truck, bus).
- **bbox_x1, bbox_y1, bbox_x2, bbox_y2**: Bounding box coordinates (top-left and bottom-right).
- **centroid_x, centroid_y**: The calculated geometric center $(x, y)$ of the vehicle.

## 5. Output Files
- `output/annotated_video.mp4`: Video with bounding boxes, IDs, and trajectory trails (last 30 frames).
- `output/trajectories.csv`: Structured data of all detected vehicle paths.
