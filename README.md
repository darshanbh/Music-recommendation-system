# Music-recommendation-system

# 🎵 Adaptive Music Recommender Based on Human Emotion

An AI-powered music recommendation system that detects human emotions in real-time using facial expressions and suggests mood-based songs automatically.

---

## 🚀 Overview

This project combines **Computer Vision + Deep Learning** to analyze user emotions via webcam and recommend music accordingly.

A Convolutional Neural Network (CNN) model detects emotions such as **happy, sad, angry, neutral, and surprised**, and maps them to suitable playlists.

---

## 🧠 Features

- 🎯 Real-time face detection using OpenCV  
- 😊 Emotion recognition using CNN  
- 🎶 Mood-based music recommendation  
- ⚡ Automatic song suggestion  
- 🔗 Spotify API integration (for dynamic songs)  
- 💻 Interactive web interface  

---

## 🛠️ Tech Stack

- Python  
- TensorFlow / Keras  
- OpenCV  
- Flask  
- HTML, CSS, JavaScript  
- Spotify API  

---

## ⚙️ Working

1. Capture image from webcam  
2. Detect face using OpenCV  
3. Predict emotion using CNN model  
4. Map emotion to playlist  
5. Recommend songs based on mood  

---

## 📸 Screenshots

> Add your screenshots inside a folder named `screenshots`

![Music Recommendation](screenshots/music-detection-homepage.jpeg)
![Emotion Detection](screenshots/music-detection.jpeg)
![Music results from spotify](screenshots/music-results.png)



---

## 📂 Project Structure


---

## ▶️ Setup Instructions

```bash
# Clone the repository
git clone https://github.com/your-username/hybrid-music-recommender.git

# Go to project folder
cd hybrid-music-recommender

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
