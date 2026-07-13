"""Comprehensive unit tests for build.py"""

import os
import sys
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock, ANY

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402


# --- Helpers ---

def make_fake_iso(name="tails1154os-2026.07.12-x86_64.iso", out=None):
    out = out or build.OUT
    out.mkdir(parents=True, exist_ok=True)
    iso = out / name
    iso.write_text("fake iso content")
    return str(iso)


# --- Test helpers ---

class TestRun:
    def test_runs_command(self):
        result = build.run(["echo", "hello"], capture_output=True, text=True)
        assert "hello" in result.stdout

    def test_check_default_true(self):
        try:
            build.run(["false"], capture_output=True)
            assert False, "should have raised"
        except subprocess.CalledProcessError:
            pass

    def test_check_false(self):
        build.run(["false"], check=False, capture_output=True)


class TestLog:
    def test_log_output(self, capsys):
        build.log("test message")
        captured = capsys.readouterr().out
        assert "test message" in captured


# --- Command tests ---

class TestFindIso:
    def test_no_iso(self):
        for f in build.OUT.glob("tails1154os-*.iso"):
            f.unlink()
        assert build.find_iso() is None

    def test_finds_latest(self):
        make_fake_iso("tails1154os-2026.01.01-x86_64.iso")
        make_fake_iso("tails1154os-2026.06.15-x86_64.iso")
        latest = make_fake_iso("tails1154os-2026.07.12-x86_64.iso")
        assert build.find_iso() == latest


class TestCmdBuild:
    def test_build_creates_work_and_out(self):
        args = MagicMock()
        with patch.object(build, 'run') as mock_run, \
             patch.object(build, 'find_iso', return_value=None):
            build.cmd_build(args)
            mock_run.assert_any_call(["sudo", "umount", "-R", str(build.WORK)], check=False)
            mock_run.assert_any_call(["sudo", "losetup", "-D"], check=False)
            mock_run.assert_any_call(["sudo", "mkarchiso", "-v", "-w", str(build.WORK),
                                      "-o", str(build.OUT), str(build.ROOT)])

    def test_build_returns_iso_path(self):
        args = MagicMock()
        with patch.object(build, 'run'), \
             patch.object(build, 'find_iso') as mock_find, \
             patch.object(build.os.path, 'getsize', return_value=100):
            mock_find.return_value = "/fake/iso.iso"
            result = build.cmd_build(args)
            assert result == "/fake/iso.iso"


class TestCmdCopy:
    def test_exits_if_no_iso(self):
        args = MagicMock(iso=None)
        for f in build.OUT.glob("tails1154os-*.iso"):
            f.unlink()
        try:
            build.cmd_copy(args)
            assert False, "should have exited"
        except SystemExit as e:
            assert e.code == 1

    def test_copies_with_dd(self):
        iso = make_fake_iso()
        args = MagicMock(iso=iso, device="/dev/null")
        with patch.object(build.shutil, 'which', return_value=None), \
             patch.object(build, 'run') as mock_run:
            build.cmd_copy(args)
            mock_run.assert_called_with(
                ["sudo", "dd", f"if={iso}", "of=/dev/null", "bs=100M",
                 "status=progress", "oflag=sync"])

    def test_copies_with_pv(self):
        iso = make_fake_iso()
        args = MagicMock(iso=iso, device="/dev/null")
        with patch.object(build.shutil, 'which', return_value="/usr/bin/pv"), \
             patch.object(build.subprocess, 'run') as mock_run:
            build.cmd_copy(args)
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "pv" in call_args
            assert "dd" in call_args

    def test_accepts_custom_iso(self):
        iso = make_fake_iso("custom.iso")
        args = MagicMock(iso=iso, device="/dev/null")
        with patch.object(build.shutil, 'which', return_value=None), \
             patch.object(build, 'run'):
            build.cmd_copy(args)

    def test_rejects_missing_iso(self):
        args = MagicMock(iso="/nonexistent.iso", device="/dev/null")
        try:
            build.cmd_copy(args)
            assert False
        except SystemExit:
            pass


class TestCmdQemu:
    def test_rejects_no_iso(self):
        args = MagicMock(iso=None)
        for f in build.OUT.glob("tails1154os-*.iso"):
            f.unlink()
        try:
            build.cmd_qemu(args)
            assert False
        except SystemExit:
            pass

    def test_launches_qemu(self):
        iso = make_fake_iso()
        args = MagicMock(iso=iso)
        type(args).memory = PropertyMock(return_value="2G")
        with patch.object(build, 'run') as mock_run:
            build.cmd_qemu(args)
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "qemu-system-x86_64" in cmd
            assert "-m" in cmd
            assert iso in cmd

    def test_default_memory(self):
        iso = make_fake_iso()
        args = MagicMock(iso=iso)
        type(args).memory = PropertyMock(return_value="4G")
        with patch.object(build, 'run') as mock_run:
            build.cmd_qemu(args)
            cmd = mock_run.call_args[0][0]
            mem_idx = cmd.index("-m") + 1
            assert cmd[mem_idx] == "4G"


