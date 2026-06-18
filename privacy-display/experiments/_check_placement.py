"""Grab one frame from the USB webcam to check physical placement."""
import sys, time
import cv2

def settings(cap):
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    cc = "".join(chr((fourcc >> 8*i) & 0xFF) for i in range(4)).strip("\x00")
    return (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            round(float(cap.get(cv2.CAP_PROP_FPS)), 1), cc)

backends = [("msmf", cv2.CAP_MSMF), ("dshow", cv2.CAP_DSHOW)]
for dev in (1, 0, 2):
    for bname, bcode in backends:
        cap = cv2.VideoCapture(dev, bcode)
        if not cap.isOpened():
            cap.release(); continue
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # warm up auto-exposure / autofocus
        end = time.time() + 2.0
        frame = None
        while time.time() < end:
            ok, frame = cap.read()
        ok, frame = cap.read()
        if ok and frame is not None:
            w, h, fps, cc = settings(cap)
            out = "experiments/_placement_check.jpg"
            cv2.imwrite(out, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            print(f"OK device={dev} backend={bname} {w}x{h}@{fps} {cc} saved={out}")
            cap.release()
            sys.exit(0)
        cap.release()
print("NO_CAMERA: could not open any device on msmf/dshow")
sys.exit(1)
