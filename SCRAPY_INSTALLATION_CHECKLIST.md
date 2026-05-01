# Scrapy + Playwright Installation Checklist

Complete this checklist step-by-step. Copy & check off as you go!

---

## ✅ PHASE 1: Install C++ Build Tools

### Step 1: Download Installer
- [ ] Download: https://aka.ms/vs/17/release/vs_BuildTools.exe
- [ ] Wait for completion (~1-2 GB file)
- [ ] File location: `C:\Users\aziz\Downloads\vs_BuildTools.exe`

### Step 2: Run Installer
- [ ] Right-click `vs_BuildTools.exe`
- [ ] Select "Run as Administrator"
- [ ] Wait 1-2 minutes for installer to load
- [ ] Installer window appeared ✓

### Step 3: Select Components
- [ ] Check: "Desktop development with C++"
- [ ] Also check:
  - [ ] MSVC v143 (C++ compiler)
  - [ ] Windows 10/11 SDK
  - [ ] CMake tools for Windows
- [ ] Click "Install" (blue button, bottom right)
- [ ] Installation progress bar started ✓

### Step 4: Wait for Installation
- [ ] ⏱️ Waiting 10-15 minutes...
- [ ] Installation completed successfully
- [ ] Close installer window if it finishes

### Step 5: Restart (if needed)
- [ ] If prompted to restart: Restart computer
- [ ] Wait for restart
- [ ] Open PowerShell again

---

## ✅ PHASE 2: Install Python Packages

### Step 1: Open PowerShell
- [ ] Open PowerShell (regular, not Admin)
- [ ] Navigate: `cd C:\Users\aziz\Desktop\projects\behaviorlens-tunisia`
- [ ] Verify you're in the right directory ✓

### Step 2: Install Scrapy
Run this command:
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy
```

- [ ] Command started
- [ ] ⏱️ Wait 2-5 minutes
- [ ] Check output for: "Successfully installed scrapy-2.x.x"
- [ ] Installation completed ✓

### Step 3: Install Scrapy-Playwright
Run this command:
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy-playwright
```

- [ ] Command started
- [ ] ⏱️ Wait 1-2 minutes
- [ ] Output shows: "Successfully installed..."
- [ ] Installation completed ✓

### Step 4: Install Playwright
Run this command:
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install playwright
```

- [ ] Command started
- [ ] ⏱️ Wait 1-2 minutes
- [ ] Output shows: "Successfully installed..."
- [ ] Installation completed ✓

---

## ✅ PHASE 3: Verify Installation

### Step 1: Test Imports
Run this command:
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy, playwright; print('✅ Scrapy:', scrapy.__version__); print('✅ Playwright installed')"
```

- [ ] Command executed
- [ ] Output shows version numbers
- [ ] No errors ✓

**Expected output:**
```
✅ Scrapy: 2.x.x
✅ Playwright installed
```

### Step 2: Verify Full Installation
```powershell
C:/Users/aziz/.local/bin/python3.15.exe setup_and_status.py
```

- [ ] Command executed
- [ ] Should now show scrapy, playwright as installed
- [ ] Check output ✓

---

## ✅ PHASE 4: Configure for InsightTN

### Step 1: Download Configuration Guide
- [ ] Read: `SCRAPY_PLAYWRIGHT_COMPLETE_GUIDE.md`
- [ ] Review: Part 3 (Configure Scrapy for InsightTN)
- [ ] Copy spider files to: `social_media/spiders/`

### Step 2: Create Spider Directory
```powershell
mkdir social_media\spiders
```

- [ ] Directory created
- [ ] Spiders can be added here

### Step 3: Configure Settings
- [ ] Create: `social_media/scrapy_settings.py`
- [ ] Copy content from guide
- [ ] Save file

### Step 4: Update config.py
- [ ] Edit: `social_media/config.py`
- [ ] Add Scrapy configuration section
- [ ] Enable: `"enabled": True`
- [ ] Save file

---

## ✅ PHASE 5: Test Scrapy Setup

### Step 1: List Available Spiders
```powershell
cd social_media
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy list
```

- [ ] Command executed
- [ ] Output shows spiders (if any created)
- [ ] No errors ✓

### Step 2: Test Collection
```powershell
cd ..
python -m social_media.app --collect --mode scrapy
```

- [ ] Collection started
- [ ] Monitor progress
- [ ] Check for errors
- [ ] Collection completed (or note errors)

### Step 3: Check Results
```powershell
dir data\
```

- [ ] Data directory exists
- [ ] Check for new files
- [ ] JSON output created ✓

---

## ✅ PHASE 6: Hybrid Mode Setup

### Step 1: Enable Hybrid Mode
Edit: `social_media/config.py`

Set:
```python
"graph_api": {"enabled": True},
"scrapy": {"enabled": True}
```

- [ ] Both sources enabled
- [ ] Credentials set (Graph API token)
- [ ] Config saved

### Step 2: Test Hybrid Collection
```powershell
python -m social_media.app --collect --mode hybrid
```

- [ ] Graph API collection started
- [ ] Scrapy collection started
- [ ] Both running (may take longer)
- [ ] Results merged

### Step 3: Verify Combined Data
```powershell
python -c "import json; posts = json.load(open('data/extracted/posts.json')); print(f'Total posts: {len(posts)}'); print('Sources:', set(p['source'] for p in posts))"
```

- [ ] Total post count shown
- [ ] Multiple sources listed
- [ ] Hybrid mode working ✓

---

## 📊 Status Summary

After completing all phases, you should have:

| Component | Status |
|-----------|--------|
| C++ Build Tools | ✅ Installed |
| Scrapy | ✅ Installed |
| Scrapy-Playwright | ✅ Installed |
| Playwright | ✅ Installed |
| Spiders | ✅ Created |
| Configuration | ✅ Updated |
| Hybrid Mode | ✅ Working |
| Graph API | ✅ Ready |

---

## 🆘 Troubleshooting

### "C++ compiler not found"
- [ ] Restart computer after C++ installation
- [ ] Run installer again (Part 1)

### "scrapy module not found"
- [ ] Run: `C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy`
- [ ] Wait for installation
- [ ] Try again

### "Playwright not found"
- [ ] Run: `C:/Users/aziz/.local/bin/python3.15.exe -m pip install playwright`
- [ ] Verify installation

### "Permission denied"
- [ ] Don't use Admin PowerShell for normal pip install
- [ ] Use regular PowerShell
- [ ] Only use Admin for C++ installer

### "Collection fails"
- [ ] Check Graph API token is set
- [ ] Verify internet connection
- [ ] Check config.py syntax
- [ ] Review logs in `data/logs/`

---

## ✨ Next Steps

Once everything is installed:

1. **Set Graph API Token**
   ```powershell
   $env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
   ```

2. **Update Page IDs**
   Edit `social_media/config.py` and add your page IDs

3. **Start Collection**
   ```powershell
   python -m social_media.app --collect
   ```

4. **View Results**
   ```powershell
   cat data\extracted\posts.json
   ```

---

## 📝 Notes

Use this space to track your progress:

```
Started: _________________
C++ installation completed: _________________
Scrapy installed: _________________
All tests passed: _________________
Hybrid mode working: _________________
First collection completed: _________________
```

---

## 🎉 Completion

You're done when:
- ✅ All phases completed
- ✅ All tests passing
- ✅ Hybrid collection working
- ✅ Data being collected

**Congratulations! Your Scrapy + Playwright setup is complete!** 🚀

