# import noisereduce as nr
# import librosa
# import soundfile as sf

# def remove_noise(input_path, output_path):
#     data, rate = librosa.load(input_path, sr=None)
#     noise_sample = data[0:int(rate*0.5)]  # first 0.5 seconds as noise
#     reduced_noise = nr.reduce_noise(y=data, y_noise=noise_sample, sr=rate)
#     sf.write(output_path, reduced_noise, rate)


# utils.py
import librosa
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import os

def remove_noise(input_path, output_path):
    # Convert to .wav using pydub (ffmpeg required)
    sound = AudioSegment.from_file(input_path)
    wav_path = input_path.rsplit('.', 1)[0] + '_temp.wav'
    sound.export(wav_path, format='wav')

    # Load converted WAV file
    data, rate = librosa.load(wav_path, sr=None, mono=True)

    # Get noise sample (first 0.5 seconds)
    noise_sample = data[:int(rate * 0.5)]

    # Reduce noise
    reduced_noise = nr.reduce_noise(y=data, y_noise=noise_sample, sr=rate)

    # Save to temp cleaned WAV
    temp_wav = output_path.rsplit('.', 1)[0] + '_cleaned.wav'
    sf.write(temp_wav, reduced_noise, rate)

    # Convert cleaned WAV to final MP3 output
    cleaned_audio = AudioSegment.from_wav(temp_wav)
    cleaned_audio.export(output_path, format="mp3")

    # Clean up temp files
    os.remove(wav_path)
    os.remove(temp_wav)