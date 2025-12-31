if __name__ == "__main__":
    from beat_studio_importer.__main__ import main
    from pathlib import Path
    import sys
    main(cwd=Path.cwd(), argv=sys.argv[1:])
