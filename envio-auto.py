import os
import paramiko
import tkinter as tk
from tkinter import ttk
import threading
import shutil
import time

# Declare sftp como uma variável global para que possa ser acessada em várias funções.
sftp = None

def atualizar_progresso(nome_arquivo, transferido, total):
    progresso = transferido / total * 100
    barra_progresso["value"] = progresso
    rotulo_status.config(text="Transferindo: {} | {:.2f}%".format(nome_arquivo, progresso))

def ler_arquivos_enviados():
    try:
        with open("contagem.txt", "r") as arquivo_contagem:
            arquivos_enviados = arquivo_contagem.read().splitlines()
        return arquivos_enviados
    except FileNotFoundError:
        return []

def listar_arquivos_remotos(diretorio_remoto):
    try:
        arquivos_remotos = sftp.listdir(diretorio_remoto)
        return arquivos_remotos
    except Exception as e:
        rotulo_status.config(text="Erro ao listar arquivos remotos: " + str(e))
        return []

def criar_diretorio(diretorio_remoto):
    if not diretorio_remoto:
        rotulo_status.config(text="O diretório remoto não pode estar em branco.")
        return

    global sftp  # Use a variável global sftp

    try:
        # Verifique se a conexão SFTP está estabelecida
        if sftp is not None:
            sftp.mkdir(diretorio_remoto)
            rotulo_status.config(text="Diretório remoto criado com sucesso: " + diretorio_remoto)
        else:
            rotulo_status.config(text="Erro: Conexão SFTP não está estabelecida.")
    except Exception as e:
        rotulo_status.config(text="Erro ao criar diretório remoto: " + str(e))

def conectar_sftp():
    global sftp  # Use a variável global sftp

    try:
        host = "212.102.60.69"
        porta = 22
        usuario = "root"
        senha = "alexandre2022"

        transporte = paramiko.Transport((host, porta))
        transporte.connect(username=usuario, password=senha)
        sftp = paramiko.SFTPClient.from_transport(transporte)

        rotulo_status.config(text="Conexão SFTP estabelecida.")
    except Exception as e:
        rotulo_status.config(text="Erro ao conectar ao SFTP: " + str(e))

def atualizar_mensagem(texto):
    texto_mensagem.config(state="normal")
    texto_mensagem.insert("end", texto + "\n")
    texto_mensagem.config(state="disabled")
    texto_mensagem.see("end")

def transferencia_sftp(diretorio_remoto):
    global sftp  # Use a variável global sftp

    try:
        host = "212.102.60.69"
        porta = 22
        usuario = "root"
        senha = "alexandre2022"

        transporte = paramiko.Transport((host, porta))
        transporte.connect(username=usuario, password=senha)
        sftp = paramiko.SFTPClient.from_transport(transporte)

        arquivos_enviados = ler_arquivos_enviados()

        while not flag_parar_transferencia:
            arquivos_locais = []

            for nome_arquivo in os.listdir(diretorio_origem):
                if os.path.isfile(os.path.join(diretorio_origem, nome_arquivo)) and nome_arquivo not in arquivos_enviados:
                    arquivos_locais.append(nome_arquivo)

            if arquivos_locais and diretorio_remoto:
                for nome_arquivo in arquivos_locais:
                    arquivo_remoto = os.path.join(diretorio_remoto, nome_arquivo)
                    tamanho_local = os.path.getsize(os.path.join(diretorio_origem, nome_arquivo))

                    arquivos_remotos = listar_arquivos_remotos(diretorio_remoto)

                    if nome_arquivo in arquivos_remotos:
                        mensagem_erro = "Arquivo '{}' já existe no servidor remoto.".format(nome_arquivo)
                        atualizar_mensagem(mensagem_erro)
                        print(mensagem_erro)
                    else:
                        sftp.put(os.path.join(diretorio_origem, nome_arquivo), arquivo_remoto, callback=lambda x, y: atualizar_progresso(nome_arquivo, x, y))

                        arquivos_enviados.append(nome_arquivo)

                        with open("F:/concluidos/contagem.txt", "w") as arquivo_contagem:
                            arquivo_contagem.write("\n".join(arquivos_enviados))

                        mensagem_sucesso = "Arquivo '{}' transferido com sucesso.".format(nome_arquivo)
                        atualizar_mensagem(mensagem_sucesso)
                        print(mensagem_sucesso)

                rotulo_status.config(text="Transferência concluída.")
            else:
                time.sleep(2)

        sftp.close()
        transporte.close()
    except Exception as e:
        mensagem_erro = "Ocorreu um erro: " + str(e)
        atualizar_mensagem(mensagem_erro)
        print(mensagem_erro)

def iniciar_thread_transferencia():
    global thread_transferencia
    global flag_parar_transferencia

    if not thread_transferencia or not thread_transferencia.is_alive():
        flag_parar_transferencia = False
        diretorio_remoto = entrada_diretorio_remoto.get()  # Obtém o diretório remoto da entrada do usuário
        thread_transferencia = threading.Thread(target=transferencia_sftp, args=(diretorio_remoto,))
        thread_transferencia.start()
    else:
        rotulo_status.config(text="Transferência já em andamento.")

def limpar_arquivos():
    diretorio_origem = "F:/concluidos/concluidostrans/"
    diretorio_destino = "F:/concluidos/lixeira/"

    try:
        for nome_arquivo in os.listdir(diretorio_origem):
            caminho_origem = os.path.join(diretorio_origem, nome_arquivo)
            caminho_destino = os.path.join(diretorio_destino, nome_arquivo)
            shutil.move(caminho_origem, caminho_destino)

        rotulo_status.config(text="Arquivos movidos para lixeira/")
    except Exception as e:
        rotulo_status.config(text="Ocorreu um erro: " + str(e))

janela_principal = tk.Tk()
janela_principal.title("Transferência de Arquivos via SFTP")

frame_entrada = tk.Frame(janela_principal)
frame_entrada.pack(side="top", anchor="w")

rotulo_entrada = tk.Label(frame_entrada, text="Diretório Remoto:")
rotulo_entrada.pack(side="left")

entrada_diretorio_remoto = tk.Entry(frame_entrada)
entrada_diretorio_remoto.pack(side="left")

botao_criar_diretorio = tk.Button(frame_entrada, text="Criar Diretório Remoto", command=lambda: criar_diretorio(entrada_diretorio_remoto.get()))
botao_criar_diretorio.pack(side="left")

frame_botoes = tk.Frame(janela_principal)
frame_botoes.pack(side="top", anchor="w")

botao_conectar_sftp = tk.Button(frame_botoes, text="Conectar ao SFTP", command=conectar_sftp)
botao_conectar_sftp.pack(side="left")

botao_iniciar = tk.Button(frame_botoes, text="Iniciar", command=iniciar_thread_transferencia)
botao_iniciar.pack(side="left")

botao_limpar = tk.Button(frame_botoes, text="Limpar", command=limpar_arquivos)
botao_limpar.pack(side="left")

rotulo_status = tk.Label(janela_principal, text="", pady=10)
rotulo_status.pack()

barra_progresso = ttk.Progressbar(janela_principal, orient="horizontal", length=300, mode="determinate")
barra_progresso.pack()

texto_mensagem = tk.Text(janela_principal, height=3, width=50, state="disabled")
texto_mensagem.pack()

arquivos_enviados = ler_arquivos_enviados()

diretorio_origem = "F:/concluidos/concluidostrans/"

flag_parar_transferencia = False

thread_transferencia = None

janela_principal.mainloop()
