import pathlib
import sys

REQUIRED_FILES = [
    "app/main.py",
    "app/api/routes.py",
    "app/services/profile_cache.py",
    "alembic.ini",
    "alembic/env.py",
    "alembic/versions/0001_initial.py",
    "docker-compose.yml",
    "tests/locustfile.py",
]


def check_required_files() -> tuple[bool, list[str]]:
    missing = [f for f in REQUIRED_FILES if not pathlib.Path(f).exists()]
    return (len(missing) == 0, missing)


# def check_python_syntax() -> tuple[bool, list[str]]:
#     failures: list[str] = []
#     for path in pathlib.Path('.').rglob('*.py'):
#         if "__pycache__" in path.parts:
#             continue
#         try:
#             compile(path.read_text(encoding='utf-8'), str(path), 'exec')
#         except Exception as exc:
#             failures.append(f"{path}: {exc}")
#     return (len(failures) == 0, failures)


def main() -> int:
    ok_files, missing = check_required_files()
    ok_syntax, syntax_errors = check_python_syntax()

    print("[Readiness Check]")
    print(f"- Required files: {'PASS' if ok_files else 'FAIL'}")
    if missing:
        for item in missing:
            print(f"  missing: {item}")

    print(f"- Python syntax: {'PASS' if ok_syntax else 'FAIL'}")
    if syntax_errors:
        for item in syntax_errors:
            print(f"  syntax: {item}")

    print("- Runtime dependencies installed: NOT VERIFIED")
    print("- Infra services running (Postgres/Redis/RabbitMQ): NOT VERIFIED")
    print("- End-to-end tests and load tests: NOT VERIFIED")

    return 0 if (ok_files and ok_syntax) else 1


if __name__ == "__main__":
    sys.exit(main())
