#!/usr/bin/env python3
"""
Download de vídeos do YouTube (interativo).

Usa yt-dlp para baixar vídeos em diferentes qualidades.
"""

import subprocess
import sys
import json
from pathlib import Path


def verificar_yt_dlp():
    """Verifica se yt-dlp está instalado."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Erro: yt-dlp não está instalado.")
        print("Instale com: pip install yt-dlp")
        print("Ou no macOS: brew install yt-dlp")
        sys.exit(1)


def obter_formatos(url: str) -> dict:
    """Obtém informações e formatos disponíveis do vídeo."""
    cmd = ["yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github", "--dump-json", "--no-playlist", url]
    resultado = subprocess.run(cmd, capture_output=True, text=True)

    if resultado.returncode != 0:
        print(f"Erro ao obter informações: {resultado.stderr}")
        sys.exit(1)

    return json.loads(resultado.stdout)


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
    print(f"{'#':<3} {'Resolução':<12} {'Formato':<6} {'Tamanho':<12} {'Tipo'}")
    print("-" * 60)

    for i, op in enumerate(formatos[:20], 1):
        tipo = "Vídeo + Áudio" if op["tem_video"] and op["tem_audio"] else \
               "Vídeo" if op["tem_video"] else "Áudio"
        fps_str = f" ({op['fps']})" if op['fps'] else ""
        print(f"{i:<3} {op['resolution'] + fps_str:<12} {op['ext']:<6} {op['tamanho']:<12} {tipo}")

    print("-" * 60)


def baixar(url: str, format_id: str, saida: str = ".") -> None:
    """Baixa o vídeo na qualidade selecionada."""
    diretorio = str(Path(saida).resolve())

    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",
        "--remote-components", "ejs:github",
        "--progress",
        "--no-playlist",
        "-f", format_id,
        "--merge-output-format", "mp4",
        "-o", f"{diretorio}/%(title)s.%(ext)s",
        url
    ]

    print(f"\nIniciando download...\n")
    subprocess.run(cmd)


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
    print("b  - Melhor qualidade disponível")
    print("q  - Sair")

    escolha = input("\nEscolha uma opção (número ou letra): ").strip().lower()

    if escolha == "q":
        print("Saindo...")
        sys.exit(0)

    diretorio = input("Diretório para salvar (Enter = atual): ").strip() or "."

    if escolha == "a":
        print("\nBaixando áudio em MP3...")
        cmd = [
            "yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github",
            "--progress", "--no-playlist",
            "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "-o", f"{diretorio}/%(title)s.%(ext)s", url
        ]
        subprocess.run(cmd)
    elif escolha == "b":
        print("\nBaixando na melhor qualidade...")
        cmd = [
            "yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github",
            "--progress", "--no-playlist",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "-o", f"{diretorio}/%(title)s.%(ext)s", url
        ]
        subprocess.run(cmd)
    else:
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(formatos):
                formato = formatos[idx]

                if formato["tem_video"] and not formato["tem_audio"]:
                    print("\nEste formato tem apenas vídeo. Baixando com áudio separado e mesclando...")
                    cmd = [
                        "yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github",
                        "--progress", "--no-playlist",
                        "-f", f"{formato['id']}+bestaudio/best",
                        "--merge-output-format", "mp4",
                        "-o", f"{diretorio}/%(title)s.%(ext)s", url
                    ]
                    subprocess.run(cmd)
                else:
                    baixar(url, formato["id"], diretorio)
            else:
                print("Opção inválida.")
        except ValueError:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
