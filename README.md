# `split_audio.py`

Split audio based on silence and min/max chunk lengths

## Install dependencies

1. FFmpeg: [https://windowsloop.com/install-ffmpeg-windows-10/](https://windowsloop.com/install-ffmpeg-windows-10/)
2. ```pip install -r requirements.txt```


## Usage

```
python3 split_audio.py --inp <input_audio> [--min <min_time> --max <max_time> --sil <min_silence> --osr <osrate>]
```
or
```
python3 split_audio.py -i <input_audio> [-m <min_time> -M <max_time> -s <min_silence> -S <osrate>]
```

**Options**

- `input_audio:` path to input audio file (with extension)
- `min_time:` minimum length of segment in s (default: 60.0)
- `max_time:` maximum length of segment in s (default: 180.0)
- `min_silence:` min silence duration to split on in s (default: 1.0)
- `osrate:` output sample rate in whole Hz (default: 22050)


## Example

```
python3 split_audio.py --inp example.wav --max 600.0 --min 60.0 --sil 1.0 --osr 22050
```
The script outputs the chunks to the `<input_audio>_split` directory
  
## Help

```
python3 split_audio.py --help
```
or
```
python3 split_audio.py -h
```
