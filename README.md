# 🎙️ Gamer Voice-to-Text (Accessibility Tool)

A push-to-talk **Voice-to-Text** tool for gaming chat and accessibility.  
It uses **OpenAI Whisper** for transcription and **runs locally on your PC** (no cloud / no “Google Translate” style service, no server timeouts).

Hold a key → speak → release → it transcribes → copies to clipboard → paste with **Ctrl+V**.

---

## 🎥 Demo video
YouTube demo (v1.0.0):  
https://www.youtube.com/watch?v=ywVSkvJV5mg

---

## 🚀 Features
- **Local transcription (No cloud):** Speech is processed on your computer.
- **Push-to-talk workflow:** Hold your talk key, speak, release to transcribe.
- **Clipboard copy:** Automatically copies the transcript (paste with **Ctrl+V**).
- **Rebind keys inside the app:** No manual config editing required.
- **GPU acceleration (if available):** Uses CUDA when your setup supports it.

---

## 🧩 How it works (quick)
1. Choose **Start Voice-to-Text**
2. Hold your **Record / Talk** key
3. Speak
4. Release
5. Transcript is copied to clipboard → paste anywhere with **Ctrl+V**

---

## ⬇️ Download (Windows)
### Option A: GitHub Release (may be split into parts)
If the release is split (because of file size limits), download **all** parts (`.zip`, `.z01`, `.z02`, etc.) into the **same folder**, then open the `.zip` with WinRAR/7-Zip to extract.

### Option B: Google Drive (single ZIP)
Use the Drive link in the GitHub Release notes / README (single file is easiest for most people).

### SHA256 (for verifying the Google Drive ZIP)
`S_to_T_v1.0.0_windows.zip`  
`FCD7ADAD20320CCCA2ED62BD6B7CD2CFBB5DA68A1E5E394FBF623D8DD213A2E8`

To verify on Windows PowerShell:
```powershell
Get-FileHash ".\S_to_T_v1.0.0_windows.zip" -Algorithm SHA256
