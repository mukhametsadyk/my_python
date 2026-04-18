import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.music_folder = music_folder
        
        self.tracks = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
        self.current_index = 0
        self.is_playing = False

    def play(self):
        if not self.tracks:
            print("Музыка папкасы бос!")
            return

        try:
            track_path = os.path.join(self.music_folder, self.tracks[self.current_index])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            print(f"Ойнап тұр: {self.tracks[self.current_index]}")
        except pygame.error as e:
            print(f"Қате: {self.tracks[self.current_index]} файлын ойнату мүмкін емес!")
            
            if len(self.tracks) > 1:
                self.next_track()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        print("Тоқтатылды")

    def next_track(self):
        if self.tracks:
            self.current_index = (self.current_index + 1) % len(self.tracks)
            self.play()

    def prev_track(self):
        if self.tracks:
            self.current_index = (self.current_index - 1) % len(self.tracks)
            self.play()

    def get_current_track_name(self):
        if self.tracks:
            return self.tracks[self.current_index]
        return "Музыка табылмады"