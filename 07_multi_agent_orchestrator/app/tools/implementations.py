import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.memory.store import VectorMemory


class CodeArgs(BaseModel):
    code: str = Field(min_length=1, max_length=4000)


class PythonCodeTool:
    name = "python_code"
    description = "Run a small Python script in a subprocess."
    args_model = CodeArgs

    async def run(self, arguments: CodeArgs) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "snippet.py"
            script.write_text(arguments.code, encoding="utf-8")
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=settings.tool_timeout_seconds,
                )
            except TimeoutError:
                process.kill()
                return {"ok": False, "error": "Code execution timed out"}
        return {
            "ok": process.returncode == 0,
            "stdout": stdout.decode("utf-8", errors="replace").strip(),
            "stderr": stderr.decode("utf-8", errors="replace").strip(),
        }


class HttpArgs(BaseModel):
    url: str
    method: str = "GET"


class HttpRequestTool:
    name = "http_request"
    description = "Perform a simple HTTP request."
    args_model = HttpArgs

    async def run(self, arguments: HttpArgs) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.tool_timeout_seconds) as client:
            response = await client.request(arguments.method, arguments.url)
        return {"status_code": response.status_code, "text": response.text[:1000]}


class MemorySaveArgs(BaseModel):
    text: str = Field(min_length=1)


class MemorySaveTool:
    name = "memory_save"
    description = "Save a fact to shared vector memory."
    args_model = MemorySaveArgs

    def __init__(self, memory: VectorMemory) -> None:
        self.memory = memory

    async def run(self, arguments: MemorySaveArgs) -> dict[str, Any]:
        self.memory.save(arguments.text)
        return {"ok": True}


class WebSearchArgs(BaseModel):
    query: str


class WebSearchTool:
    name = "web_search"
    description = "Return a compact search style note for a query."
    args_model = WebSearchArgs

    async def run(self, arguments: WebSearchArgs) -> dict[str, Any]:
        return {"results": [f"Search note for: {arguments.query}"]}
