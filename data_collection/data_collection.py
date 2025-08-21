from pylsl import StreamInlet, resolve_byprop
from psychopy import visual, core, event
import numpy as np
import pandas as pd
import itertools
import os

DATA_SAVE_DIR = './data/'
SESSION_NAME = 'subject01_session01'
TRIAL_DURATION = 3.0   # seconds
INTER_TRIAL_INTERVAL = 2.0   # seconds
NUM_TRIALS_PER_CLASS = 10    # MI and Rest each
EEG_STREAM_NAME = 'EEG_BCI'  # LSL stream name

# Makes directories if they don't exist
os.makedirs(DATA_SAVE_DIR, exist_ok=True)

# Psychopy window, can modify screen size here
win = visual.Window(fullscr=False, size=(1280, 800), winType='pyglet',
                    waitBlanking=False, color='black')
instruction = visual.TextStim(win, text='', height=0.1, color='white')

# Finding LSL stream
print("Looking for an EEG stream…")
streams = resolve_byprop('name', EEG_STREAM_NAME, timeout=5)
if not streams:
    streams = resolve_byprop('type', 'EEG', timeout=5)
if not streams:
    raise RuntimeError("No LSL EEG stream found (name or type). Start GUI or dummy outlet.")
inlet = StreamInlet(streams[0], max_buflen=60)
print("Connected to:", streams[0].name())

# Helper to show the countdown
def show_countdown(win, label):
    for msg in ("Ready", "Set"):
        instruction.text = msg
        instruction.draw(); win.flip()
        core.wait(1.0)
    # Displays experimental condition depending on the injected label
    instruction.text = ("Imagine slowly raising your right arm and extending it outwards"
                        if label == 1 else "Rest.")
    instruction.draw(); win.flip()

# Runs the trial 
def run_trial(win, label, duration=TRIAL_DURATION):
    trial_data, timestamps = [], []
    timer = core.Clock()

    while timer.getTime() < TRIAL_DURATION:
        sample, ts = inlet.pull_sample(timeout=0.0) 
        if sample is not None:
            trial_data.append(sample); timestamps.append(ts)

        instruction.draw(); win.flip()
        core.wait(0.001) 

        if 'escape' in event.getKeys():
            return 'ESCAPE', trial_data, timestamps

    return 'OK', trial_data, timestamps

# Main experiment runner
def run_experiment():
    all_data, all_labels, all_timestamps = [], [], []

    try:
        print("Starting experiment...")

        # Instructions screen
        instruction.text = """Welcome to the Motor Imagery experiment.

Before we begin, you will first practice by actually lifting your right arm and noticing how it feels.
During the experiment, the prompt will guide you to:
 • "Imagine slowly raising your right arm and extending it outwards," or
 • "Rest."

Each trial will start with a countdown:
 • "Ready"
 • "Set"
 • Then the experimental condition ("Rest" or "Imagine...") will appear.

Focus on the instruction shown during each trial.

Press SPACE to begin or ESC to quit."""
        instruction.height = 0.07
        instruction.draw(); win.flip()

        while True:
            keys = event.getKeys()
            if 'space' in keys: break
            if 'escape' in keys:
                win.close(); core.quit()

        # Build labels with NumPy's unbiased permutation 
        rng = np.random.default_rng()
        # 0 = Rest, 1 = MI; exactly NUm_TRIALS of each, shuffled
        labels = rng.permutation(np.repeat([0, 1], NUM_TRIALS_PER_CLASS)).tolist()

        # Loops through trials (with countdowns)
        for idx, label in enumerate(labels):
            print(f"Starting trial {idx+1}/{len(labels)} | {'MI' if label == 1 else 'Rest'}")

            # Use the ITI to show the countdown (Ready 1s + Set 1s)
            if INTER_TRIAL_INTERVAL > 0:
                show_countdown(win, label)

            # Run the trial (condition text already displayed)
            result, trial_data, timestamps = run_trial(win, label)
            if result == 'ESCAPE':
                print("Experiment manually stopped."); break

            # Collect
            all_data.extend(trial_data)
            all_labels.extend([label] * len(trial_data))
            all_timestamps.extend(timestamps)

        print("Experiment completed. Saving data...")

        # Save CSV
        eeg_array = np.array(all_data)
        df = pd.DataFrame(eeg_array, columns=[f"Ch{i+1}" for i in range(eeg_array.shape[1])])
        df["Label"] = all_labels
        df["Timestamp"] = all_timestamps

        csv_path = os.path.join(DATA_SAVE_DIR, f"{SESSION_NAME}.csv")
        df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        win.close(); core.quit()

if __name__ == "__main__":
    run_experiment()
