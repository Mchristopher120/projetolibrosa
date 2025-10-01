import yt_dlp
import librosa
import soundfile as sf
import os
import tkinter as tk
from tkinter import messagebox
import threading

def download_audio_from_youtube(youtube_url, output_path="audio_original.wav"):
    """
    Baixa o áudio de um vídeo do YouTube e o salva como um arquivo WAV.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.splitext(output_path)[0],
        'quiet': True,
        'cachedir': False
    }
    print(f"\nBaixando áudio de: {youtube_url}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(youtube_url, download=True)
            print(f"Áudio baixado como: {output_path}")
            return output_path
    except Exception as e:
        print(f"ERRO: Falha ao baixar o áudio. Verifique o link e a sua conexão.")
        print(f"Detalhe do erro: {e}")
        return None

def separate_harmony_percussion(audio_path):
    """
    Carrega o áudio e separa a parte harmônica da percussiva.
    """
    print(f"Carregando e processando o áudio: {audio_path}...")
    try:
        y, sr = librosa.load(audio_path, sr=None) # sr=None mantém a taxa de amostragem original
        print("Realizando a separação... Isso pode levar alguns minutos para músicas longas.")
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        print("Separação concluída.")
        return y_harmonic, y_percussive, sr
    except Exception as e:
        print(f"ERRO: Falha ao processar o áudio com o Librosa.")
        print(f"Detalhe do erro: {e}")
        return None, None, None

def save_audio(audio_data, sr, filename, output_dir="resultado_separacao"):
    """
    Salva os dados de áudio em um arquivo WAV dentro de um diretório específico.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    print(f"Salvando arquivo em: {filepath}")
    try:
        sf.write(filepath, audio_data, sr)
        print(f"Arquivo salvo com sucesso!")
        return filepath
    except Exception as e:
        print(f"ERRO: Falha ao salvar o arquivo de áudio.")
        print(f"Detalhe do erro: {e}")
        return None
    
# --- LÓGICA DA INTERFACE ---

def processo_principal():
    """Pega a URL e executa todo o processo de download e separação."""
    
    # Pega o link do campo de texto
    youtube_link = campo_url.get()
    if not youtube_link:
        messagebox.showerror("Erro", "Por favor, insira um link do YouTube.")
        return

    # Bloqueia o botão para evitar múltiplos cliques
    botao_iniciar.config(state="disabled")
    
    original_audio_file = "audio_original.wav"
    output_harmonic_file = "harmonia.wav"
    output_percussive_file = "percussao.wav"

    try:
        # Atualiza o status na tela
        label_status.config(text="Baixando áudio... Por favor, aguarde.")
        janela.update_idletasks() # Força a atualização da tela
        
        audio_file_path = download_audio_from_youtube(youtube_link, original_audio_file)

        if audio_file_path and os.path.exists(audio_file_path):
            label_status.config(text="Processando o áudio... Isso pode demorar vários minutos.")
            janela.update_idletasks()
            
            y_harmonic, y_percussive, sr = separate_harmony_percussion(audio_file_path)

            if y_harmonic is not None and y_percussive is not None:
                label_status.config(text="Salvando arquivos separados...")
                janela.update_idletasks()

                save_audio(y_harmonic, sr, output_harmonic_file)
                save_audio(y_percussive, sr, output_percussive_file)

                messagebox.showinfo("Sucesso", "Processo concluído! Os arquivos foram salvos na pasta 'resultado_separacao'.")
            
            try:
                os.remove(audio_file_path)
            except OSError:
                pass
        else:
            raise ValueError("Falha no download. O arquivo de áudio não foi encontrado.")

    except Exception as e:
        messagebox.showerror("Erro no Processo", f"Ocorreu um erro:\n{e}")
    finally:
        # Reabilita o botão e reseta o status no final, mesmo se der erro
        botao_iniciar.config(state="normal")
        label_status.config(text="Aguardando link...")


def iniciar_thread():
    """Inicia o processo principal em uma thread separada para não congelar a GUI."""
    thread = threading.Thread(target=processo_principal)
    thread.start()


# 1. Cria a janela principal
janela = tk.Tk()
janela.title("Separador de Áudio do YouTube")
janela.geometry("500x250")

# 2. Cria os componentes (Widgets)
label_instrucao = tk.Label(janela, text="Cole o link do vídeo do YouTube abaixo:")
label_instrucao.pack(pady=10)

campo_url = tk.Entry(janela, width=60)
campo_url.pack(pady=5, padx=10)

botao_iniciar = tk.Button(janela, text="Iniciar Processo", command=iniciar_thread, font=("Helvetica", 12), bg="#4CAF50", fg="white")
botao_iniciar.pack(pady=20)

label_status = tk.Label(janela, text="Aguardando link...", font=("Helvetica", 10))
label_status.pack(pady=10)

# 3. Inicia o loop da aplicação
janela.mainloop()