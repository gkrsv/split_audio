import os
import librosa
import argparse
from utils import vad_audio_segment
FFMPEG_BIN = 'ffmpeg'


def convert2wav(audio_file, wav_file):
    try:
        cmd = '{} -i {} -acodec pcm_s16le -ar 16000 -ac 1 {} -y -loglevel panic'.format(
            FFMPEG_BIN, audio_file, wav_file)
        os.system(cmd)
        return True
    except Exception as error:
        print('Error: {}'.format(repr(error)))
        return False


def trim_audio_ffmpeg(src_file, start_tm, end_tm, dst_file):
    osrate = args.osr
    if not os.path.exists(src_file):
        return False

    try:
        cmd = '{} -i {} -ar {} -ac 1 -filter "aresample=isr=44100:osr={}:dither_method=triangular_hp:resampler=swr:filter_type=cubic" -ss {:.2f} -to {:.2f} {} ' \
              '-y -loglevel panic'.format(FFMPEG_BIN, src_file, osrate, osrate, start_tm, end_tm, dst_file)
        os.system(cmd)
        return True
    except Exception as error:
        print('Error: {}'.format(repr(error)))
        return False


def get_duration(wave_file, samplerate=16000):
    y, fs = librosa.load(wave_file, sr=samplerate)
    n_frames = len(y)
    audio_length = n_frames * (1 / fs)

    return audio_length


def audio_split(arguments):
    audio_file = args.input
    min_silence = args.sil
    min_duration = args.min
    max_duration = args.max

    convert_file = audio_file[:-4] + '_convert.wav'
    if not convert2wav(audio_file, convert_file):
        return

    print("Reading from {}".format(audio_file))
    dur = get_duration(convert_file)
    print("Audio duration is {}s".format(dur))

    segments = vad_audio_segment(convert_file)
    if len(segments) == 0:
        print("No segments to split")
        return

    try:
        os.remove(convert_file)
    except:
        pass

    # make a segment using min/max length
    final_list = []
    temp_segment = segments[0]
    for x in segments[1:]:
        cur_duration = x[1] - x[0]
        temp_duration = temp_segment[1] - temp_segment[0]

        # try to split on silences no shorter than min duration
        if x[0] - temp_segment[1] <= min_silence:
            temp_segment[1] = x[1]
            continue
        
        if cur_duration + temp_duration > max_duration:
            final_list.append(temp_segment)
            temp_segment = x
        else:
            temp_segment[1] = x[1]
    final_list.append(temp_segment)

    if final_list[-1][1] - final_list[-1][0] <= min_duration:
        mean_time = (final_list[-2][0] + final_list[-1][1]) / 2
        final_list[-2][1] = mean_time
        final_list[-1][0] = mean_time
        
    # split audio
    split_dir = audio_file[:-4] + '_split'
    os.makedirs(split_dir, exist_ok=True)
    final_list[0][0] = 0
    final_list[-1][1] = dur
    print("Chunks will be saved to {}".format(split_dir))
    for i, seg in enumerate(final_list):
        stime, etime = seg
        if i == 0:
            etime = (etime + final_list[i+1][0]) / 2
        elif i == len(final_list)-1:
            stime = (stime + final_list[i-1][1]) / 2
        else:
            stime = (stime + final_list[i - 1][1]) / 2
            etime = (etime + final_list[i + 1][0]) / 2

        split_audio_file = "{}_{}.wav".format(
            os.path.basename(audio_file)[:-4],
            i+1)
        split_audio_path = os.path.join(split_dir, split_audio_file)
        trim_audio_ffmpeg(audio_file, stime, etime, split_audio_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inp', type=str, required=True, help="Path to audio file (with extension)")
    parser.add_argument('-m', '--min', type=float, default=60.0, help="Min chunk length (s)")
    parser.add_argument('-M', '--max', type=float, default=180.0, help="Max chunk length (s)")
    parser.add_argument('-s', '--sil', type=float, default=1.0, help="Min silence to split on (s)")
    parser.add_argument('-S', '--osr', type=int, default=22050, help="Output sample rate (Hz)")
    args = parser.parse_args()
    
    try:
        audio_split(args)
    except IndexError:
        print("Error: min silence likely too long. Reduce --sil value and rerun")
    else:
        print("Done")
