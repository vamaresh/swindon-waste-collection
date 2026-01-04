# Swindon Waste Collection Checker - Fresh Build

A modern, standalone web application for checking waste collection schedules in Swindon Borough Council.

## 🎨 Features

- **Clean, Modern UI**: Beautiful purple gradient design with smooth animations
- **3-Step Process**: 
  1. Enter postcode
  2. Select address from dropdown
  3. View bin collection schedule
- **Zero Frontend Dependencies**: Pure HTML, CSS, and Vanilla JavaScript
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Shows days until collection with special badges for "Today" and "Tomorrow"

## 🏗️ Architecture

### Frontend
- **File**: `index.html` (standalone HTML file)
- **Tech**: Pure HTML5, CSS3, Vanilla JavaScript
- **No Build Step**: Works directly in browser

### Backend (Python Serverless Functions)
- **Platform**: Vercel Serverless Functions
- **Language**: Python 3
- **Endpoints**:
  - `POST /api/uprn-lookup` - Convert postcode to addresses
  - `GET /api/collections/{uprn}` - Get collection schedule

### Data Source
- Scrapes **Swindon Borough Council** website
- URL: `https://www.swindon.gov.uk/info/20122/rubbish_and_recycling_collection_days`
- Uses **iShare Maps** GIS system for address lookup
- Parses collection dates from HTML

## 📦 Setup & Installation

### Prerequisites
```bash
# Node.js (for Vercel CLI)
node >= 18.x

# Python
python >= 3.9
```

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd swindon-waste-collection
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node dependencies (for Vercel CLI)**
```bash
npm install
```

4. **Install Vercel CLI**
```bash
npm install -g vercel
```

5. **Run locally**
```bash
vercel dev
```

6. **Open browser**
```
http://localhost:3000
```

### Testing Backend

Test the Python scrapers directly:
```bash
# Test UPRN lookup
python3 test_backend.py "SN1 1JJ"

# Debug website structure
python3 debug_website.py
```

## 🚀 Deployment to Vercel

### First Time Deployment

1. **Login to Vercel**
```bash
vercel login
```

2. **Deploy**
```bash
vercel --prod
```

3. **Follow prompts** to link to your Vercel project

### Subsequent Deployments

```bash
# Deploy to production
vercel --prod

# Or just push to GitHub if connected
git push origin main
```

### Configure Vercel

The `vercel.json` file is already configured:
- Routes API requests to Python functions
- Serves static HTML from root
- Handles rewrites properly

## 🐛 Debugging

### Enable Debug Logs

All Python files now include comprehensive `print()` statements:
- `[UPRN LOOKUP]` - Address lookup logs
- `[COLLECTIONS]` - Collection scraping logs  
- `[SCRAPER]` - HTML parsing logs

### View Logs

**Local (Vercel Dev)**:
```bash
vercel dev --debug
```

**Production (Vercel)**:
```bash
vercel logs
```

Or view in Vercel Dashboard: https://vercel.com/dashboard

### Common Issues

**"No addresses found"**
- The iShare Maps API might be rate-limiting
- Try a different Swindon postcode (SN1, SN2, SN3, SN25, SN26)
- Check logs for specific error messages

**"Collection data not loading"**
- Website structure may have changed
- Check `debug_website.py` output
- Verify UPRN format is correct (10-12 digits)

**CORS Errors**
- Should not occur with Vercel deployment
- Backend proxies all requests

## 📂 Project Structure

```
swindon-waste-collection/
├── index.html              # Main frontend (standalone)
├── standalone.html         # Same as index.html (backup)
├── vercel.json            # Vercel configuration
├── package.json           # Node dependencies
├── requirements.txt       # Python dependencies
├── api/
│   ├── collections.py     # GET /api/collections/{uprn}
│   ├── uprn-lookup.py     # POST /api/uprn-lookup
│   ├── health.py          # GET /api/health (healthcheck)
│   └── services/
│       ├── swindon_scraper.py    # Collection scraper
│       └── uprn_lookup.py         # Address lookup service
├── test_backend.py        # Backend testing script
├── debug_website.py       # Website structure inspector
└── test_direct.py         # iShare API tester
```

## 🎯 API Documentation

### POST /api/uprn-lookup

**Request:**
```json
{
  "postcode": "SN1 1JJ"
}
```

**Response:**
```json
{
  "addresses": [
    {
      "uprn": "100120123456",
      "address": "1 HIGH STREET, SWINDON, SN1 1JJ"
    }
  ],
  "postcode": "SN1 1JJ",
  "count": 1
}
```

### GET /api/collections/{uprn}

**Request:**
```
GET /api/collections/100120123456
```

**Response:**
```json
{
  "collections": [
    {
      "date": "2026-01-10",
      "type": "Rubbish bin",
      "icon": "trash-can",
      "color": "rubbish",
      "days_until": 6
    },
    {
      "date": "2026-01-10",
      "type": "Recycling boxes",
      "icon": "recycle",
      "color": "recycling",
      "days_until": 6
    }
  ],
  "uprn": "100120123456"
}
```

## 🔧 Tech Stack

**Frontend:**
- HTML5
- CSS3 (with gradients, animations, flexbox, grid)
- Vanilla JavaScript (ES6+)
- Fetch API

**Backend:**
- Python 3.12
- Requests (HTTP client)
- BeautifulSoup4 (HTML parsing)
- Vercel Serverless Functions

**Deployment:**
- Vercel (hosting + serverless)
- GitHub (version control)

## 📝 Known Limitations

1. **iShare API**: The Swindon council uses a third-party GIS system that may have rate limiting or access restrictions
2. **Scraping**: Website structure changes will break the scraper
3. **No Caching**: Each request hits the Swindon website (could add Redis/caching layer)
4. **No Authentication**: Public API, anyone can query

## 🎨 UI Color Scheme

- **Primary Gradient**: Purple (`#667eea` to `#764ba2`)
- **Rubbish**: Dark gray (`#4a5568`)
- **Recycling**: Green (`#48bb78`)
- **Garden**: Orange (`#ed8936`)
- **Plastics**: Blue (`#4299e1`)

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your needs!

## 📄 License

See LICENSE file

## 🙏 Credits

- Swindon Borough Council for data source
- iShare Maps (Astun Technology) for GIS system
- Original scraper logic inspired by [waste_collection_schedule](https://github.com/mampfes/hacs_waste_collection_schedule)

## 📞 Support

For issues or questions:
1. Check the debug logs
2. Run test scripts
3. Verify postcode is in Swindon area
4. Check Vercel deployment logs

---

**Last Updated**: January 4, 2026  
**Status**: ⚠️ In Development - Address lookup needs fixing
