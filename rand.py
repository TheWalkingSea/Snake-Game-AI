import os
import threading
def main(): os.system(r"python C:\Users\msm67\Downloads\Snake-Game-AI\snakeOFFICAL.py")
threads = list()
for i in range(10):
    t = threading.Thread(target=main)
    threads.append(t)
    t.start()