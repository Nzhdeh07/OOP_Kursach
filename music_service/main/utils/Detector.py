import librosa
import numpy as np


class Detector:

    # Создание базы данных аккордов
    note_database = {
        'C': [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50],
        'C#': [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73],
        'D': [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66],
        'D#': [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51],
        'E': [20.60, 41.20, 82.41, 164.81, 329.63, 659.25, 1318.51],
        'F': [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91],
        'F#': [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98],
        'G': [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98],
        'G#': [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22],
        'A': [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00],
        'A#': [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66],
        'B': [30.87, 61.74, 123.47, 246.94, 493.88, 987.77, 1975.53]
    }

    @staticmethod
    def detect_notes(self, file_path):
        y, sr = librosa.load(file_path)

        # Разбиение аудиофайла на сегменты
        segments = librosa.effects.split(y, top_db=20)

        # Определение аккорда в каждом такте
        for segment_start, segment_end in segments:
            segment_start_time = segment_start / sr
            segment_end_time = segment_end / sr
            segment_chords = []

            segment_spectrum = np.abs(librosa.stft(y[segment_start:segment_end], n_fft=2048, hop_length=512))
            segment_frequencies = librosa.fft_frequencies(sr=sr, n_fft=2048)

            # Определение наиболее вероятного аккорда
            max_correlation = 0
            max_chord = ''
            for chord_name, chord_frequencies in self.note_database.items():
                # Создание шаблона для аккорда
                template = np.zeros_like(segment_spectrum)
                for freq in chord_frequencies:
                    idx = np.argmin(np.abs(segment_frequencies - freq))
                    template[idx] = 1

                    # Рассчет коэффициента корреляции
                    correlation = np.sum(segment_spectrum * template) / np.sqrt(np.sum(segment_spectrum ** 2) * np.sum(template ** 2))
                    if correlation > max_correlation:
                        max_correlation = correlation
                        max_chord = chord_name

            segment_chords.append(max_chord)

            print('Нота в сегменте от {:.2f} до {:.2f} секунд: {}'.format(segment_start_time, segment_end_time, ', '.join(segment_chords)))

    @staticmethod
    def get_tempo(file_path):
        y, sr = librosa.load(file_path, mono=True)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return int(tempo)

    @staticmethod
    def get_key(file_path):
        y, sr = librosa.load(file_path)
        chroma_cq = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma = np.mean(chroma_cq, axis=1)

        pitches = np.array([0, 2, 4, 5, 7, 9, 11])
        key = pitches[np.argmax(chroma[pitches])]
        if key >= 5:
            mode = "major"
        else:
            mode = "minor"
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        # key_note = notes[key % 12]
        max_index = np.argmax(chroma)
        key = notes[max_index]
        return key, mode
