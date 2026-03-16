#!/usr/bin/env python3
"""MessagePack encoder/decoder."""
import struct, sys

def pack(obj):
    if obj is None: return b"\xc0"
    if obj is True: return b"\xc3"
    if obj is False: return b"\xc2"
    if isinstance(obj, int):
        if 0 <= obj < 128: return bytes([obj])
        if -32 <= obj < 0: return struct.pack("b", obj)
        if 0 <= obj < 256: return b"\xcc" + struct.pack("B", obj)
        if 0 <= obj < 65536: return b"\xcd" + struct.pack(">H", obj)
        return b"\xce" + struct.pack(">I", obj)
    if isinstance(obj, str):
        b = obj.encode()
        if len(b) < 32: return bytes([0xa0 | len(b)]) + b
        return b"\xd9" + bytes([len(b)]) + b
    if isinstance(obj, list):
        if len(obj) < 16: r = bytes([0x90 | len(obj)])
        else: r = b"\xdc" + struct.pack(">H", len(obj))
        for item in obj: r += pack(item)
        return r
    if isinstance(obj, dict):
        if len(obj) < 16: r = bytes([0x80 | len(obj)])
        else: r = b"\xde" + struct.pack(">H", len(obj))
        for k, v in obj.items(): r += pack(k) + pack(v)
        return r
    if isinstance(obj, float): return b"\xcb" + struct.pack(">d", obj)
    return b"\xc0"

def unpack(data, offset=0):
    b = data[offset]
    if b < 0x80: return b, offset + 1
    if b >= 0xe0: return struct.unpack("b", bytes([b]))[0], offset + 1
    if b == 0xc0: return None, offset + 1
    if b == 0xc2: return False, offset + 1
    if b == 0xc3: return True, offset + 1
    if b == 0xcc: return data[offset+1], offset + 2
    if b == 0xcd: return struct.unpack(">H", data[offset+1:offset+3])[0], offset + 3
    if b == 0xce: return struct.unpack(">I", data[offset+1:offset+5])[0], offset + 5
    if b == 0xcb: return struct.unpack(">d", data[offset+1:offset+9])[0], offset + 9
    if 0xa0 <= b <= 0xbf:
        n = b & 0x1f; return data[offset+1:offset+1+n].decode(), offset + 1 + n
    if b == 0xd9:
        n = data[offset+1]; return data[offset+2:offset+2+n].decode(), offset + 2 + n
    if 0x90 <= b <= 0x9f:
        n = b & 0x0f; items = []; off = offset + 1
        for _ in range(n): v, off = unpack(data, off); items.append(v)
        return items, off
    if 0x80 <= b <= 0x8f:
        n = b & 0x0f; d = {}; off = offset + 1
        for _ in range(n):
            k, off = unpack(data, off); v, off = unpack(data, off); d[k] = v
        return d, off
    return None, offset + 1

if __name__ == "__main__":
    obj = {"name": "Rogue", "age": 1, "skills": ["python", "crypto"], "active": True}
    packed = pack(obj)
    unpacked, _ = unpack(packed)
    print(f"Original:  {obj}")
    print(f"Packed:    {packed.hex()} ({len(packed)} bytes)")
    print(f"Unpacked:  {unpacked}")
    print(f"Match:     {obj == unpacked}")
