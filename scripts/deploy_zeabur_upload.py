from __future__ import annotations

import argparse
import base64
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_zip(out_path: Path) -> None:
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in ROOT.rglob('*'):
            if p.is_dir():
                continue
            rel = p.relative_to(ROOT)
            rel_s = rel.as_posix()
            if rel_s.startswith('__pycache__/') or p.suffix in {'.pyc', '.pyo', '.pyd'}:
                continue
            zf.write(p, rel_s)


def main() -> None:
    parser = argparse.ArgumentParser(description='Upload current project zip to an existing Zeabur service')
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--service-id', required=True)
    parser.add_argument('--environment-id', required=True)
    args = parser.parse_args()

    zip_path = ROOT.parent / f'{ROOT.name}.zip'
    build_zip(zip_path)
    data = zip_path.read_bytes()
    sha = base64.b64encode(hashlib.sha256(data).digest()).decode()

    base_headers = {
        'authorization': f'Bearer {args.api_key}',
        'user-agent': 'Mozilla/5.0',
        'origin': 'https://zeabur.com',
        'referer': 'https://zeabur.com/',
    }

    body = json.dumps({
        'content_hash': sha,
        'content_hash_algorithm': 'sha256',
        'content_length': len(data),
    }).encode()
    req = urllib.request.Request('https://api.zeabur.com/v2/upload', data=body, method='POST', headers={**base_headers, 'content-type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        create = json.loads(r.read().decode())

    req2 = urllib.request.Request(create['presign_url'], data=data, method=create.get('presign_method', 'PUT'))
    for k, v in create.get('presign_header', {}).items():
        req2.add_header(k, v)
    req2.add_header('Content-Length', str(len(data)))
    with urllib.request.urlopen(req2, timeout=120):
        pass

    body3 = json.dumps({
        'upload_type': 'existing_service',
        'service_id': args.service_id,
        'environment_id': args.environment_id,
    }).encode()
    req3 = urllib.request.Request(
        f'https://api.zeabur.com/v2/upload/{create["upload_id"]}/prepare',
        data=body3,
        method='POST',
        headers={**base_headers, 'content-type': 'application/json'},
    )
    with urllib.request.urlopen(req3, timeout=60) as r:
        prep = json.loads(r.read().decode())

    print('Deploy prepared:', prep['url'])


if __name__ == '__main__':
    main()
