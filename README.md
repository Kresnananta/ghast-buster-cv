# Ghast Buster

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Status](https://img.shields.io/badge/Status-In_Development-yellow?style=flat)

## Description

A computer vision-based mini-game inspired by Minecraft mechanics, built entirely using **OpenCV** and **NumPy**.

*This project was developed to fulfill the requirements of the **Computer Vision** course taught by `Arta Kusuma Hernanda, B.S., M.S.`*

> **Name**: Anak Agung Ngurah Agung Kresna Ananta  
> **Department**: Computer Engineering  
> **NRP**: 5024241085

## Features

* **Real-Time Hand Tracking:** Utilizes HSV color space masking, morphological operations, and image moments to accurately track the player's hand position.
* **Dynamic Color Calibration:** Export and import skin color HSV profiles (`.json`) on the fly using Tkinter file explorer dialogs.
* **Custom Alpha Blending:** Manually implements NumPy matrix operations to seamlessly overlay transparent `.png` assets (Shield and Fireballs) without performance drops.
<!-- * **Finite State Machine (FSM):** Clean architectural design separating the application into distinct `START`, `PLAYING`, and `GAME OVER` states. -->

## Project Structure

```text
ghast-buster-cv/
├── asset/                 # Contains game sprites
├── preset/                # Stores exported HSV calibration profiles (.json)
├── constants.py           # Anything constant
├── main.py                # Core game loop
├── calibrateCam.py        # Calibrate skin color
├── .gitignore             # Excludes __pycache__ and local environments
└── README.md              # Project documentation
```

## Instalation

1. **Clone the repository**
    ```bash
    git clone https://github.com/Kresnananta/ghast-buster-cv.git
    cd ghast-buster-cv
    ```
2. **Install dependencies**
    ```bash
    pip install opencv-python numpy
    ```
3. **Run the game**
    ```bash
    python main.py
    ```

## How to Play
1. **Calibration (Important)**  
    Lighting conditions affect computer vision heavily. Before playing, run `calibrate.py` to adjust the **HSV sliders** until your hand is completely white (and the background is black) in the Mask window. Click Export JSON to save your environment's preset.
2. **Keybinds You Must Know**
    - `i` : Import your saved .json color preset (can be done during the game).
    - `s` : Save preset in `calibrateCam.py`.
    - `q` : Quit the application.

## Project Progress
This project is currently under active development. Below is the checklist of planned and completed features:
- [x] **Phase 1: Core Engine & Calibration**
  - [x] Initialize OpenCV camera feed and basic mirroring.
  - [x] Implement HSV skin color masking and morphological noise reduction.
  - [x] Add functionality to Export/Import `.json` color presets using Tkinter `filedialog` module.

- [ ] **Phase 2: Game Architecture**
  - [ ] Set up Finite State Machine (START, PLAYING, GAME OVER).
  - [x] Modularize codebase (`main.py`, <!--vision.py`,--> `constants.py`).

- [ ] **Phase 3:**  
. . .

:0