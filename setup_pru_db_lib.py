#!/usr/bin/env python3
"""
Scaffold the static_hash_store package *and* install it in editable‑mode.

Place this script in the project root (same level as agent.py) and run:
    python setup_static_hash_store.py
"""

import textwrap, subprocess, sys
from pathlib import Path

# ---------------------------------------------------------------------------
ROOT   = Path(__file__).resolve().parent
PKG    = ROOT / "static_hash_store"
EXAMPLES = PKG / "examples"
PKG.mkdir(exist_ok=True)
EXAMPLES.mkdir(parents=True, exist_ok=True)

# ---- helper ---------------------------------------------------------------
def write(rel_path: str, code_block: str):
    path = PKG / rel_path
    path.write_text(textwrap.dedent(code_block.lstrip("\n")), encoding="utf‑8")
    print("  ⋄ wrote", path.relative_to(ROOT))

# ---------------------------------------------------------------------------
# 1) individual modules
write("__init__.py", """
    from .store import StaticHashStore
    __all__ = ["StaticHashStore"]
""")

write("const.py", """(# ==================================================
# static_hash_store/const.py
# ==================================================
MAGIC = b"SHS1"          # 4‑byte magic + version major «1»
HEADER_FMT = "<4sHHLQ"    # magic, version_minor (H), key_size (H), segment_count (L), bloom_bits (Q)
HEADER_SIZE = 24          # bytes (4+2+2+4+8+padding)
BUCKET_FMT = "<Q"         # 8‑byte offset of first entry in segment (0 = empty)
BUCKET_SIZE = 8
ENTRY_HDR_FMT = "<QQL"    # next_offset, key_hash, value_size
ENTRY_HDR_SIZE = 8+8+4    # 20 bytes (pad to 24 for alignment)
VERSION_MINOR = 0
""")
write("bloom.py", """
# ==================================================
# static_hash_store/bloom.py
# ==================================================
from math import log, ceil
from hashlib import blake2b
import struct

class Bloom:
    def __init__(self, n_items:int, fp_rate:float=0.01, bits:bytearray|None=None):
        m = ceil(-(n_items * log(fp_rate)) / (log(2)**2))
        k = ceil((m/n_items) * log(2))
        self.m = m
        self.k = k
        self.bits = bits if bits is not None else bytearray((m+7)//8)
    # -- hashing helpers ---------------------------------------------------
    def _hashes(self, key:bytes):
        h = blake2b(key, digest_size=16).digest()
        h1, h2 = struct.unpack("<QQ", h)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m
    # ----------------------------------------------------------------------
    def add(self, key:bytes):
        for bit in self._hashes(key):
            self.bits[bit//8] |= 1 << (bit & 7)
    def __contains__(self, key:bytes):
        return all(self.bits[bit//8] & (1 << (bit & 7)) for bit in self._hashes(key))
    @classmethod
    def from_bytes(cls, n_items:int, fp_rate:float, data:bytes):
        bloom = cls(n_items, fp_rate, bytearray(data))
        return bloom""")
write("compression.py", """(# ==================================================
# static_hash_store/compression.py
# ==================================================
import zstandard as zstd
import struct

# -------- Delta‑encoding helpers -----------------------------------------

def delta_encode(sorted_ints:list[int]) -> bytes:

    out = bytearray()
    prev = 0
    for n in sorted_ints:
        delta = n - prev
        prev = n
        while True:
            byte = delta & 0x7F
            delta >>= 7
            if delta:
                out.append(byte | 0x80)
            else:
                out.append(byte)
                break
    return bytes(out)

# -------- zstd wrappers ---------------------------------------------------

cctx = zstd.ZstdCompressor(level=3)
dctx = zstd.ZstdDecompressor()

def compress(data:bytes) -> bytes:
    return cctx.compress(data)

def decompress(data:bytes) -> bytes:
    return dctx.decompress(data)""")
