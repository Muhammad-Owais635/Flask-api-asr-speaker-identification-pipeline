import wave
import os
import argparse
import scipy.io.wavfile
import numpy as np
import shutil

def validate_wav(file):
    print("Validating input audio file...")
    try:
        with wave.open(file, 'r') as audio:
            sample_rate = audio.getframerate()
            num_frames = audio.getnframes()
            print("Sampling Rate:", sample_rate)
            print("Number of Frames:", num_frames)
            print("Sample Width:", audio.getsampwidth())
            duration_min = (num_frames / sample_rate) // 60
            duration_sec = (num_frames / sample_rate) % 60
            print("File Duration:", duration_min, "Minutes", duration_sec, "Seconds")
            print("Successfully validated WAV file.")
        return True
    except wave.Error as err:
        print(err)
        return False

def cutter(wav_file, seg_file):
    print("Segmenting audio file...")
    with open(seg_file, 'r') as f:
        lines = f.readlines()

    fs, audio_data = scipy.io.wavfile.read(wav_file)
    base_name = os.path.basename(wav_file)
    file_name = os.path.splitext(base_name)[0]
    file_dir = os.path.join("Audios",file_name)
    print(file_dir)
    print("File Name:", file_name)
    if os.path.exists(file_dir):
        shutil.rmtree(file_dir)
    os.mkdir(file_dir)

    for i, line in enumerate(lines, start=1):
        segment_info = line.strip().split("\t")
        segment_name, speaker_id, start_time, end_time, segment_text = segment_info

        segment_id = f"{file_name}_S{i}"
        segment_file = os.path.join(file_dir, f"{segment_id}.wav")
        segment_start = int(float(start_time) * fs)
        segment_end = int(float(end_time) * fs)

        segment_audio = audio_data[segment_start:segment_end]
        scipy.io.wavfile.write(segment_file, fs, segment_audio)

        #text_file = os.path.join(file_name, "text.txt")
        #with open(text_file, "a") as f:
         #   f.write(f"{segment_id}\t{segment_text}\n")

    print("Segmentation completed.")

def main():
    parser = argparse.ArgumentParser(description='This script segments an audio file based on a provided segment file.')
    parser.add_argument('wav_file', help='input WAV file')
    parser.add_argument('seg_file', help='segment file with format "Segment\\tSpeaker ID\\tStart\\tEnd\\tText"')
    args = parser.parse_args()

    if validate_wav(args.wav_file):
        cutter(args.wav_file, args.seg_file)

if __name__ == "__main__":
    main()

