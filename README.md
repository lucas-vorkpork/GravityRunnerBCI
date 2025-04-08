# Mind Over Gravity: Binary MI Detection in Gravity Runner

This project focuses on developing a binary classifier that distinguishes between motor imagery (MI) of right-arm movement and a baseline resting state using EEG data. The classifier will operate on a sliding window of X milliseconds, enabling near real-time predictions.

Signal processing methods such as bandpass filtering (8–30 Hz) will be employed to focus on mu and beta rhythms—well-established indicators of MI-related cortical activity. Feature extraction will leverage both Common Spatial Patterns (CSP) to emphasize spatial differences and autoregressive (AR) modeling to capture temporal dynamics within each EEG window. These features will serve as inputs to lightweight machine learning classifiers optimized for live deployment.

The outputs from the classifier will be integrated into a custom-designed Gravity Runner game. In this game, successful MI detection lifts the character to the ceiling, while a resting-state prediction returns the character to the ground. The user must mentally toggle between these states to navigate obstacles, creating an interactive feedback loop that promotes improved motor imagery control through gameplay.


## Project Structure

ui/ # Pygame UI for user interaction
│ ├── main_ui.py # Main UI script
│ └── assets/ # Images, sounds, etc.

data/ # Raw input data (before processing), used for model training

processed_data/ # Data after signal processing, input features for machine_learning

signal_processing/ # Scripts for cleaning and processing data 
│ └── process_signals.py

machine_learning/ # Machine learning models and training scripts
│ └── train_model.py

live_classifier/ # Scripts to classify data live
│ └── live_classify.py

README.md # This file 

requirements.txt # Python package requirements
