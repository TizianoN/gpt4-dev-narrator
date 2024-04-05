import cv2
import base64
from openai import OpenAI
import os
import requests
import base64
import pygame
import time

api_key = os.environ.get("OPENAI_API_KEY")
fps = 20
file_audio_path = "output.m4a"
client = OpenAI(
  api_key=api_key
)

# Funzione principale
def main():
  try:
    narrate()
  except KeyboardInterrupt:
    print("Cattura dell'immagine dalla webcam interrotta.")

# Funzione che narra quel che accade nella webcam dell'utente
def narrate():
  try:    
    while True:
      # Inizializzo la webcam
      video_stream = init_video_stream()
      
      # Recupero l'immagine dalla webcam 
      webcam_frame_base64_jpeg = get_base64_image_from_webcam(video_stream)
      
      # Invia l'immagine in base64 all'endpoint
      textual_content = send_image_to_gpt4(webcam_frame_base64_jpeg)
      
      # Trasforma il contenuto in audio 
      text_to_speech(textual_content)
      
      reproduce_audio()
      
      # Interrompe il loop se l'utente preme 'q'
      if cv2.waitKey(int (1000 / fps)) & 0xFF == ord('q'):
        # Rilascio la webcam
        video_stream.release()
        
        break
        
  finally:
    # Rilascia le risorse e chiude la finestra
    video_stream.release()
    cv2.destroyAllWindows()

# Funzione che inizializza lo streaming della webcam
def init_video_stream():
  # Inizializza l'accesso alla webcam
  cap = cv2.VideoCapture(0)

  # Verifica se la webcam è stata inizializzata correttamente
  if not cap.isOpened():
      raise IOError("Impossibile accedere alla webcam")
    
  return cap

# Funzione per leggere un frame dalla webcam
def get_base64_image_from_webcam(video_stream):
  
  # Cattura un frame dalla webcam
  ret, frame = video_stream.read()

  # Mostra il frame catturato (opzionale)
  cv2.imshow('Webcam', frame)
    
  # Verifica se il frame è stato catturato correttamente
  if ret:
      # Converte il frame in formato JPEG
      _, buffer = cv2.imencode('.jpg', frame)
      
      # Converte il buffer JPEG in una stringa base64
      base64_jpg = base64.b64encode(buffer).decode()
      
      # Stampa una porzione della stringa per conferma
      # print("Stringa base64 dell'immagine:", base64_jpg[:50], "...") 
  else:
      print("Errore nella cattura dell'immagine dalla webcam")
      
  return base64_jpg

# Funzione per convertire un'immagine in formato base64
# def image_to_base64(image):
#   return base64.b64encode(image).decode('utf-8')
  

# Funzione per inviare l'immagine in base64 a GPT4
def send_image_to_gpt4(base64_image):
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Descrivi quello che vedi"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 100
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
  content = response['choices'][0]['message']['content']

  print(content)
  
  return content

def text_to_speech(text):
  with client.audio.speech.with_streaming_response.create(
      model="tts-1",
      voice="onyx",
      input=text,
  ) as response:
    response.stream_to_file(file_audio_path)
  
  return "ok"

def reproduce_audio():
  # Inizializzazione di Pygame
  pygame.mixer.init()
  pygame.mixer.music.load(file_audio_path)
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy():
      # Tieni in esecuzione il programma finché la musica è in riproduzione
      time.sleep(1)

  pygame.mixer.music.unload()  # Scarica il file musicale per liberare la risorsa
  pygame.mixer.quit()  # Chiude il mixer
        
# Funzione che lancia lo script
if __name__ == "__main__":
  main()