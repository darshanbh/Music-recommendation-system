from flask import Flask, render_template, jsonify, Response
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array

import threading
import time
from collections import defaultdict
from flask import request, jsonify
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

SPOTIFY_CLIENT_ID = "5f207c0dd0da47df84d1f18d2f3a07e5"
SPOTIFY_CLIENT_SECRET = "f43414c7182d4b6ea0b387ff456a6d0b"


app = Flask(__name__)

# Load models
face_classifier = cv2.CascadeClassifier(r'haarcascade_frontalface_default.xml')
classifier = load_model(r'model.h5')

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Global camera object
camera = None
camera_lock = threading.Lock()

# Emotion to song mapping
# emotion_songs = {
#     'Angry': [
#         {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'url': 'https://open.spotify.com/track/3qm84nBvXcwhK6YErldlgK'},
#         {'title': 'Seven Nation Army', 'artist': 'The White Stripes', 'url': 'https://open.spotify.com/track/5FOaIawezxsNBdGHISjcNK'},
#         {'title': 'Killing In The Name', 'artist': 'Rage Against The Machine', 'url': 'https://open.spotify.com/track/5qHWQNPcGVp55JgXRpGFmv'}
#     ],
#     'Disgust': [
#         {'title': 'In The End', 'artist': 'Linkin Park', 'url': 'https://open.spotify.com/track/7qiZfU4dY1lsylvNEprXTS'},
#         {'title': 'Crawling', 'artist': 'Linkin Park', 'url': 'https://open.spotify.com/track/4mJIpjJVKvjVoiO8OjqmKp'},
#         {'title': 'Boulevard of Broken Dreams', 'artist': 'Green Day', 'url': 'https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqV'}
#     ],
#     'Fear': [
#         {'title': 'Chop Suey!', 'artist': 'System Of A Down', 'url': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMwbM'},
#         {'title': 'Teardrop', 'artist': 'Massive Attack', 'url': 'https://open.spotify.com/track/4eQ4qPXvQ47vz2GjRhNGfn'},
#         {'title': 'Unknown', 'artist': 'Imagine Dragons', 'url': 'https://open.spotify.com/track/3XVBdyKGUtArF諦'}
#     ],
#     'Happy': [
#         {'title': 'Good as Hell', 'artist': 'Lizzo', 'url': 'https://open.spotify.com/track/1301WleyT98MSxVHPZCA6M'},
#         {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'url': 'https://open.spotify.com/track/52p2rHMQoJGAWDVaVBrHBE'},
#         {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'url': 'https://open.spotify.com/track/1301WleyT98MSxVHPZCA6M'}
#     ],
#     'Neutral': [
#         {'title': 'Chill Vibes', 'artist': 'Various Artists', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DX4UtSsGT1Sbe'},
#         {'title': 'Lo-Fi Beats', 'artist': 'Various Artists', 'url': 'https://open.spotify.com/playlist/0VjIjW4GlUZAMYd2vXMwbM'},
#         {'title': 'Peaceful Piano', 'artist': 'Various Artists', 'url': 'https://open.spotify.com/playlist/37i9dQZF1DWSJHnPUl5asE'}
#     ],
#     'Sad': [
#         {'title': 'Someone Like You', 'artist': 'Adele', 'url': 'https://open.spotify.com/track/2takcwFFVrjo0Vay0TSR5m'},
#         {'title': 'Hurt', 'artist': 'Johnny Cash', 'url': 'https://open.spotify.com/track/3pD1yT2HFroMG1j53RXx1Z'},
#         {'title': 'The Night We Met', 'artist': 'Lord Huron', 'url': 'https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMwbM'}
#     ],
#     'Surprise': [
#         {'title': 'Mr. Blue Sky', 'artist': 'Electric Light Orchestra', 'url': 'https://open.spotify.com/track/3qm84nBvXcwhK6YErldlgK'},
#         {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'url': 'https://open.spotify.com/track/52p2rHMQoJGAWDVaVBrHBE'},
#         {'title': 'Good as Hell', 'artist': 'Lizzo', 'url': 'https://open.spotify.com/track/1301WleyT98MSxVHPZCA6M'}
#     ]
# }

spotify_token = None
spotify_token_time = 0
selected_language = "english"   # default language


def get_spotify_access_token():
    global spotify_token, spotify_token_time

    if spotify_token and (time.time() - spotify_token_time < 3600):
        return spotify_token

    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

    spotify_token = response.json()["access_token"]
    spotify_token_time = time.time()
    return spotify_token


emotion_language_query = {
    "english": {
        "Happy": "happy upbeat english songs",
        "Sad": "sad acoustic english songs",
        "Angry": "angry workout english songs",
        "Fear": "calm relaxing english songs",
        "Disgust": "dark alternative english songs",
        "Neutral": "chill lofi english songs",
        "Surprise": "party hits english songs"
    },
    "hindi": {
        "Happy": "happy bollywood songs",
        "Sad": "sad bollywood songs",
        "Angry": "intense bollywood songs",
        "Fear": "soft bollywood songs",
        "Disgust": "emotional hindi songs",
        "Neutral": "chill hindi songs",
        "Surprise": "bollywood party songs"
    },
    "kannada": {
        "Happy": "happy kannada songs",
        "Sad": "sad kannada songs",
        "Angry": "power kannada songs",
        "Fear": "melody kannada songs",
        "Disgust": "emotional kannada songs",
        "Neutral": "chill kannada songs",
        "Surprise": "kannada party songs"
    }
}


