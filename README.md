# Dataset Download Tracker

Track monthly downloads for Canada's protected areas, critical habitat, and wetlands datasets from the Open Government Analytics platform.

## What This App Does

This app automatically tracks monthly download statistics for three Government of Canada datasets:

1. **CPCAD** (Canadian Protected and Conserved Areas Database)
2. **Critical Habitat** for Species at Risk National Dataset
3. **CNWI** (Canadian National Wetlands Inventory)

It pulls data from the [Open Government Analytics dataset](https://open.canada.ca/data/en/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412) and displays trends over time.

## Features

✅ **Dashboard** — View all three datasets in one place  
✅ **Monthly trends** — Line charts showing download counts over time  
✅ **Automatic refresh** — Click "Refresh Data Now" to pull latest numbers  
✅ **CSV export** — Download your data for reports  
✅ **Notes/annotations** — Add notes for dataset releases or events  
✅ **No login required** — Simple, lightweight desktop app  

## Setup Instructions for Your Desktop

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. **Important**: Check the box "Add Python to PATH" during installation
3. Restart your computer after installing

### Step 2: Clone This Repository

1. Open **Command Prompt** (press `Win + R`, type `cmd`, press Enter)
2. Navigate to where you want the app (e.g., your Desktop):
   ```
   cd Desktop
   ```
3. Clone the repo:
   ```
   git clone https://github.com/srjbridge/dataset-download-tracker.git
   cd dataset-download-tracker
   ```

   **Don't have Git?** Download the repo as a ZIP file from GitHub, extract it, and open Command Prompt in that folder.

### Step 3: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Fix the Static Folder (One-Time Setup)

Due to how the files were uploaded, you need to move the `static` folder to the correct location:

1. In File Explorer, navigate to `dataset-download-tracker/templates/static/`
2. **Cut** the `static` folder
3. **Paste** it directly in `dataset-download-tracker/` (same level as `app.py`)

The structure should look like:
```
dataset-download-tracker/
  ├── app.py
  ├── requirements.txt
  ├── templates/
  │   └── index.html
  └── static/
      └── style.css
```

### Step 6: Run the App

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### Step 7: Open in Your Browser

Go to:
```
http://localhost:5000
```

You'll see the dashboard with your three datasets!

## How to Use

### First Time: Load Data

1. Click **"Refresh Data Now"** to download the latest analytics
2. Wait 5-10 seconds for the data to load
3. The dashboard will populate with available months

### View Data

- **Dashboard tab**: See all three datasets on one chart
- **Individual tabs** (CPCAD, Critical Habitat, CNWI): Detailed views
- **Export to CSV**: Download the data table for reports

### Add Notes

*(Feature can be extended in `templates/index.html` if needed)*

## Troubleshooting

### "python not found"

- You didn't check "Add Python to PATH" during installation
- Solution: Reinstall Python and check that box

### "Module not found" error

- Your virtual environment isn't activated
- Solution: Run `venv\Scripts\activate` again
- Or you forgot to run `pip install -r requirements.txt`

### App won't load / blank page

- Make sure you moved the `static` folder to the right place (Step 5)
- Check that `python app.py` is still running (don't close Command Prompt)

### "No data" in dashboard

- Click "Refresh Data Now" to pull data from Open Government Analytics
- If datasets aren't in the Top 100 for a given month, they won't appear

## Stopping the App

- Press `Ctrl + C` in the Command Prompt window
- Or just close the Command Prompt

## Running the App Again Later

1. Open Command Prompt
2. Navigate to the folder:
   ```
   cd Desktop\dataset-download-tracker
   ```
3. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open `http://localhost:5000` in your browser

## Technical Details

- **Backend**: Python 3.8+ with Flask
- **Database**: SQLite (auto-created as `downloads.db`)
- **Frontend**: HTML + JavaScript + Chart.js
- **Data source**: Open Government Analytics Top 100 CSV

## License

MIT License - feel free to modify and use
