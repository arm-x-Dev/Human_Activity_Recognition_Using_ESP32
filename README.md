# ESP32 TinyML Wi-Fi CSI Human Activity Recognition (HAR) System

![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20Xtensa-E73A3E?style=for-the-badge&logo=espressif&logoColor=white)
![Language](https://img.shields.io/badge/Language-Python%20%7C%20C%2B%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/TinyML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Graphics](https://img.shields.io/badge/UI-Pygame%20Telemetry-darkgreen?style=for-the-badge&logo=pygame&logoColor=white)
![Signal](https://img.shields.io/badge/Signal-Wi--Fi%20CSI-blue?style=for-the-badge)

An advanced, edge-AI telemetry radar system that repurposes standard Wi-Fi signals into a passive motion sensor. By tracking Channel State Information (CSI) anomalies on bare-metal ESP32 microcontrollers, this system extracts environmental perturbations and classifies human activities locally on the edge using a compiled Machine Learning decision tree. The system streams real-time telemetry to a high-resolution dark-themed data cockpit.

---

## 🚀 How to Run the System

Follow these steps in order to get your live telemetry radar cockpit up and running:

### 1. Hardware Initialization
* **Flash the Firmware:** Open the Arduino IDE and flash `ESP32_CSI_Transmitter.ino` to your transmitter board and `ESP32_CSI_Receiver.ino` to your receiver board.
* **Boot the Hardware:** Power on both boards and position them roughly 1–2 meters apart on your desk. Press the **EN (Reset)** button on both chips to ensure a clean hardware boot.
* **Port Lock Check:** Ensure the Arduino IDE Serial Monitor is **completely closed** so Windows unlocks the USB communication port.

### 2. Software Environment Setup
Open your terminal inside the project directory and activate your virtual environment, then install the required graphic and serial communication dependencies:

# Activate your virtual environment (Windows)
```bash
.venv\Scripts\activate
```
# Install dependencies
```bash
pip install pygame pyserial numpy
```
### 3\. Launching the Data Cockpit
Run the main visualization script to open your high-resolution telemetry dashboard:
```bash
python dashboard.py
```
_Once the window opens, sit perfectly still for the initial frame sync, then move your hands or body between the antennas to watch the real-time oscilloscope wave and classification cards react live!_

🧠 What AI/ML is Used and Why
-----------------------------

Instead of relying on heavy cloud computers, this project utilizes **TinyML (Tiny Machine Learning)** principles to run intelligence directly on cheap, low-power microcontrollers.

### 1\. What Exactly is Used?

*   **Signal Feature Extraction:** The system isolates subcarrier indices 10 through 60 from the raw Wi-Fi packets. It calculates the **Active Mean (Amplitude)** and the **Standard Deviation (Variance)** of the signal waveform over a moving historical window of 30 frames.
    
*   **C++ Inline Decision Tree (model.h):** The extracted features are processed through a supervised Machine Learning **Decision Tree Classifier**. The trained tree mathematical rules are exported directly into static C++ code (model.h), evaluating floating-point logic gates on the raw hardware in microseconds.
    
*   **Three-State Predictive Output:** \* **Index 0 (STATIC BASELINE):** High amplitude stability, near-zero variance.
    
    *   **Index 1 (DYNAMIC MOTION):** Moderate amplitude absorption drops, localized variance spikes.
        
    *   **Index 2 (HIGH-INTENSITY TRANSIENT):** Massive amplitude attenuation, explosive multi-point standard deviation spikes.
      
### 2\. Why Was This Approach Used?

*   **Zero Cloud Dependency:** Processing everything on the edge means the system works completely offline. No data ever leaves your room, ensuring total privacy.
    
*   **Ultra-Low Latency:** By converting complex mathematical matrices into standard C++ if-else gates inside model.h, the ESP32 can make hundreds of physical predictions per second with zero lag.
    
*   **Environmentally Adaptive:** Tracking the signal variance allows the system to easily filter out background electromagnetic noise (like a nearby router), making it highly sensitive to true human movement while staying incredibly stable.

---

## 🛠️ System Architecture

The physical system pipeline operates entirely locally across three distinct layers:

1. **Physical Layer:** The Transmitter blasts raw IEEE 802.11 packets. The Receiver intercepts these packets and extracts raw Channel State Information (CSI) matrix frames representing the physical indoor environment.
2. **Edge ML Inference Layer (`model.h`):** The ESP32 parses the subcarriers, computes a windowed rolling standard deviation, and pipes the features into the hardcoded compilation tree gates to evaluate human state changes instantly.
3. **Visualization Layer (`dashboard.py`):** A single-threaded, highly optimized Pygame engine reads the calculated predictions via a structured USB serial line, updating live vector waveforms on the dark telemetry cockpit layout.

---

## 🤝 Contributing

Contributions to improve subcarrier feature engineering, filter background multipath fading, or add new dynamic UI visualization layers are highly welcome! 

1. Fork the project repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'feat: add custom high-pass noise filter'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a professional Pull Request for review.

---

## 📄 License

Distributed under the MIT License. See the local `LICENSE` file for more details regarding open-source reuse permissions.

---

## 💎 Acknowledgments

* **Espressif Systems:** For opening up native access to the underlying raw Wi-Fi physical layer (PHY) Channel State Information registers.
* **Scikit-Learn Community:** For providing the training algorithms used to build and prune the foundational human activity decision trees.
