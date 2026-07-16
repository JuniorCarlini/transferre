<div align="center">

<img src="assets/logo.png" alt="Transferre — YouTube Downloader" width="420">

<br>

**Um script simples e poderoso para baixar vídeos do YouTube via linha de comando.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-cli-red?style=for-the-badge&logo=youtube)](https://github.com/yt-dlp/yt-dlp)

</div>

---

## 📌 Sobre o Projeto

Este é um script prático em Python que utiliza o **yt-dlp** para fazer o download de vídeos do YouTube de forma rápida e direta pelo terminal. Ele facilita o processo de extração da melhor qualidade de vídeo e áudio e cuida da mesclagem (muxing) de forma automatizada.

## 🚀 Requisitos

Antes de rodar o script, você precisará instalar algumas dependências. Certifique-se de ter os seguintes itens configurados em seu ambiente:

| Ferramenta | Como Instalar / Link | Descrição |
| :--- | :--- | :--- |
| **Python 3** | [Download Oficial](https://www.python.org/downloads/) | Linguagem base necessária para rodar o script. |
| **yt-dlp** | `pip install yt-dlp` ou `brew install yt-dlp` | Software responsável por baixar o vídeo. |
| **Node.js** | `brew install node` | Runtime JS (muitas vezes necessário pelo yt-dlp para extrair assinaturas). |
| **FFmpeg** | `brew install ffmpeg` | Necessário para mesclar as faixas de vídeo e áudio (muxing) em alta qualidade. |

> 💡 **Dica (macOS / Linux via Homebrew):**
> Você pode instalar os utilitários de sistema em um único comando:
> ```bash
> brew install yt-dlp node ffmpeg
> ```

## 🍪 Exportar Cookies do YouTube (Necessário)

O YouTube requer autenticação para downloads. Exporte os cookies **uma única vez**:

1. Instale a extensão **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)** no Chrome/Edge/Brave
2. Acesse **youtube.com** e faça login na sua conta
3. Clique na extensão e clique em **"Export"**
4. Salve o arquivo como `cookies.txt` na mesma pasta do script

> ⚠️ O script detecta automaticamente o arquivo `cookies.txt` se ele existir.

## 🛠️ Como Usar

**1.** Abra o terminal na pasta onde o script está localizado.

**2.** Execute o script passando o comando abaixo:

```bash
python3 baixar_youtube.py
```

**3.** Cole a **URL do vídeo** quando solicitado. O script lista os formatos disponíveis:

```
Título: Nome do vídeo
Duração: 10:32
Canal: Meu Canal
============================================================

Opções de download:

#   Resolução    Formato Tamanho      Tipo
------------------------------------------------------------
1   1920x1080    mp4     142.3 MB     Vídeo
2   1280x720     mp4     78.1 MB      Vídeo + Áudio
3   640x360      mp4     31.7 MB      Vídeo + Áudio
```

**4.** Escolha uma opção:

| Opção | O que faz |
| :--- | :--- |
| `1`, `2`, `3`… | Baixa o formato correspondente da lista (mescla o áudio automaticamente se o formato for só vídeo). |
| `a` | Baixa **apenas o áudio** em MP3, na melhor qualidade. |
| `b` | Baixa na **melhor qualidade** disponível (`bestvideo+bestaudio`). |
| `q` | Sai do script. |

**5.** Escolha a pasta de destino — ou pressione **Enter** para usar a pasta padrão `downloads/`.

Aguarde o processamento e aproveite o seu vídeo offline! 🎉

---
<div align="center">
<i>Transformando downloads em uma tarefa simples via terminal.</i>
</div>
