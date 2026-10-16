import argparse
import os
import sys

from app.config import STORAGE_ROOT
from app.db import get_session
from app.services.importer import import_source
from app.services.import_progress import ImportProgress


def main():
    parser = argparse.ArgumentParser(
        description="Importa arquivos para o HUDSON com progresso persistente"
    )
    parser.add_argument("--source", required=True, help="Diretorio de origem")
    parser.add_argument("--wbs", default="INDEFINIDO", help="Codigo WBS")
    parser.add_argument("--ronda", default=None, help="Identificador da rodada")
    parser.add_argument("--usuario", default="sistema", help="Usuario responsavel")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        parser.error("O diretorio de origem nao existe ou nao e acessivel.")

    ronda_id = args.ronda
    if ronda_id is None:
        from datetime import datetime
        ronda_id = f"RONDA-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("Contando arquivos da origem...", flush=True)
    source_total = sum(
        len(files) for _, _, files in os.walk(args.source)
    )

    progress = ImportProgress(
        STORAGE_ROOT,
        ronda_id,
        {
            "source": os.path.abspath(args.source),
            "wbs": args.wbs,
            "usuario": args.usuario,
            "source_total": source_total,
            "source_completed": 0,
            "units_processed": 0,
            "current_path": None,
            "novos": 0,
            "duplicados": 0,
            "indexados": 0,
            "sem_texto": 0,
            "sem_estante": 0,
            "desbloqueados": 0,
            "errors_count": 0,
            "recent_errors": [],
        },
    )

    last_saved_units = -1
    last_saved_source = -1

    def save_progress(summary, current_path, source_completed, total):
        nonlocal last_saved_units, last_saved_source
        units = summary.total

        if (
            units - last_saved_units < 25
            and source_completed - last_saved_source < 25
            and source_completed < total
        ):
            return

        progress.update(
            source_total=total,
            source_completed=source_completed,
            units_processed=units,
            current_path=str(current_path),
            novos=summary.novos,
            duplicados=summary.duplicados,
            indexados=summary.indexados,
            sem_texto=summary.sem_texto,
            sem_estante=summary.sem_estante,
            desbloqueados=summary.desbloqueados,
            errors_count=len(summary.erros),
            recent_errors=summary.erros[-10:],
        )
        last_saved_units = units
        last_saved_source = source_completed

    try:
        with get_session() as session:
            summary = import_source(
                session,
                args.source,
                STORAGE_ROOT,
                obra_wbs=args.wbs,
                ronda_id=ronda_id,
                usuario_captura=args.usuario,
                progress_callback=save_progress,
                source_total=source_total,
            )

        progress.finish(
            "completed_with_errors" if summary.erros else "completed",
            source_total=source_total,
            source_completed=source_total,
            units_processed=summary.total,
            current_path=None,
            novos=summary.novos,
            duplicados=summary.duplicados,
            indexados=summary.indexados,
            sem_texto=summary.sem_texto,
            sem_estante=summary.sem_estante,
            desbloqueados=summary.desbloqueados,
            errors_count=len(summary.erros),
            recent_errors=summary.erros[-10:],
        )

        print("=" * 60)
        print("HUDSON IMPORT CLI — RELATORIO DA RONDA")
        print("=" * 60)
        print(f"Ronda ID:                    {summary.ronda_id}")
        print(f"Arquivos fisicos na origem:  {source_total}")
        print(f"Unidades processadas:        {summary.total}")
        print(f"Novos itens custodiados:     {summary.novos}")
        print(f"Indexados:                   {summary.indexados}")
        print(f"Desbloqueados:               {summary.desbloqueados}")
        print(f"Sem texto extraido:          {summary.sem_texto}")
        print(f"Sem estante mapeada:         {summary.sem_estante}")
        print(f"Duplicados:                  {summary.duplicados}")
        print(f"Erros:                       {len(summary.erros)}")
        print(f"Estado persistido em:        {progress.status_path}")
        print("=" * 60)

        if summary.erros:
            for erro in summary.erros[-10:]:
                print(f"  - {erro}")

    except BaseException as exc:
        try:
            progress.finish(
                "failed",
                failure=str(exc),
            )
        except Exception:
            progress.close()
        raise


if __name__ == "__main__":
    main()
