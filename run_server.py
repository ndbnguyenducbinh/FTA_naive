import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import api_router

app = FastAPI(
    title="Neuro-Symbolic Diagnostic Copilot API & Prototype",
    description="Backend engine combining GraphRAG and Bayesian Inference for Hardware Diagnostic",
    version="2.5",
)

# Include API Router
app.include_router(api_router)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to Neuro-Symbolic Diagnostic Copilot API. Visit /docs for Swagger."}

@app.get("/favicon.ico")
def serve_favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    import socket

    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    target_port = int(os.getenv("PORT", 8000))
    if is_port_in_use(target_port) and "PORT" not in os.environ:
        # Fallback to next available port if default 8000 is occupied
        for p in range(8001, 8010):
            if not is_port_in_use(p):
                target_port = p
                break

    print("\n" + "="*70)
    print("🚀 NEURO-SYMBOLIC DIAGNOSTIC COPILOT (PROTOTYPE SERVER)")
    print(f"📍 Dashboard UI:       http://localhost:{target_port}")
    print(f"📖 OpenAPI / Swagger:  http://localhost:{target_port}/docs")
    print("⚡ Real-time Bayesian: Sub-10ms latency ready")
    print("="*70 + "\n")
    uvicorn.run("run_server:app", host="0.0.0.0", port=target_port, reload=False)