write("store.py", """# ==================================================
# static_hash_store/store.py
# ==================================================
import mmap, os, struct, fcntl, hashlib
from pathlib import Path
from typing import Iterator, Optional
from .const import *
from .bloom import Bloom
from .compression import compress, decompress

class StaticHashStore:
    def __init__(self, path:str|os.PathLike, key_size:int=8, segments:int=256, bloom_fp:float=0.01):
        self.path = Path(path)
        self.key_size = key_size
        self.segments = segments
        self.bloom_fp = bloom_fp

        if self.path.exists():
            self._open_existing()
        else:
            self._create_new()

    # ------------------------------------------------------------------
    def _create_new(self):
        with open(self.path, "wb") as f:
            # write placeholder header + zeroed bucket table + empty bloom
            bloom_bits = 1  # at least 1 bit
            header = struct.pack(HEADER_FMT, MAGIC, VERSION_MINOR, self.key_size,
                                 self.segments, bloom_bits)
            f.write(header.ljust(HEADER_SIZE, b"\0"))
            f.write(b"\0" * (BUCKET_SIZE * self.segments))
            f.write(b"\0" * bloom_bits)  # placeholder bloom
            f.flush()
        self.file = open(self.path, "r+b")
        self.mm = mmap.mmap(self.file.fileno(), 0)
        # initialize bloom object
        self.bloom = Bloom(0, self.bloom_fp)
        self._header_dirty = True

    def _open_existing(self):
        self.file = open(self.path, "r+b")
        self.mm = mmap.mmap(self.file.fileno(), 0)
        magic, ver_minor, key_sz, seg_cnt, bloom_bits = struct.unpack_from(HEADER_FMT, self.mm, 0)
        if magic != MAGIC:
            raise ValueError("Invalid store file")
        if key_sz != self.key_size:
            raise ValueError("Key size mismatch")
        self.segments = seg_cnt
        bloom_off = HEADER_SIZE + BUCKET_SIZE * self.segments
        bloom_raw = self.mm[bloom_off: bloom_off + bloom_bits]
        self.bloom = Bloom.from_bytes(1, self.bloom_fp, bloom_raw)  # n_items unused
        self._header_dirty = False

    # ------------------------------------------------------------------
    def _segment_of(self, key_hash:int) -> int:
        return key_hash % self.segments

    def _bucket_offset(self, segment:int) -> int:
        return HEADER_SIZE + segment * BUCKET_SIZE

    # ------------------------------------------------------------------
    def get(self, key:bytes) -> Optional[bytes]:
        key_hash = hashlib.blake2b(key, digest_size=8).digest()
        h_int = struct.unpack("<Q", key_hash)[0]
        if key not in self.bloom:
            return None  # fast negative
        seg = self._segment_of(h_int)
        bucket_ptr_off = self._bucket_offset(seg)
        entry_off = struct.unpack_from(BUCKET_FMT, self.mm, bucket_ptr_off)[0]
        while entry_off:
            next_off, e_hash, val_sz = struct.unpack_from(ENTRY_HDR_FMT, self.mm, entry_off)
            k_off = entry_off + ENTRY_HDR_SIZE
            k_bytes = self.mm[k_off: k_off + self.key_size]
            if e_hash == h_int and k_bytes == key:
                v_off = k_off + self.key_size
                return bytes(self.mm[v_off: v_off + val_sz])
            entry_off = next_off
        return None

    # ------------------------------------------------------------------
    def put(self, key:bytes, value:bytes):
        if len(key) != self.key_size:
            raise ValueError("Key length mismatch")
        key_hash = hashlib.blake2b(key, digest_size=8).digest()
        h_int = struct.unpack("<Q", key_hash)[0]
        seg = self._segment_of(h_int)
        bucket_ptr_off = self._bucket_offset(seg)
        # acquire exclusive lock on segment bucket region
        fcntl.lockf(self.file.fileno(), fcntl.LOCK_EX, BUCKET_SIZE, bucket_ptr_off)
        try:
            bucket_head = struct.unpack_from(BUCKET_FMT, self.mm, bucket_ptr_off)[0]
            # append new entry at EOF
            eof = self.mm.size()
            data = struct.pack(ENTRY_HDR_FMT, bucket_head, h_int, len(value)) + key + value
            self.mm.resize(eof + len(data))
            self.mm[eof: eof+len(data)] = data
            # update bucket head pointer
            struct.pack_into(BUCKET_FMT, self.mm, bucket_ptr_off, eof)
            # add to bloom
            self.bloom.add(key)
            self._header_dirty = True
        finally:
            fcntl.lockf(self.file.fileno(), fcntl.LOCK_UN, BUCKET_SIZE, bucket_ptr_off)

    # ------------------------------------------------------------------
    def flush(self):
        if self._header_dirty:
            # write bloom bits & header counts
            bloom_bits = len(self.bloom.bits)
            bloom_off = HEADER_SIZE + BUCKET_SIZE * self.segments
            # resize if needed
            need = bloom_off + bloom_bits
            if self.mm.size() < need:
                self.mm.resize(need)
            self.mm[bloom_off:bloom_off + bloom_bits] = self.bloom.bits
            header = struct.pack(HEADER_FMT, MAGIC, VERSION_MINOR, self.key_size,
                                 self.segments, bloom_bits)
            self.mm[0:len(header)] = header
            self._header_dirty = False
        self.mm.flush()

    # ------------------------------------------------------------------
    def close(self):
        self.flush()
        self.mm.close()
        self.file.close()""")

# 2) example builder (optional)
(EXAMPLES / "build_store.py").write_text(textwrap.dedent("""# ==================================================
# examples/build_store.py
# ==================================================
import struct, argparse, random
from static_hash_store import StaticHashStore

def main():
    p = argparse.ArgumentParser()
    p.add_argument("store", help="path to shs file")
    p.add_argument("count", type=int)
    args = p.parse_args()

    shs = StaticHashStore(args.store, key_size=8)
    pack = struct.Struct("<Q").pack
    for i in range(args.count):
        k = pack(i)
        v = f"value_{i}".encode()
        shs.put(k, v)
    shs.close()

if __name__ == "__main__":
    main()"""), encoding="utf‑8")

# 3) minimal setup.py for editable install
(ROOT / "setup.py").write_text(textwrap.dedent("""
    from setuptools import setup, find_packages
    setup(
        name="static_hash_store",
        version="0.1.0",
        packages=find_packages(),
        install_requires=["numpy", "zstandard"],
        python_requires=">=3.9",
    )
"""), encoding="utf‑8")
print("  ⋄ wrote setup.py")

# ---------------------------------------------------------------------------
print("\n✓  Files scaffolded — running `pip install -e .` …\n")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

print("\n🎉  static_hash_store is now installed in editable‑mode.")
print("    Test with:\n"
      "        python - <<'PY'\n"
      "        from static_hash_store import StaticHashStore\n"
      "        s = StaticHashStore('demo.shs')\n"
      "        s.put(b'12345678', b'hello')\n"
      "        print(s.get(b'12345678'))\n"
      "        PY")
