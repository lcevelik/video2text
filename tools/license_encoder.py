#!/usr/bin/env python3
"""
License file encoder/decoder utility.

Encodes licenses.txt into an obfuscated format for distribution.
The encoded file is not meant to be cryptographically secure, but rather
to prevent casual viewing of test license keys in distributed builds.
"""

import base64
import sys
from pathlib import Path


def encode_license_file(input_path: Path, output_path: Path):
    """
    Encode a license file using base64 + simple XOR obfuscation.

    Args:
        input_path: Path to plaintext licenses.txt
        output_path: Path to save encoded licenses.dat
    """
    # Read plaintext licenses
    with open(input_path, 'r') as f:
        content = f.read()

    # Encode to bytes
    content_bytes = content.encode('utf-8')

    # Simple XOR with key (not cryptographically secure, just obfuscation)
    key = b'FonixFlow2024VideoTranscription'
    xor_bytes = bytearray()
    for i, byte in enumerate(content_bytes):
        xor_bytes.append(byte ^ key[i % len(key)])

    # Base64 encode the result
    encoded = base64.b64encode(bytes(xor_bytes))

    # Write to output file
    with open(output_path, 'wb') as f:
        f.write(encoded)

    print(f"✅ Encoded {input_path} -> {output_path}")
    print(f"   Original size: {len(content_bytes)} bytes")
    print(f"   Encoded size: {len(encoded)} bytes")


def decode_license_file(input_path: Path) -> str:
    """
    Decode an encoded license file.

    Args:
        input_path: Path to encoded licenses.dat

    Returns:
        Decoded plaintext content
    """
    # Read encoded file
    with open(input_path, 'rb') as f:
        encoded = f.read()

    # Base64 decode
    xor_bytes = base64.b64decode(encoded)

    # XOR with same key to decode
    key = b'FonixFlow2024VideoTranscription'
    content_bytes = bytearray()
    for i, byte in enumerate(xor_bytes):
        content_bytes.append(byte ^ key[i % len(key)])

    # Decode to string
    content = bytes(content_bytes).decode('utf-8')

    return content


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Encode: python license_encoder.py encode <input.txt> [output.dat]")
        print("  Decode: python license_encoder.py decode <input.dat>")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'encode':
        if len(sys.argv) < 3:
            print("Error: Input file required")
            sys.exit(1)

        input_path = Path(sys.argv[2])
        output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else input_path.with_suffix('.dat')

        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)

        encode_license_file(input_path, output_path)

    elif command == 'decode':
        if len(sys.argv) < 3:
            print("Error: Input file required")
            sys.exit(1)

        input_path = Path(sys.argv[2])

        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            sys.exit(1)

        content = decode_license_file(input_path)
        print("Decoded content:")
        print("=" * 50)
        print(content)
        print("=" * 50)

    else:
        print(f"Error: Unknown command: {command}")
        print("Use 'encode' or 'decode'")
        sys.exit(1)


if __name__ == '__main__':
    main()