def get_spotify_songs_by_emotion(emotion, limit=5):
    try:
        token = get_spotify_access_token()
        # query = emotion_to_query.get(emotion, "chill")
        query = emotion_language_query.get(
        selected_language, emotion_language_query["english"]
        ).get(emotion, "chill songs")


        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        tracks = response.json()["tracks"]["items"]

        songs = []
        for track in tracks:
            songs.append({
                "title": track["name"],
                "artist": ", ".join(a["name"] for a in track["artists"]),
                "url": track["external_urls"]["spotify"]
            })

        return songs

    except Exception as e:
        print("Spotify API error:", e)
        return []

# Global variables for scan state
scan_active = False
scan_data = {
    'emotion_counts': defaultdict(int),
    'total_frames': 0,
    'emotion_percentages': {},
    'recommended_songs': [],
    'dominant_emotion': None,
    'scan_progress': 0,
    'live_emotions': []  # Store last 10 emotions for real-time display
}

def detect_emotions_15sec():
    global scan_active, scan_data, camera, camera_lock

    scan_duration = 5   # ✅ 5 SECONDS ONLY
    start_time = time.time()

    scan_data = {
        'emotion_counts': defaultdict(int),
        'total_frames': 0,
        'emotion_percentages': {},
        'recommended_songs': [],
        'dominant_emotion': None,
        'scan_progress': 0,
        'live_emotions': []
    }

    with camera_lock:
        cap = camera if camera else cv2.VideoCapture(0)

    while scan_active:
        elapsed = time.time() - start_time

        #  FORCE STOP AFTER  SECONDS
        if elapsed >= scan_duration:
            break

        with camera_lock:
            ret, frame = cap.read()

        if not ret:
            continue

        # ✅ PROGRESS (0–100)
        scan_data['scan_progress'] = int((elapsed / scan_duration) * 100)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.2, 4, minSize=(60, 60))

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (48, 48))
            roi = cv2.equalizeHist(roi)
            roi = roi / 255.0
            roi = roi.reshape(1, 48, 48, 1)

            pred = classifier.predict(roi, verbose=0)[0]
            idx = pred.argmax()
            emotion = emotion_labels[idx]
            confidence = pred[idx] * 100

            if confidence > 5:
                scan_data['emotion_counts'][emotion] += 1
                scan_data['total_frames'] += 1
                scan_data['live_emotions'].append({
                    'emotion': emotion,
                    'confidence': round(confidence, 1)
                })

                if len(scan_data['live_emotions']) > 10:
                    scan_data['live_emotions'].pop(0)

    # ✅ FINALIZE RESULTS
    if scan_data['total_frames'] > 0:
        for emo, cnt in scan_data['emotion_counts'].items():
            scan_data['emotion_percentages'][emo] = round(
                (cnt / scan_data['total_frames']) * 100, 2
            )

        dominant = max(scan_data['emotion_counts'],
                       key=scan_data['emotion_counts'].get)

        scan_data['dominant_emotion'] = dominant
        scan_data['recommended_songs'] = get_spotify_songs_by_emotion(dominant)

    # ✅ HARD STOP
    scan_data['scan_progress'] = 100
    scan_active = False


    if opened_local_camera:
        cap.release()


def generate_frames():
    """Generate video frames with face detection"""
    global camera, camera_lock
    
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        with camera_lock:
            if camera is None:
                break
            ret, frame = camera.read()
        
        if not ret:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces with faster parameters for live feed
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.2, 4, minSize=(60, 60))
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            # Add "Face Detected" label
            cv2.putText(frame, "FACE DETECTED", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add instructions on the frame
        cv2.putText(frame, "Keep your face centered in the green box", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "Make clear facial expressions for better accuracy", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if len(faces) == 0:
            cv2.putText(frame, "NO FACE DETECTED - Please adjust position", (20, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# flask routes
# @app.route('/start_scan', methods=['POST'])
# def start_scan():
#     global scan_active, selected_language

#     data = request.get_json()
#     selected_language = data.get("language", "english")

#     scan_active = True
#     return jsonify({"status": "scan started", "language": selected_language})


# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route"""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan')
def scan_page():
    return render_template('scan.html')

# @app.route('/start_scan', methods=['POST'])
# def start_scan():
#     global scan_active
#     if not scan_active:
#         scan_active = True
#         thread = threading.Thread(target=detect_emotions_15sec)
#         thread.daemon = True
#         thread.start()
#         return jsonify({'status': 'Scan started'})
#     return jsonify({'status': 'Scan already in progress'})

@app.route('/start_scan', methods=['POST'])

def start_scan():
    global scan_active, selected_language

    if scan_active:
        return jsonify({'status': 'already_running'})

    data = request.get_json(silent=True) or {}
    selected_language = data.get("language", "english")

    scan_active = True
    threading.Thread(target=detect_emotions_15sec, daemon=True).start()

    return jsonify({'status': 'started'})



@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    global scan_active
    scan_active = False
    return jsonify({'status': 'Scan stopped'})

@app.route('/get_scan_data', methods=['GET'])
def get_scan_data():
    return jsonify(scan_data)


@app.route('/is_scanning', methods=['GET'])
def is_scanning():
    """Return whether a scan is currently active"""
    return jsonify({'scanning': bool(scan_active)})

@app.route('/reset_data', methods=['POST'])
def reset_data():
    global scan_data
    # Stop any active scan and reset all scan-related state
    global scan_active
    scan_active = False
    scan_data = {
        'emotion_counts': defaultdict(int),
        'total_frames': 0,
        'emotion_percentages': {e: 0.0 for e in ['Angry','Disgust','Fear','Happy','Neutral','Sad','Surprise']},
        'recommended_songs': [],
        'dominant_emotion': None,
        'scan_progress': 0,
        'live_emotions': []
    }
    return jsonify({'status': 'Data reset'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
