from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import build_backend


ROOT = Path(__file__).resolve().parents[1]


class PackagingSmokeTests(unittest.TestCase):
    def test_build_wheel_contains_real_package_files_and_no_pth(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            wheel_name = build_backend.build_wheel(tmpdir)
            wheel_path = Path(tmpdir) / wheel_name
            self.assertTrue(wheel_path.exists(), "wheel file should be created")

            with ZipFile(wheel_path) as zf:
                names = set(zf.namelist())

            self.assertFalse(
                any(name.endswith(".pth") for name in names),
                "a normal wheel should not depend on a .pth file into the source tree",
            )
            self.assertIn(
                "intelligence/__init__.py",
                names,
                "wheel should package the importable module itself",
            )
            self.assertIn(
                "intelligence/cli.py",
                names,
                "wheel should package the CLI module itself",
            )

    def test_installed_wheel_supports_module_and_console_script_without_source_tree(
        self,
    ) -> None:
        src_dir = ROOT / "src"
        hidden_src_dir = ROOT / "_src_hidden_for_test"
        with tempfile.TemporaryDirectory() as tmpdir:
            wheel_name = build_backend.build_wheel(tmpdir)
            wheel_path = Path(tmpdir) / wheel_name

            if hidden_src_dir.exists():
                shutil.rmtree(hidden_src_dir)
            src_dir.rename(hidden_src_dir)
            try:
                venv_dir = Path(tmpdir) / "venv"
                subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_dir)],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                python_bin = venv_dir / "bin" / "python"
                script_bin = venv_dir / "bin" / "intelligence"

                subprocess.run(
                    [
                        str(python_bin),
                        "-m",
                        "pip",
                        "install",
                        "--no-deps",
                        str(wheel_path),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )

                module_run = subprocess.run(
                    [str(python_bin), "-m", "intelligence", "--version"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual("intelligence 0.1.0", module_run.stdout.strip())

                script_run = subprocess.run(
                    [str(script_bin), "--version"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual("intelligence 0.1.0", script_run.stdout.strip())
            finally:
                if hidden_src_dir.exists():
                    hidden_src_dir.rename(src_dir)

