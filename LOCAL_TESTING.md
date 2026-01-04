# Swindon Waste Collection - Local Testing Guide

## 🚀 Quick Start

### 1. Clone/Checkout the Code

```bash
git clone https://github.com/vamaresh/swindon-waste-collection.git
cd swindon-waste-collection
```

Or if you already have it:
```bash
cd swindon-waste-collection
git pull origin main
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.9 or higher
- `requests` library
- `beautifulsoup4` library

### 3. Run the Local Server

```bash
python3 run_local.py
```

**You should see:**
```
============================================================
🚀 Swindon Waste Collection - Local Development Server
============================================================

✓ Server running at: http://localhost:8000
✓ API endpoint: http://localhost:8000/api/uprn-lookup
✓ Collections: http://localhost:8000/api/collections/{uprn}

📝 Test with a Swindon postcode (e.g., SN3 4PG, SN1 1JJ)

⏹  Press Ctrl+C to stop the server
============================================================
```

### 4. Open Your Browser

Navigate to: **http://localhost:8000**

### 5. Test the Application

1. **Enter a Swindon postcode**: `SN3 4PG` or `SN1 1JJ`
2. **Click "Find Addresses"**
3. **Select an address** from the dropdown
4. **View your bin collection schedule!**

---

## 🧪 Testing Different Postcodes

Try these Swindon postcodes:
- `SN1 1JJ` - Swindon town center
- `SN2 1DY` - Gorse Hill area
- `SN3 4PG` - Stratton St Margaret
- `SN25 4AN` - North Swindon

---

## 🔧 Troubleshooting

### Port Already in Use

If port 8000 is already in use, edit `run_local.py` and change:
```python
port = 8000  # Change to 8080 or 3000
```

### Module Not Found

Make sure you're in the correct directory:
```bash
pwd  # Should show .../swindon-waste-collection
```

Install dependencies again:
```bash
pip install --upgrade -r requirements.txt
```

### No Addresses Found

- Make sure you're using a **Swindon postcode** (SN1-SN6, SN25, SN26)
- Check your internet connection
- The Swindon website might be temporarily down

---

## 📋 What to Check

✅ **Frontend**: Modern purple gradient UI loads  
✅ **Postcode Lookup**: Returns list of addresses  
✅ **Address Selection**: Dropdown populated  
✅ **Collections Display**: Colorful cards with bin dates  
✅ **Responsive**: Works on mobile screen sizes  

---

## 🐛 Debug Mode

Watch the terminal output for detailed logs:
```
[LOCAL SERVER] Looking up postcode: SN3 4PG
[UPRN LOOKUP SERVICE] Searching for: SN3 4PG
[UPRN LOOKUP SERVICE] Status: 200
[UPRN LOOKUP SERVICE] Found 49 results
```

---

## 📁 Project Structure

```
swindon-waste-collection/
├── index.html              # Main frontend
├── run_local.py           # Local development server (NEW!)
├── requirements.txt       # Python dependencies
├── api/
│   ├── uprn-lookup.py     # UPRN lookup handler
│   ├── waste_collections.py  # Collections handler
│   └── services/
│       ├── uprn_lookup.py     # UPRN service
│       └── swindon_scraper.py # Collections scraper
└── test_backend.py        # Backend testing script
```

---

## 🌐 Deployment

Once tested locally and working:

```bash
# Deploy to Vercel (after fixing project settings)
vercel --prod
```

---

## 💡 Tips

- **Browser Console**: Press F12 to see frontend debug logs
- **Terminal**: Watch for `[LOCAL SERVER]` logs
- **Network Tab**: Check API requests/responses
- **Test Multiple Postcodes**: Verify different areas work

---

**Happy Testing! 🎉**
