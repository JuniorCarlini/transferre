<div align="center">

# 📥 Transferre

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

**3.** O script interativo irá solicitar:
- A **URL do vídeo** no YouTube.
- A **qualidade desejada** para o download.

Aguarde o processamento e aproveite o seu vídeo offline! 🎉

---
<div align="center">
<i>Transformando downloads em uma tarefa simples via terminal.</i>
</div>
