# 🛡️ DeepShield – AI-Based Deepfake Detection Browser Plugin


DeepShield is an AI-powered browser extension designed to detect deepfake images and videos in real-time while browsing the internet. It helps users identify manipulated media and prevents the spread of misinformation by analyzing content directly on web pages.



## 🚀 Features

* 🔍 Real-time deepfake detection
* 🌐 Browser extension integration (Chrome)
* 🤖 AI model for image/video analysis
* ⚡ Fast API-based detection system
* 📊 Confidence score for predictions
* 🛡️ Helps prevent misinformation and cybercrime

---

## 🧠 Problem Statement

With the rapid growth of deepfake technology, it has become increasingly difficult to differentiate between real and fake media. This creates serious issues such as:

* Fake news spread
* Identity misuse
* Cybercrime and fraud

DeepShield aims to provide a reliable solution by detecting deepfake content instantly.

---

## 💡 Solution

DeepShield uses deep learning models (CNN-based) to analyze media content and determine whether it is real or fake. The system integrates:

* Frontend browser extension
* Backend API server
* AI model for detection

---

## 🏗️ System Architecture

1. User browses a webpage
2. Extension scans media (images/videos)
3. Media is sent to backend API
4. AI model processes the data
5. Result (Real/Fake + Confidence) is returned
6. Extension displays alert to user

---

## 🧰 Tech Stack

### Frontend

* HTML
* CSS
* JavaScript (Chrome Extension APIs)

### Backend

* Python
* Flask / Django REST Framework

### AI/ML

* TensorFlow / Keras
* CNN (Convolutional Neural Networks)

### Dataset

* FaceForensics++
* DeepFake Detection Challenge Dataset

---

## 📂 Project Structure

```
DeepShield/
│
├── backend/
│   ├── app.py
│   ├── fix_h5.py
│   └── requirement.txt
│
├── model/
│   ├── model.py
│   ├── train.py
│   ├── data_loader.py
│   └── requirements.txt
│
├── deepshield extension/
│   ├── popup.html
│   ├── popup.js
│
├── auto_train.py
└── README.md
```

---



## ▶️ Usage

* Open any website with media
* Click DeepShield extension
* It scans content automatically
* Displays whether media is **Real or Fake**

---

## 📊 Output

* Real / Fake classification
* Confidence score (e.g., 92% Fake)

---

## 🔐 Applications

* Social media monitoring
* News verification
* Cybercrime prevention
* Digital forensics

---

## ⚠️ Limitations

* Detection accuracy depends on dataset
* High-quality deepfakes may be harder to detect
* Requires internet connection for API

---

## 🔮 Future Enhancements

* Real-time video stream detection
* Mobile app version
* Improved model accuracy using GAN-based detection
* Integration with social media platforms

---

## 👨‍💻 Author

* Your Name (Final Year CSE Student)

---

## 📜 License

This project is for educational purposes only.

---

## ⭐ Conclusion
<img width="1122" height="858" alt="Screenshot 2025-10-16 110333" src="https://github.com/user-attachments/assets/56969cae-9e48-4600-93a8-dc70d6b7f2ca" />

DeepShield provides an effective AI-based solution to detect deepfake media in real-time. It enhances digital trust and helps combat misinformation in modern internet ecosystems.
