import cv2
import mediapipe as mp
import os
import argparse
import subprocess

def find_global_face_region(video_path, min_detection_confidence=0.5, expand_ratio=1.2):
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=min_detection_confidence)

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x_min_global, y_min_global = width, height
    x_max_global, y_max_global = 0, 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                x, y, w, h = bboxC.xmin, bboxC.ymin, bboxC.width, bboxC.height

                abs_x = int(x * width)
                abs_y = int(y * height)
                abs_w = int(w * width)
                abs_h = int(h * height)

                x_min_global = min(x_min_global, abs_x)
                y_min_global = min(y_min_global, abs_y)
                x_max_global = max(x_max_global, abs_x + abs_w)
                y_max_global = max(y_max_global, abs_y + abs_h)

    cap.release()

    center_x = (x_min_global + x_max_global) // 2
    center_y = (y_min_global + y_max_global) // 2
    side_length = max(x_max_global - x_min_global, y_max_global - y_min_global)
    side_length = int(side_length * expand_ratio)

    x1 = max(0, center_x - side_length // 2)
    y1 = max(0, center_y - side_length // 2)
    x2 = min(width, center_x + side_length // 2)
    y2 = min(height, center_y + side_length // 2)

    return x1, y1, x2, y2

def crop_video_with_fixed_region(video_path, output_path, crop_region, resize_dim=(256, 256)):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    cropped_video_path = os.path.join(output_path, "cropped_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(cropped_video_path, fourcc, fps, resize_dim)

    x1, y1, x2, y2 = crop_region
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        face_crop = frame[y1:y2, x1:x2]
        face_resized = cv2.resize(face_crop, resize_dim)
        out.write(face_resized)

    cap.release()
    out.release()

    return cropped_video_path

def add_audio_to_video(original_video, cropped_video, final_output):
    subprocess.run([
        "ffmpeg", "-i", cropped_video, "-i", original_video,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", final_output
    ])
    print(f"Saved final video with audio to {final_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop video based on global face region and retain audio.")
    parser.add_argument("-i", "--input", required=True, help="Path to input video file (e.g., input.mp4)")
    parser.add_argument("-o", "--output", default="crop_result", help="Path to output directory (default: crop_result)")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    print("Finding global face region...")
    crop_region = find_global_face_region(args.input)
    print(f"Global crop region: {crop_region}")

    print("Cropping video with fixed region...")
    cropped_video_path = crop_video_with_fixed_region(args.input, args.output, crop_region)

    print("Adding audio to cropped video...")
    final_output_path = os.path.join(args.output, f"cropped_{os.path.basename(args.input).split('/')[-1]}")
    add_audio_to_video(args.input, cropped_video_path, final_output_path)

    os.remove(cropped_video_path)