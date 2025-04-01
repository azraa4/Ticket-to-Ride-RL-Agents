import tkinter as tk
from tkinter import filedialog
import matplotlib
matplotlib.use("TkAgg")  # Force a known backend if needed
import matplotlib.pyplot as plt

def main():
    # 1. Hide the main Tkinter window (we only want the file dialog)
    root = tk.Tk()
    root.withdraw()

    # 2. Let the user select the CSV/TXT file to read
    file_path = filedialog.askopenfilename(
        title="Select training_loss.txt File",
        filetypes=[("Text or CSV Files", "*.txt *.csv"), ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    # 3. Read the file, skipping the header line
    losses = []
    with open(file_path, "r") as f:
        header_line = next(f)  # skip "episode,batch,loss"
        print("Header line:", header_line.strip())  # optional: just to confirm

        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                try:
                    loss_value = float(parts[2])
                    losses.append(loss_value)
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")

    if not losses:
        print("No valid loss values found in the file.")
        return

    # 4. Define the chunk size (window) for averaging
    chunk_size = 10  # change to 5, 20, etc. to get more or less smoothing
    chunked_losses = []
    temp_chunk = []

    for i, val in enumerate(losses):
        temp_chunk.append(val)
        # once we accumulate 'chunk_size' elements, compute average
        if (i + 1) % chunk_size == 0:
            avg_val = sum(temp_chunk) / len(temp_chunk)
            chunked_losses.append(avg_val)
            temp_chunk = []

    # If there's a leftover partial chunk at the end, you can average it, too
    if temp_chunk:
        avg_val = sum(temp_chunk) / len(temp_chunk)
        chunked_losses.append(avg_val)

    # 5. Create x-values to align the chunked averages with the raw data
    # For chunk i, it covers indexes [i*chunk_size .. (i+1)*chunk_size-1].
    # We'll put the chunked point at the midpoint of that range:
    x_chunked = []
    for i in range(len(chunked_losses)):
        # midpoint in that chunk
        midpoint = (i * chunk_size) + (chunk_size - 1) / 2.0
        x_chunked.append(midpoint)

    # 6. Plot both curves: raw + averaged
    plt.figure()
    plt.plot(range(len(losses)), losses, label="Raw Loss")
    plt.plot(x_chunked, chunked_losses, label=f"Averaged (every {chunk_size} steps)")
    plt.xlabel("Replay Calls")
    plt.ylabel("Loss")
    plt.title("Loss Over Time (Raw vs. Smoothed)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
