import os, time
if __name__ == "__main__":
    while 1:
        os.system("python3 capturecharacteristics.py")
        print("Restarting...")
        time.sleep(0.2)  # 200ms to CTR+C twice

