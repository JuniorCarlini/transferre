#!/usr/bin/env python3
"""
Download de vídeos do YouTube (interativo).

Usa yt-dlp para baixar vídeos em diferentes qualidades.
"""

import subprocess
import sys
import json
import shutil
from pathlib import Path

COOKIES_FILE = Path(__file__).parent / "cookies.txt"
DOWNLOADS_DIR = Path(__file__).parent / "downloads"

# Navegador de onde puxar cookies quando não existe cookies.txt. Sem cookie
# algum o YouTube devolve URLs que morrem em "HTTP Error 403" no meio do
# download, deixando só um .part que nenhum player abre.
#
# Ler os cookies do navegador exige a chave do Keychain ("Chrome Safe Storage"),
# então o macOS pede autorização a cada execução — clique "Sempre Permitir" para
# ele parar de perguntar. Se preferir não usar o Keychain, ponha None aqui e
# exporte seus cookies para cookies.txt (veja o README).
NAVEGADOR_COOKIES = "chrome"

# QuickTime, Fotos, iMovie e iPhone só abrem H.264 (avc1) com áudio AAC (mp4a).
# O "melhor" do YouTube hoje é AV1 ou VP9 com áudio Opus: baixa até o fim,
# gera um .mp4 válido, e mesmo assim não abre no Mac. Por isso a qualidade
# padrão é a melhor *compatível*, não a melhor absoluta.
FORMATO_COMPATIVEL = (
    "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
    "best[vcodec^=avc1][acodec^=mp4a]/"
    "best[ext=mp4]/best"
)
AUDIO_PARA_MP4 = "bestaudio[acodec^=mp4a]/bestaudio[ext=m4a]/bestaudio"


def codec_compativel(vcodec: str) -> bool:
    """Diz se o codec de vídeo abre nativamente no macOS/iOS."""
    return vcodec.startswith("avc1") or vcodec.startswith("h264")


