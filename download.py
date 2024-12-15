import csv
import subprocess
import argparse
import os

def download_videos(input_file, output_dir="source_videos"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    try:
        with open(input_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if 'video_id' not in reader.fieldnames:
                print("Error: 'video_id' column not found.")
                return
            
            for row in reader:
                video_id = row['video_id']
                url = f"https://youtu.be/{video_id}"
                print(f"Downloading: {url}")
                
                try:
                    output_path = os.path.join(output_dir, "%(title)s.%(ext)s")
                    subprocess.run([
                        "yt-dlp",
                        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                        "--merge-output-format", "mp4",
                        "-o", output_path,  # 출력 경로 지정
                        url
                    ], check=True)
                except subprocess.CalledProcessError:
                    print(f"Failed to download video: {video_id}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("YouTube Video Downloader running ...")
    parser = argparse.ArgumentParser(description="YouTube video downloader script")
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to CSV file with YouTube video IDs"
    )
    parser.add_argument(
        "-o", "--output",
        default="source_videos",
        help="Directory to save downloaded videos (default: source_videos)"
    )
    args = parser.parse_args()
    download_videos(args.input, args.output)
    print("YouTube Video Downloader completed.")