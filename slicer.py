import cv2
import mediapipe as mp
import subprocess
import os
import argparse

def detect_faces_and_extract(video_path, output_dir, min_face_duration=3):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    print(f"Processing video: {video_path}")
    print(f"Video duration: {duration:.2f} seconds, FPS: {fps}")

    face_frames = []
    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_frame += 1

        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            face_frames.append(current_frame)

    cap.release()

    cut_times = []
    start_time = 0

    s, e = 0, 0
    while s < len(face_frames):
        while e + 1 < len(face_frames) and face_frames[e + 1] - face_frames[e] == 1:
            e += 1

        if e - s + 1 >= min_face_duration * fps:
            cut_times.append((face_frames[s] / fps, face_frames[e] / fps))

        e += 1
        s = e

    print(f"Detected {len(cut_times)} segments with faces.")

    for i, (start, end) in enumerate(cut_times):
        output_path = os.path.join(output_dir, f"{video_path.split('/')[-1].split('.')[0]}_segment_{i + 1}.mp4")
        print(f"Saving segment {i + 1}: {start:.2f}s to {end:.2f}s")
        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-ss", f"{start:.2f}", "-to", f"{end:.2f}",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "copy",
            output_path
        ], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract video segments where faces appear for a certain duration.")
    parser.add_argument("-i", "--input", required=True, help="Path to input video file (e.g., input.mp4)")
    parser.add_argument("-o", "--output", default="slice_result", help="Output path (default: slice_result)")
    parser.add_argument("-d", "--duration", type=int, default=3, help="Minimum face duration in seconds (default: 3)")
    args = parser.parse_args()

    detect_faces_and_extract(args.input, args.output, args.duration)
