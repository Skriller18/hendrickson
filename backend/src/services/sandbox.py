import uuid
import tempfile
import os
import subprocess
import asyncio
from pathlib import Path
from typing import AsyncGenerator

import docker
from docker.errors import DockerException


class SandboxExecutor:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except DockerException:
            self.client = None

    async def execute_test(
        self, test_code: str, language: str, framework: str, test_id: str
    ) -> dict:
        if language == "python" and framework == "pytest":
            return await self._execute_python_pytest(test_code, test_id)
        elif language in ("typescript", "javascript") and framework in ("jest", "vitest"):
            return await self._execute_node_test(test_code, test_id, framework)
        else:
            return await self._execute_generic(test_code, test_id)

    async def execute_suite(
        self, tests: list[dict]
    ) -> AsyncGenerator[dict, None]:
        for test in tests:
            result = await self.execute_test(
                test.get("code_body", ""),
                test.get("language", "python"),
                test.get("framework", "pytest"),
                test.get("test_id", "unknown"),
            )
            yield result

    async def _execute_python_pytest(self, test_code: str, test_id: str) -> dict:
        tmp_dir = tempfile.mkdtemp(prefix=f"hendrickson_test_{test_id}_")
        test_file = Path(tmp_dir) / f"test_{test_id}.py"
        test_file.write_text(test_code)

        try:
            proc = await asyncio.create_subprocess_exec(
                "python", "-m", "pytest", str(test_file), "-v", "--tb=short",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmp_dir,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=60
            )

            passed = proc.returncode == 0
            return {
                "test_id": test_id,
                "status": "PASSED" if passed else "FAILED",
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "exit_code": proc.returncode,
            }
        except asyncio.TimeoutError:
            return {
                "test_id": test_id,
                "status": "TIMEOUT",
                "stdout": "",
                "stderr": "Test execution timed out after 60 seconds",
                "exit_code": -1,
            }
        except Exception as e:
            return {
                "test_id": test_id,
                "status": "ERROR",
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _execute_node_test(self, test_code: str, test_id: str, framework: str) -> dict:
        tmp_dir = tempfile.mkdtemp(prefix=f"hendrickson_test_{test_id}_")
        test_file = Path(tmp_dir) / f"test_{test_id}.test.ts"
        test_file.write_text(test_code)

        pkg_json = Path(tmp_dir) / "package.json"
        pkg_json.write_text('{"name":"test","private":true}')

        try:
            proc = await asyncio.create_subprocess_exec(
                "npx", framework, str(test_file), "--no-coverage",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmp_dir,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=60
            )

            passed = proc.returncode == 0
            return {
                "test_id": test_id,
                "status": "PASSED" if passed else "FAILED",
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "exit_code": proc.returncode,
            }
        except asyncio.TimeoutError:
            return {
                "test_id": test_id,
                "status": "TIMEOUT",
                "stdout": "",
                "stderr": "Test execution timed out after 60 seconds",
                "exit_code": -1,
            }
        except Exception as e:
            return {
                "test_id": test_id,
                "status": "ERROR",
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _execute_generic(self, test_code: str, test_id: str) -> dict:
        return {
            "test_id": test_id,
            "status": "SKIPPED",
            "stdout": "",
            "stderr": f"No executor available for this test type",
            "exit_code": 0,
        }
