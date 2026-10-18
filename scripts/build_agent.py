"""Developer packaging only. The downloaded agent needs no Python."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FILES = ('AGENTS.md', 'CLAUDE.md', 'START HERE.md', 'OPERATIONS.md', 'REVIEW.md', 'tools/records.js')


def build(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    bodies = {name: (ROOT / 'agent' / name).read_bytes() for name in FILES}
    manifest = {'name': 'Support Release Readiness', 'version': '0.2.2', 'state_schema': 1,
                'supported_target': 'macOS local Codex and Claude Code desktop sessions',
                'readiness': 'Desktop and independent-user acceptance gates remain separate from software tests',
                'files': {name: hashlib.sha256(body).hexdigest() for name, body in bodies.items()}}
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name, body in bodies.items():
            archive.writestr('Release Readiness/' + name, body)
        archive.writestr('Release Readiness/PACKAGE.json', json.dumps(manifest, indent=2) + '\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/support-release-readiness-agent.zip')
    print(build(parser.parse_args().output))
