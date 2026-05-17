# ScanLine Release Guide

## Local release flow

1. Create and activate a clean virtual environment.
2. Install dependencies from `requirements.txt` and `pyinstaller`.
3. Verify `python main.py` works before packaging.
4. Build with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_release.ps1 -Version v0.1.0
```

5. Test `dist\ScanLine\ScanLine.exe`.
6. Upload `release\ScanLine-v0.1.0-win64.zip` to a GitHub Release.

## Notes

- This project should be shipped as a one-folder build, not one-file.
- EasyOCR may download model files on first launch if they are not already cached.
- Windows Defender warnings are possible for unsigned executables.
- If you need fully offline first-run behavior, bundle the EasyOCR model cache separately.

## GitHub release flow

1. Commit the release preparation changes.
2. Create and push a version tag, for example:

```powershell
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

3. Open GitHub Releases.
4. Draft a release for the tag.
5. Upload the generated ZIP as the release asset.
