# Darknet-dashboard

Simple dashboard for monitoring darknet (https://github.com/AlexeyAB/darknet) training (checked only for yolov4 detection).

Shows current iteration number, loss graph and time left.

Works by parsing log file
```
 2: 3249.455322, 3247.817871 avg loss, 0.000000 rate, 4.869840 seconds, 64 images, 9.561636 hours left
```

## Runing

Run darknet train with ``` > log_file.txt ``` and pass this log file to the app. 

E.g.

```
./darknet detector train yolo.data yolo.cfg yolov4.conv.137 -dont_show -map > ~/dark_logs.txt
```

And then

```
python app.py ~/dark_logs.txt
```

Dash is running on http://127.0.0.1:8050/
