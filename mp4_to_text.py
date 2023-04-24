import wave
import struct
import sys
from scipy import fromstring, int16
import numpy as np
import os
import math
import speech_recognition as sr
import ffmpeg

# mp4からwavファイルへ変換する
def mp4towav(fileneme):
    mp4_file = fileneme
    wav_file = mp4_file.replace(".mp4", ".wav")

    # wavファイルの存在チェック
    file = os.path.exists(wav_file)
    # wavファイルが存在する場合はスキップ
    if not file:
        stream = ffmpeg.input(mp4_file)
        # 出力
        stream = ffmpeg.output(stream, wav_file)
        # 実行
        ffmpeg.run(stream)
    else:
        print("処理をスキップしました")

    # 変換後のファイル名を返す
    return wav_file

# filenameに読み込むファイル、timeにカットする間隔
def cut_wav(filename, time):
    # timeの単位は[sec]

    # ファイルを読み出し
    wavf = filename
    wr = wave.open(wavf, 'r')

    # waveファイルが持つ性質を取得
    ch = wr.getnchannels()
    width = wr.getsampwidth()
    fr = wr.getframerate()
    fn = wr.getnframes()
    total_time = 1.0 * fn / fr
    integer = math.floor(total_time * 100)  # 小数点以下切り捨て
    t = int(time * 100)  # 秒数[sec]
    frames = int(ch * fr * t / 100)
    num_cut = int(integer // t)
    # waveの実データを取得し、数値化
    data = wr.readframes(wr.getnframes())
    wr.close()
    X = np.frombuffer(data, dtype=int16)

    for i in range(num_cut + 1):
        print(i)
        # 出力データを生成
        outf = wav_dir + '/' + str(i) + '.wav'
        # 音声をカットした部分は少し巻き戻す
        if i > 0:
            start_cut = int(i * frames) - int(180000)
        else:
            start_cut = int(i * frames)

        end_cut = int(i * frames + frames)
        print(start_cut)
        print(end_cut)
        Y = X[start_cut:end_cut]
        outd = struct.pack("h" * len(Y), *Y)

        # 書き出し
        ww = wave.open(outf, 'w')
        ww.setnchannels(ch)
        ww.setsampwidth(width)
        ww.setframerate(fr)
        ww.writeframes(outd)
        ww.close()

        # 音声ファイルをテキストファイルに変換
        wav_to_text(outf)

# 音声ファイル（wav）から文字へ変換
def wav_to_text(wavfile):
    r = sr.Recognizer()

    # 音声ファイルを指定
    with sr.AudioFile(wavfile) as source:
        audio = r.record(source)

    try:
        # 日本語変換
        text = r.recognize_google(audio, language='ja-JP')
        print(text)

        with open(out_file, 'a', encoding='utf-8') as f:
            f.write(text)
    # 以下は認識できなかったときに止まらないように。
    except sr.UnknownValueError:
        print("could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == "__main__":
    # ファイルパスをコマンドライン引数で受け取る
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_mp4_file>")
        sys.exit()

    f_name = sys.argv[1]

    # mp4からwavファイルに変換す
    w_name = mp4towav(f_name)

    # 一応既に同じ名前のディレクトリがないか確認
    iDir = os.path.abspath(os.path.dirname(f_name))
    wav_dir = iDir + "/wav"
    out_dir = iDir + "/output"
    file = os.path.exists(wav_dir)

    if not file:
        # 保存先のディレクトリの作成
        os.mkdir(wav_dir)

    file = os.path.exists(out_dir)
    if not file:
        # 保存先のディレクトリの作成
        os.mkdir(out_dir)

    # wavファイルをcut_time単位に分割する
    cut_time = 30
    out_file = out_dir + '/out.txt'
    cut_wav(w_name, float(cut_time))
