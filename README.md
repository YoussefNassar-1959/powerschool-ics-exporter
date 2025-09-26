# ALA PowerSchool → Google Calendar Exporter

> **Add all your ALA classes to Google Calendar in under 2 minutes — no coding, no passwords shared, no Google API.**

This tool automatically exports your **weekly class schedule** from PowerSchool (like Physics, ELII, CS, Advisory, etc.) into a file you can **import directly into Google Calendar**.

✅ Works for all ALA students  
✅ 100% private — runs only on your computer  
✅ Handles all your classes, including evening sessions and weekends  
✅ Free and open-source

---

## How to Use (Step-by-Step)

### 1. **Download the Tool**
- Click the green **"Code"** button above
- Click **"Download ZIP"**
- Open your **Downloads** folder and **double-click the ZIP file** to extract it  
  → You’ll see a folder named `powerschool-ics-exporter`

### 2. **Install One Time Only (Takes 30 Seconds)**
- Open the folder you just extracted
- **Double-click** the file called `install.bat` *(Windows)*  
  *(Mac users: see note below)*
- Wait until you see **“✅ All done!”** — then close the window

> **Don’t see `install.bat`?**  
> [Download it here](https://github.com/your-username/powerschool-ics-exporter/raw/main/install.bat) and save it into the folder.

### 3. **Run the Exporter**
- **Double-click** `run.bat`
- A **browser window will open** → **log in to PowerSchool** as usual
- Go to **“My Schedule”** (make sure you see your weekly classes)
- **Wait 5 seconds** after everything loads (no spinning icons!)
- Go back to the black window and **press ENTER**

### 4. **Get Your Calendar File**
- The tool will say:  
  `🎉 Success! Calendar saved to: .../ala_schedule.ics`
- You’ll now see a file called **`ala_schedule.ics`** in the folder

### 5. **Import into Google Calendar**
1. Go to [Google Calendar](https://calendar.google.com)
2. Click the **gear icon ⚙️ → “Settings”**
3. Go to **“Import & export”**
4. Click **“Select file from your computer”** → choose `ala_schedule.ics`
5. Pick a calendar (e.g., “My Classes”) → **Import**

✅ **Done!** Your ALA schedule now appears in Google Calendar — with class names, teachers, rooms, and correct times!

---

## Mac Users
1. Open **Terminal**
2. Run these commands:
   ```bash
   cd ~/Downloads/powerschool-ics-exporter
   pip3 install beautifulsoup4 ics playwright
   playwright install chromium
   python3 powerschool_to_ics.py
