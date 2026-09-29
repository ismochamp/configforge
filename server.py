#!/usr/bin/env python3
"""Local-only review interface for the C++17 migration engine; stdlib only."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
META = json.loads((ROOT / "project.json").read_text())
MAX_BODY = 2 * 1024 * 1024


def execute(text, mappings=None, inspect=False):
    if not isinstance(text, str) or len(text.encode("utf-8")) > 1024 * 1024:
        raise ValueError("Paste or upload UTF-8 input up to 1 MiB.")
    if not text.strip():
        raise ValueError("Add source text before running a migration.")
    with tempfile.TemporaryDirectory(prefix=META["name"].lower() + "-") as work:
        work = Path(work)
        source = work / ("source." + META["kind"])
        output = work / "result.json"
        source.write_text(text, encoding="utf-8", newline="")
        binary = ROOT / "build" / ("migrator.exe" if __import__("os").name == "nt" else "migrator")
        command = [str(binary), "--input", str(source)]
        if inspect:
            command += ["--inspect"]
        else:
            if not isinstance(mappings, list) or not 1 <= len(mappings) <= 256:
                raise ValueError("Choose between 1 and 256 field mappings.")
            lines = []
            for entry in mappings:
                if not isinstance(entry, dict):
                    raise ValueError("Each mapping must be an object.")
                values = [entry.get("source"), entry.get("target"), entry.get("type")]
                if any(not isinstance(v, str) or not v.strip() or any(c in v for c in "\t\r\n\x00") for v in values):
                    raise ValueError("Mapping values must be non-empty text without tabs or line breaks.")
                if values[2] not in ("string", "integer", "number", "boolean"):
                    raise ValueError("Unsupported field type.")
                if not isinstance(entry.get("required"), bool):
                    raise ValueError("Required must be a boolean.")
                lines.append("\t".join(values + [str(entry["required"]).lower()]))
            mapping = work / "mapping.tsv"
            mapping.write_text("\n".join(lines) + "\n", encoding="utf-8")
            command += ["--map", str(mapping), "--output", str(output)]
        process = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        try:
            result = json.loads(process.stdout)
        except (ValueError, TypeError) as error:
            raise RuntimeError("Migration engine did not return a valid report.") from error
        if process.returncode not in (0, 2):
            raise RuntimeError("Migration engine exited unexpectedly.")
        if result["ok"] and not inspect:
            result["output"] = output.read_text(encoding="utf-8")
            decoded = json.loads(result["output"])
            result["preview"] = decoded[:20] if isinstance(decoded, list) else decoded
        return result


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/meta":
            mappings = []
            for line in (ROOT / "fixtures/mapping.tsv").read_text().splitlines():
                source, target, kind, required = line.split("\t")
                mappings.append(dict(source=source, target=target, type=kind, required=required == "true"))
            self.respond(200, dict(META, sample=(ROOT / "fixtures" / META["fixture"]).read_text(), mappings=mappings))
            return
        files = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
        if path not in files:
            self.respond(404, {"error": "Not found"})
            return
        name, content_type = files[path]
        self.respond(200, (ROOT / "web" / name).read_bytes(), content_type)

    def do_POST(self):
        if self.path not in ("/api/inspect", "/api/migrate"):
            self.respond(404, {"error": "Not found"})
            return
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"):
            self.respond(403, {"error": "This local tool only accepts requests from its own page."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                raise ValueError("Request exceeds the 2 MiB limit or is empty.")
            if "application/json" not in self.headers.get("Content-Type", ""):
                raise ValueError("Expected application/json.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            self.respond(200, execute(data.get("text"), data.get("mappings"), inspect=self.path.endswith("inspect")))
        except (ValueError, UnicodeError) as error:
            self.respond(400, {"error": str(error)})
        except subprocess.TimeoutExpired:
            self.respond(422, {"error": "Migration exceeded the 20-second execution limit."})
        except Exception as error:
            self.respond(500, {"error": str(error)})

    def log_message(self, format, *args):
        print("[local] " + format % args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=META["port"])
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"{META['name']} ready at http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
