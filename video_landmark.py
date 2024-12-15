import cv2
import mediapipe as mp
import subprocess
import os
import argparse

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=0.5)

def process_video(input_path, output_path, version):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    temp_video_path = os.path.join(output_path, f"temp_{os.path.basename(input_path).rsplit('.', 1)[0]}_v{version}.mp4")
    final_video_path = os.path.join(output_path, f"{os.path.basename(input_path).rsplit('.', 1)[0]}_v{version}.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    if version == 1:
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(128, 128, 128), thickness=1)
                        )
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=drawing_spec
                        )
                    elif version == 2:
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                    elif version == 3:
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_LEFT_EYE,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_RIGHT_EYE,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_LIPS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                    elif version == 4:
                        frame.fill(0)
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_LEFT_EYE,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_RIGHT_EYE,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_LIPS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )

            out.write(frame)

    cap.release()
    out.release()

    subprocess.run([
        "ffmpeg", "-i", temp_video_path, "-i", input_path,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", final_video_path
    ], check=True)

    os.remove(temp_video_path) 
    print(f"Saved output video with audio: {final_video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw MediaPipe Face Mesh landmarks on video.")
    parser.add_argument("-i", "--input", required=True, help="Path to input video file.")
    parser.add_argument("-o", "--output", default="landmark_result", help="Output directory path.")
    parser.add_argument("-v", "--version", type=int, choices=[1, 2, 3, 4], required=True, help="Version of landmark drawing (1-4).")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    process_video(args.input, args.output, args.version)
