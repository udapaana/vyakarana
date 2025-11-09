#!/usr/bin/env python3
"""
Simple HTTP server to serve images for OCR
Run this in the background, then Claude can fetch images via HTTP
"""

import http.server
import socketserver
import json
from pathlib import Path
import base64

PORT = 8765


class OCRImageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/image/"):
            # Extract page number from URL: /image/251
            page_num = self.path.split("/")[-1]
            try:
                page_num = int(page_num)
                img_path = Path(f"phase1_ocr/images/official_1931/{page_num:03d}.png")

                if img_path.exists():
                    # Serve the image
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    with open(img_path, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, f"Image not found: {page_num}")
            except Exception as e:
                self.send_error(500, str(e))

        elif self.path == "/batch":
            # Return JSON list of available pages
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            output_dir = Path("phase1_ocr/sources/official_1931")
            available_pages = []

            for page_num in range(251, 733):
                txt_path = output_dir / f"{page_num:03d}.txt"
                if not txt_path.exists():
                    available_pages.append(page_num)
                    if len(available_pages) >= 10:  # Return first 10 unprocessed
                        break

            response = {
                "available_pages": available_pages,
                "base_url": f"http://localhost:{PORT}/image/",
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()


def run_server():
    with socketserver.TCPServer(("", PORT), OCRImageHandler) as httpd:
        print(f"🌐 OCR Image Server running on http://localhost:{PORT}")
        print(f"\nEndpoints:")
        print(
            f"  - http://localhost:{PORT}/batch - Get next batch of unprocessed pages"
        )
        print(f"  - http://localhost:{PORT}/image/251 - Get specific page image")
        print(f"\nPress Ctrl+C to stop\n")
        httpd.serve_forever()


if __name__ == "__main__":
    import os

    os.chdir("/Users/skmnktl/Downloads/ocr")
    run_server()
