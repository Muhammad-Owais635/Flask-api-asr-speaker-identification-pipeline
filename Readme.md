# ASR and Speaker Identification API

This project provides a modular API service that integrates **Automatic Speech Recognition (ASR)** and **Speaker Identification**. The API is structured into several Python scripts and shell utilities to process `.wav` files, transcribe audio, identify speakers, and return enriched text.

---

## 📁 Project Structure

### 1. `wsgi.py`
Used to run the service with Gunicorn. It imports the API class (from `ASR_SR_API.py`) to start the service.

---

### 2. `ASR_SR_API.py`
Main API logic. Contains a class `ASR_API` with the following methods:

#### ▸ `ASR(self)`
- Accepts user requests (must include a `.wav` file)
- Saves the audio to a folder
- Sends the audio to the ASR system and receives a transcript (text file)
- Passes the transcript and audio to `Speaker_Recognition()`

#### ▸ `Speaker_Recognition()`
Performs speaker identification:
- Generates audio segments
- Passes segments to the speaker identification model
- Receives output mapping each segment to a speaker ID
- Passes result to `replace_speaker_ids()`

#### ▸ `replace_speaker_ids()`
- Uses a speaker mapping file to replace IDs with actual speaker names

#### ▸ `read_speaker_segment_names()`
- Extracts segment names from a given file

---

### 3. `Api_Sre_ivec_make_predictions.sh`
Shell script to run **Speaker Identification** using extracted features and trained models.

---

### 4. `generator.py`
Generates the following required input files:
- `ut2spk`
- `wav.scp`
- `target_reference`

These files are used by the Speaker Identification shell script.

---

### 5. `segmentor.py`
- Generates audio segments based on the `.wav` file and the transcript returned by ASR.

---

### 6. `asr_client.py`
- Sends `.wav` files to the ASR system and returns the transcribed text.

---

### 7. `Call_ASR_API.py`
- Utility script to test and consume the API services (for local or integration testing).

---

## 📁 Student Model (ASR Only)

### 1. `wsgi_1.py`
- Runs a simpler service using only ASR (no speaker identification).
- Imports the `ASR_ONLY.py` API module.

### 2. `ASR_ONLY.py`
Contains the simplified API class for ASR:

#### ▸ `ASR(self)`
- Validates input
- Sends the `.wav` file to the ASR system
- Returns the transcription text file

---

## 🚀 Use Cases

- Speaker diarization in meetings
- Transcription and labeling of recorded interviews
- Audio data preprocessing for downstream NLP tasks

---

## 🧪 Notes
- Input must be a `.wav` file.
- Ensure speaker mapping and models are properly configured.

