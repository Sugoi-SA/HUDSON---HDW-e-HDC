import argparse
import json
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import STORAGE_ROOT


def read_status(ronda_id):
    safe_id = "".join(
        c if c.isalnum() or c in "_.-" else "_" for c in ronda_id
    )
    if safe_id in ("", ".", ".."):
        raise ValueError("Identificador de rodada inválido")

    path = os.path.join(STORAGE_ROOT, "import_status", safe_id + ".json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)



def format_local_time(value):
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo("America/Sao_Paulo")).isoformat(
            timespec="seconds"
        )
    except (ValueError, TypeError):
        return str(value)



def show_status(status):
    total = int(status.get("source_total", 0) or 0)
    done = int(status.get("source_completed", 0) or 0)
    percent = min(100.0, 100.0 * done / total) if total else 0.0

    width = 32
    filled = int(width * percent / 100)
    bar = "#" * filled + "-" * (width - filled)

    def number(key):
        return f"{int(status.get(key, 0) or 0):,}"

    print("=" * 72)
    print("HUDSON IMPORT  |  PROGRESSO DA RONDA")
    print("=" * 72)
    print(f"Ronda:       {status.get('ronda_id', '-')}")
    print(f"Estado:      {str(status.get('state', '-')).upper()}")
    print(f"Início:      {format_local_time(status.get('started_at'))}")
    print(f"Atualização: {format_local_time(status.get('updated_at'))}")
    print(f"Término:     {format_local_time(status.get('finished_at'))}")
    print("-" * 72)
    print(f"Progresso    [{bar}] {percent:6.2f}%")
    print(f"Arquivos     {done:,} / {total:,}")
    print(f"Unidades     {number('units_processed')}")
    print("-" * 72)
    print("RESUMO")
    print(f"  Novos itens:       {number('novos')}")
    print(f"  Indexados:         {number('indexados')}")
    print(f"  Duplicados:        {number('duplicados')}")
    print(f"  Sem texto:         {number('sem_texto')}")
    print(f"  Sem estante:       {number('sem_estante')}")
    print(f"  Desbloqueados:     {number('desbloqueados')}")
    print(f"  Erros:             {number('errors_count')}")
    print("-" * 72)
    print(f"Origem: {status.get('source', '-')}")
    print(f"WBS:    {status.get('wbs', '-')}")
    print(f"Atual:  {status.get('current_path') or '-'}")

    if status.get("failure"):
        print(f"FALHA:  {status['failure']}")

    errors = status.get("recent_errors", [])
    if errors:
        print("-" * 72)
        print("ERROS RECENTES")
        for error in errors[-5:]:
            print(f"  - {error}")

    print("=" * 72)
    print("Acompanhamento contínuo: Ctrl+C para sair do painel.")

def main():
    parser = argparse.ArgumentParser(
        description="Consulta o progresso persistente de uma importação HUDSON"
    )
    parser.add_argument("--ronda", required=True, help="Identificador da rodada")
    parser.add_argument(
        "--watch", action="store_true", help="Atualiza a tela continuamente"
    )
    parser.add_argument(
        "--interval", type=int, default=5,
        help="Intervalo de atualização em segundos (padrão: 5)"
    )
    args = parser.parse_args()

    if args.interval < 1:
        parser.error("--interval deve ser pelo menos 1 segundo")

    while True:
        try:
            status = read_status(args.ronda)
            if args.watch:
                os.system("clear")
            show_status(status)
        except FileNotFoundError:
            print("Ainda não existe estado salvo para a rodada:", args.ronda)
            print("Confira o identificador e se a importação já foi iniciada.")
            if not args.watch:
                raise SystemExit(1)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print("Não foi possível consultar o progresso:", exc)
            raise SystemExit(1)

        if not args.watch:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