def verificar_yt_dlp():
    """Verifica se yt-dlp está instalado."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Erro: yt-dlp não está instalado.")
        print("Instale com: pip install yt-dlp")
        print("Ou no macOS: brew install yt-dlp")
        sys.exit(1)

    if not shutil.which("ffmpeg"):
        print("Erro: ffmpeg não encontrado.")
        print("Sem ele o yt-dlp não junta vídeo + áudio nem converte para MP3;")
        print("o resultado fica pela metade e não abre em player nenhum.")
        print("Instale com: brew install ffmpeg")
        sys.exit(1)

    if not shutil.which("node"):
        print("Aviso: Node.js não encontrado.")
        print("O YouTube exige um runtime JS para liberar os vídeos; o yt-dlp vai")
        print("tentar outro que esteja instalado. Se o download falhar, instale-o:")
        print("  brew install node\n")


def opcoes_cookies() -> list:
    """Escolhe a fonte de cookies: o arquivo local, senão o navegador."""
    if COOKIES_FILE.exists():
        return ["--cookies", str(COOKIES_FILE)]
    if NAVEGADOR_COOKIES:
        return ["--cookies-from-browser", NAVEGADOR_COOKIES]
    return []


def montar_cmd(url: str, *opcoes: str) -> list:
    """Monta um comando yt-dlp com as flags comuns a todos os downloads."""
    cmd = ["yt-dlp", "--remote-components", "ejs:github", "--no-playlist"]

    # Só força o node se ele existir; caso contrário deixa o yt-dlp escolher
    # sozinho o runtime JS disponível, em vez de falhar.
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])

    cmd.extend(opcoes_cookies())
    cmd.extend(opcoes)
    cmd.append(url)
    return cmd


def baixar_mp4(url: str, seletor: str, diretorio: str) -> None:
    """Baixa um seletor de formato e entrega um .mp4 já mesclado."""
    executar_download(montar_cmd(
        url,
        "--progress",
        "-f", seletor,
        "--merge-output-format", "mp4",
        "-o", f"{diretorio}/%(title)s.%(ext)s",
    ))


def mostrar_dicas_erro() -> None:
    """Mostra as causas mais comuns de falha, conforme o ambiente atual."""
    print("\nPossíveis causas:")

    if not shutil.which("node"):
        print("  - Node.js não está instalado: brew install node")
    if not COOKIES_FILE.exists():
        print("  - 'HTTP Error 403' ou 'Sign in to confirm you're not a bot': o")
        print("    YouTube recusou a sessão. Este script tenta os cookies do")
        print(f"    {NAVEGADOR_COOKIES}; se você não está logado no YouTube nele,")
        print("    exporte os cookies para cookies.txt (veja o README).")

    print("  - yt-dlp desatualizado: pip install -U yt-dlp")
    print("  - Cache antigo do solver de JS: yt-dlp --rm-cache-dir")

    avisar_parciais()


def avisar_parciais() -> None:
    """Avisa sobre sobras .part: parecem vídeo, mas não abrem em player nenhum."""
    parciais = list(DOWNLOADS_DIR.glob("*.part")) if DOWNLOADS_DIR.exists() else []
    if not parciais:
        return

    print(f"\n{len(parciais)} download(s) pela metade em {DOWNLOADS_DIR}:")
    for p in parciais:
        print(f"  - {p.name}")
    print("São arquivos incompletos, não vídeos; apague-os antes de tentar de novo.")


def obter_formatos(url: str) -> dict:
    """Obtém informações e formatos disponíveis do vídeo."""
    cmd = montar_cmd(url, "--dump-json")
    resultado = subprocess.run(cmd, capture_output=True, text=True)

    if resultado.returncode != 0:
        print(f"\nErro ao obter informações do vídeo:\n{resultado.stderr.strip()}")
        mostrar_dicas_erro()
        sys.exit(1)

    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError:
        print("\nErro: o yt-dlp não retornou dados válidos sobre o vídeo.")
        if resultado.stderr.strip():
            print(resultado.stderr.strip())
        mostrar_dicas_erro()
        sys.exit(1)


def executar_download(cmd: list) -> None:
    """Executa o download e informa o resultado."""
    resultado = subprocess.run(cmd)

    if resultado.returncode != 0:
        print("\n" + "=" * 60)
        print("O download falhou. Veja a mensagem do yt-dlp acima.")
        mostrar_dicas_erro()
        sys.exit(1)

    print("\nDownload concluído!")


def filtrar_formatos(formatos: list) -> list:
    """Filtra e organiza formatos de vídeo/áudio disponíveis."""
    opcoes = []

    for f in formatos:
        format_id = f.get("format_id", "")
        ext = f.get("ext", "")
        resolution = f.get("resolution", "")
        fps = f.get("fps", "")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        filesize = f.get("filesize") or f.get("filesize_approx", 0)

        tem_video = vcodec != "none"
        tem_audio = acodec != "none"

        if not tem_video and not tem_audio:
            continue

        if filesize:
            tamanho = filesize / (1024 * 1024)
            tamanho_str = f"{tamanho:.1f} MB"
        else:
            tamanho_str = "N/A"

        opcoes.append({
            "id": format_id,
            "ext": ext,
            "resolution": resolution,
            "fps": f"{fps} fps" if fps else "",
            "tem_video": tem_video,
            "tem_audio": tem_audio,
            "tamanho": tamanho_str,
            "vcodec": vcodec,
        })

    opcoes.sort(key=lambda x: (
        not x["tem_video"],
        -int(x["resolution"].split("x")[1]) if "x" in x["resolution"] else 0
    ))

    return opcoes


def mostrar_opcoes(info: dict, formatos: list) -> None:
    """Mostra informações do vídeo e opções de download."""
    print("\n" + "=" * 60)
    print(f"Título: {info.get('title', 'N/A')}")
    print(f"Duração: {info.get('duration_string', 'N/A')}")
    print(f"Canal: {info.get('channel', 'N/A')}")
    print("=" * 60)

    print("\nOpções de download:\n")
    print(f"{'#':<3} {'Resolução':<18} {'Formato':<6} {'Tamanho':<11} {'Tipo':<14} {'Abre no Mac'}")
    print("-" * 78)

    for i, op in enumerate(formatos[:20], 1):
        tipo = "Vídeo + Áudio" if op["tem_video"] and op["tem_audio"] else \
               "Vídeo" if op["tem_video"] else "Áudio"
        fps_str = f" ({op['fps']})" if op['fps'] else ""
        if not op["tem_video"]:
            compat = "sim"
        else:
            compat = "sim" if codec_compativel(op["vcodec"]) else f"não ({op['vcodec'].split('.')[0]})"
        print(f"{i:<3} {op['resolution'] + fps_str:<18} {op['ext']:<6} "
              f"{op['tamanho']:<11} {tipo:<14} {compat}")

    print("-" * 78)
    print("'Abre no Mac' = QuickTime/Fotos/iPhone tocam sem instalar codec extra.")


def baixar(url: str, format_id: str, saida: str = str(DOWNLOADS_DIR)) -> None:
    """Baixa o vídeo na qualidade selecionada."""
    diretorio = str(Path(saida).resolve())
    Path(diretorio).mkdir(parents=True, exist_ok=True)

    print(f"\nIniciando download...\n")
    baixar_mp4(url, format_id, diretorio)


def main():
    verificar_yt_dlp()

    print("\n=== Download de Vídeos do YouTube ===\n")
    url = input("Cole a URL do vídeo: ").strip()

    if not url:
        print("URL inválida.")
        sys.exit(1)

    print("\nObtendo informações do vídeo...")
    info = obter_formatos(url)
    formatos = filtrar_formatos(info.get("formats", []))

    if not formatos:
        print("Nenhum formato disponível.")
        sys.exit(1)

    mostrar_opcoes(info, formatos)

    print("\nOpções especiais:")
    print("a  - Baixar apenas áudio (MP3)")
    print("b  - Melhor qualidade que abre no Mac (H.264 + AAC) [recomendado]")
    print("x  - Melhor qualidade absoluta (AV1/VP9 — pode não abrir no QuickTime)")
    print("q  - Sair")

    escolha = input("\nEscolha uma opção (número ou letra): ").strip().lower()

    if escolha == "q":
        print("Saindo...")
        sys.exit(0)

    diretorio = input(f"Diretório para salvar (Enter = {DOWNLOADS_DIR}): ").strip() or str(DOWNLOADS_DIR)
    Path(diretorio).mkdir(parents=True, exist_ok=True)

    if escolha == "a":
        print("\nBaixando áudio em MP3...")
        executar_download(montar_cmd(
            url,
            "--progress",
            "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "-o", f"{diretorio}/%(title)s.%(ext)s",
        ))
    elif escolha == "b":
        print("\nBaixando na melhor qualidade compatível com QuickTime...")
        baixar_mp4(url, FORMATO_COMPATIVEL, diretorio)
    elif escolha == "x":
        print("\nBaixando na melhor qualidade absoluta...")
        print("Atenção: se vier AV1/VP9 ou áudio Opus, o QuickTime não abre o")
        print("arquivo mesmo ele estando íntegro. Use VLC, ou escolha 'b'.")
        baixar_mp4(url, f"bestvideo+{AUDIO_PARA_MP4}/best", diretorio)
    else:
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(formatos):
                formato = formatos[idx]

                if formato["tem_video"] and not codec_compativel(formato["vcodec"]):
                    print(f"\nAtenção: este formato é {formato['vcodec'].split('.')[0]}.")
                    print("O arquivo vai baixar inteiro, mas o QuickTime/Fotos não abre.")
                    print("Use VLC para assistir, ou cancele e escolha 'b'.")

                if formato["tem_video"] and not formato["tem_audio"]:
                    # Áudio precisa ser AAC: Opus dentro de .mp4 gera um arquivo
                    # que o QuickTime abre mudo ou recusa de vez.
                    print("\nEste formato tem apenas vídeo. Baixando com áudio separado e mesclando...")
                    baixar_mp4(url, f"{formato['id']}+{AUDIO_PARA_MP4}", diretorio)
                else:
                    baixar(url, formato["id"], diretorio)
            else:
                print("Opção inválida.")
        except ValueError:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
