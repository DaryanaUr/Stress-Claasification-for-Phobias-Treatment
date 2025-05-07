# Stress Classification for Phobias Treatment

This project is a real-time stress detection and classification system that uses **Galvanic Skin Response (GSR)** and **Heart Rate (HR)** signals to evaluate physiological stress levels. It integrates a **deep learning model (LSTM)** for classification and controls a Unity-based therapy environment via **Lab Streaming Layer (LSL)** triggers.


⚠️ **Disclaimer**: The datasets used for training the model are **private** due to the confidentiality of physiological and biometric data. This repository is shared **only for illustrative purposes**, so this repository includes the tools for data collection, model training, and real-time inference and control that I used.

---

## 🔧 Requirements

I recommend using a **virtual environment** to isolate your dependencies.

And don't forget to install the required libraries:
pip install tensorflow scikit-learn numpy pandas matplotlib pyserial pynput pylsl
