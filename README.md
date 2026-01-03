# Swindon Waste Collection 🗑️♻️

A modern Progressive Web App (PWA) for checking waste collection schedules in Swindon Borough Council area.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/vamaresh/swindon-waste-collection)

## ✨ Features

- **📍 Postcode Search**: Enter your Swindon postcode to find your address
- **🏠 Address Selection**: Choose from multiple addresses if needed
- **📅 Collection Schedule**: View all upcoming waste collection dates
- **⏱️ Countdown**: See days until next collection
- **🎨 Color-Coded**: Different colors for each waste type
  - 🖤 Rubbish bin (Black)
  - 💙 Recycling boxes (Blue)
  - 💚 Garden waste bin (Green)
  - 💛 Plastics (Yellow)
- **📱 Progressive Web App**: Install on your phone like a native app
- **⚡ Fast & Responsive**: Built with React + Vite + Tailwind CSS
- **💾 Offline Support**: Cached data available offline
- **🔒 Privacy-Focused**: No tracking, no cookies, no personal data stored

## 🖼️ Screenshots

[Screenshots will be added after deployment]

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Vercel account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/vamaresh/swindon-waste-collection.git
   cd swindon-waste-collection
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Start development server**
   ```bash
   # Option 1: Using Vercel CLI (recommended)
   npm install -g vercel
   vercel dev
   
   # Option 2: Using Vite only (frontend only)
   npm run dev
   ```

4. **Open in browser**
   - Navigate to `http://localhost:3000` (Vercel) or `http://localhost:5173` (Vite)

### Environment Variables

Create a `.env` file in the root directory (optional for local development):

```env
VITE_API_URL=http://localhost:3000
```

## 📦 Deployment to Vercel

### Option 1: Deploy with Vercel Button

Click the "Deploy with Vercel" button at the top of this README.

### Option 2: Manual Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   # Deploy to preview
   vercel
   
   # Deploy to production
   vercel --prod
   ```

### Configuration

The `vercel.json` file is already configured with:
- Python 3.9 runtime for serverless functions
- Automatic routing for API endpoints
- SPA fallback routing

## 🏗️ Architecture

### Backend (Python Serverless Functions)

Located in `/api/` directory, deployed as Vercel Serverless Functions:

- **`/api/health`** - Health check endpoint
- **`/api/uprn-lookup`** - POST endpoint for postcode → UPRN lookup
- **`/api/collections/[uprn]`** - GET endpoint for fetching collection schedule

**Implementation:**
- Uses Python's `BaseHTTPRequestHandler` for Vercel serverless compatibility
- Web scraping with BeautifulSoup4 and Requests
- Retry logic with exponential backoff (max 30s delay)
- CORS support for cross-origin requests

**Services:**
- `api/services/swindon_scraper.py` - Web scraper for Swindon Council website
- `api/services/uprn_lookup.py` - Address lookup service

### Frontend (React + TypeScript + Vite)

Located in `/src/` directory:

**Components:**
- `PostcodeForm.tsx` - Postcode input with validation
- `AddressSelector.tsx` - Address dropdown selector
- `CollectionSchedule.tsx` - Collection schedule display
- `CollectionItem.tsx` - Individual collection card
- `LoadingSpinner.tsx` - Loading state component

**Services:**
- `services/api.ts` - API client with axios
- `hooks/useCollections.ts` - Custom React hook for data management

**Styling:**
- Tailwind CSS for utility-first styling
- Custom color scheme for waste types
- Responsive design (mobile-first)

### PWA Configuration

- Service worker for offline support (`public/sw.js`)
- Web app manifest (`public/manifest.json`)
- Installable on mobile devices
- Network-first caching strategy

## 🧪 Testing

### Test with Sample Data

Use these test UPRNs for Swindon addresses:
- `100121147490`
- `200002922415`

### Manual Testing Checklist

- [ ] Enter valid Swindon postcode
- [ ] Select address from dropdown
- [ ] View collection schedule
- [ ] Test on mobile device
- [ ] Test PWA installation
- [ ] Test offline mode
- [ ] Test error handling (invalid postcode)
- [ ] Test responsive design

## 🛠️ Technology Stack

**Frontend:**
- React 18
- TypeScript
- Vite 5
- Tailwind CSS
- Axios
- Lucide React (icons)
- React Hot Toast

**Backend:**
- Python 3.9+
- BeautifulSoup4
- Requests
- Python DateUtil

**Deployment:**
- Vercel (Serverless Functions + Static Hosting)

## 📝 API Documentation

### POST /api/uprn-lookup

Look up addresses for a postcode.

**Request:**
```json
{
  "postcode": "SN1 1XX"
}
```

**Response:**
```json
{
  "addresses": [
    {
      "uprn": "100121147490",
      "address": "1 Nyland Road, SN1 1XX"
    }
  ]
}
```

### GET /api/collections/[uprn]

Get waste collection schedule for a UPRN.

**Response:**
```json
{
  "collections": [
    {
      "date": "2026-01-10",
      "type": "Rubbish bin",
      "icon": "trash-can",
      "days_until": 7
    }
  ],
  "uprn": "100121147490"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-03T20:00:00Z"
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Attribution

This project adapts scraping code from the excellent [hacs_waste_collection_schedule](https://github.com/mampfes/hacs_waste_collection_schedule) project:

- **Original Author**: Steffen Zimmermann
- **Original License**: MIT License (Copyright 2020 Steffen Zimmermann)
- **Original Source**: [swindon_gov_uk.py](https://github.com/mampfes/hacs_waste_collection_schedule/blob/cb495700e56ddc21d1260b4d4af276f877b8d996/custom_components/waste_collection_schedule/waste_collection_schedule/source/swindon_gov_uk.py)

Thank you to Steffen Zimmermann for creating and maintaining the original scraping logic!

## ⚠️ Disclaimer

This is an unofficial application and is not affiliated with, endorsed by, or connected to Swindon Borough Council. Collection dates are sourced from the official Swindon Borough Council website but this application is not guaranteed to be accurate or up-to-date.

Always verify collection dates with the [official Swindon Borough Council website](https://www.swindon.gov.uk/info/20122/rubbish_and_recycling_collection_days).

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact Swindon Borough Council for collection-related queries

## 🗺️ Roadmap

- [ ] Add notifications for upcoming collections
- [ ] Add calendar export (iCal format)
- [ ] Add support for multiple saved addresses
- [ ] Add dark mode
- [ ] Add collection history
- [ ] Add missed collection reporting
- [ ] Add recycling guidelines

---

Made with ♻️ by [vamaresh](https://github.com/vamaresh)