class TestCmdClean:
    def test_unmounts_before_remove(self):
        with patch.object(build, 'run') as mock_run, \
             patch.object(build.Path, 'exists', return_value=True), \
             patch.object(build.shutil, 'rmtree'):
            build.cmd_clean(None)
            mock_run.assert_any_call(["sudo", "umount", "-R", str(build.WORK)], check=False)


class TestMain:
    def test_build_subcommand(self):
        test_args = ["build"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_build') as mock_cmd:
            build.main()
            mock_cmd.assert_called_once()

    def test_clean_subcommand(self):
        test_args = ["clean"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_clean') as mock_cmd:
            build.main()
            mock_cmd.assert_called_once()

    def test_copy_subcommand(self):
        test_args = ["copy", "/dev/sda"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_copy') as mock_cmd:
            build.main()
            mock_cmd.assert_called_once()

    def test_qemu_subcommand(self):
        test_args = ["qemu"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_qemu') as mock_cmd:
            build.main()
            mock_cmd.assert_called_once()

    def test_flash_subcommand(self):
        test_args = ["flash", "/dev/sda"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_build', return_value="/fake.iso"), \
             patch.object(build, 'cmd_copy') as mock_copy:
            build.main()
            mock_copy.assert_called_once()

    def test_all_subcommand(self):
        test_args = ["all", "/dev/sda"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_build', return_value="/fake.iso"), \
             patch.object(build, 'cmd_copy') as mock_copy, \
             patch.object(build, 'cmd_qemu') as mock_qemu:
            build.main()
            mock_copy.assert_called_once()
            mock_qemu.assert_called_once()

    def test_all_skip_qemu(self):
        test_args = ["all", "--skip-qemu"]
        with patch.object(sys, 'argv', ['build.py'] + test_args), \
             patch.object(build, 'cmd_build', return_value="/fake.iso"), \
             patch.object(build, 'cmd_copy') as mock_copy, \
             patch.object(build, 'cmd_qemu') as mock_qemu:
            build.main()
            mock_copy.assert_not_called()
            mock_qemu.assert_not_called()

    def test_no_args_shows_usage(self):
        try:
            with patch.object(sys, 'argv', ['build.py']):
                build.main()
            assert False, "should have exited"
        except SystemExit:
            pass

    def test_help(self):
        for flag in ["-h", "--help"]:
            try:
                with patch.object(sys, 'argv', ['build.py', flag]):
                    build.main()
                assert False
            except SystemExit:
                pass


class TestIntegration:
    def test_cmd_build_to_find_iso(self):
        args = MagicMock()
        with patch.object(build, 'run'), \
             patch.object(build, 'find_iso', return_value="/fake.iso"), \
             patch.object(build.os.path, 'getsize', return_value=100):
            result = build.cmd_build(args)
            assert result == "/fake.iso"

    def test_find_iso_returns_iso_in_out(self):
        if list(build.OUT.glob("tails1154os-*.iso")):
            found = build.find_iso()
            assert found is not None
            assert found.startswith(str(build.OUT))

    def test_run_exits_on_failure(self):
        try:
            build.run(["nonexistent_command_12345"], check=True, capture_output=True)
            assert False
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass


class TestEdgeCases:
    def test_work_dir_path(self):
        assert str(build.WORK).endswith("/work")

    def test_out_dir_path(self):
        assert str(build.OUT).endswith("/out")

    def test_iso_pattern(self):
        assert build.ISO_PATTERN == "tails1154os-*.iso"

    def test_find_iso_multiple_versions(self):
        iso1 = make_fake_iso("tails1154os-2026.01.01-x86_64.iso")
        iso2 = make_fake_iso("tails1154os-2026.07.12-x86_64.iso")
        found = build.find_iso()
        assert found == iso2
        assert found != iso1

    def test_run_with_capture(self):
        result = build.run(["echo", "hello"], capture_output=True, text=True)
        assert result.returncode == 0


class TestSubprocessKwargs:
    def test_check_false_overrides_default(self):
        proc = build.run(["echo", "hi"], check=False, capture_output=True, text=True)
        assert proc.returncode == 0

    def test_check_true_raises(self):
        try:
            build.run(["false"], check=True, capture_output=True)
            assert False
        except subprocess.CalledProcessError:
            pass

    def test_run_passes_extra_kwargs(self):
        env = {"TEST_ENV": "value"}
        result = build.run(["sh", "-c", "echo $TEST_ENV"], capture_output=True,
                           text=True, env={**os.environ, **env})
        assert "value" in result.stdout
