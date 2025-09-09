# ADA Slope Compliance Tool - User Interface

Modern web interface for the ADA Slope Compliance Tool with drag-and-drop file uploads, interactive maps, and real-time analysis.

## Features

- **Modern Web UI**: Clean, responsive interface with drag-and-drop file uploads
- **Interactive Maps**: Leaflet-based map visualization with compliance color coding
- **Real-time Analysis**: Progress tracking with detailed status messages
- **Flexible Input**: Support for DEM + paths files OR DEM + bounding box (OSM fetch)
- **Professional Results**: Detailed compliance statistics and interactive path details

## Quick Start

1. **Navigate to UI directory:**
   ```bash
   cd ui/
   ```

2. **Start the application:**
   ```bash
   python start.py
   ```

3. **Open browser:**
   - Navigate to: http://localhost:5000
   - The UI will automatically open

## Usage

### Step 1: Upload DEM
- Click "Choose DEM file" and select your GeoTIFF
- **Important**: DEM must be in projected coordinate system (meters)
- Use QGIS or gdalwarp to reproject if needed

### Step 2: Provide Paths
**Option A - Upload Paths File:**
- Click "Choose paths file" and select GeoJSON file
- Paths will be analyzed against the DEM

**Option B - Fetch from OSM:**
- Leave paths file empty
- Enter bounding box coordinates (longitude/latitude)
- Tool will fetch pedestrian paths from OpenStreetMap

### Step 3: Configure Parameters
- **Running Slope Threshold**: Maximum allowed running slope (default: 5.0%)
- **Cross Slope Threshold**: Maximum allowed cross slope (default: 2.083%)
- **Sampling Interval**: Distance between analysis points (default: 2.0m)

### Step 4: Run Analysis
- Click "Run Analysis"
- Progress bar shows processing status
- Results appear on interactive map

## Results Interpretation

### Map Visualization
- **Green paths**: Compliant with both running and cross slope requirements
- **Red paths**: Non-compliant (exceeds one or both thresholds)
- Click paths for detailed compliance information

### Statistics Panel
- **Total Paths**: Number of analyzed path segments
- **Compliant**: Paths meeting both slope requirements
- **Non-compliant**: Paths exceeding thresholds
- **Compliance Rate**: Percentage of compliant paths

## Technical Architecture

### Frontend
- **HTML5/CSS3/JavaScript**: Modern responsive design
- **Leaflet**: Interactive mapping library
- **Font Awesome**: Professional icons
- **Real-time updates**: Progress tracking and status messages

### Backend API
- **Flask**: Python web framework
- **File handling**: Secure temporary file management
- **Pipeline integration**: Calls existing scripts (`fetch_paths.py`, `eval_ada.py`)
- **Error handling**: Professional error messages with technical details

### Data Flow
1. **Upload**: Files stored in `temp_uploads/`
2. **Processing**: Backend calls lean pipeline scripts
3. **Results**: Generated GeoJSON stored in `temp_outputs/`
4. **Visualization**: Frontend renders interactive map

## API Endpoints

### `POST /api/upload`
Upload files and run analysis
- **Body**: FormData with DEM file, optional paths file, parameters
- **Returns**: Analysis results with GeoJSON and summary statistics

### `GET /api/results/{job_id}`
Retrieve analysis results
- **Returns**: GeoJSON feature collection with compliance data

### `GET /api/health`
Health check endpoint
- **Returns**: Service status

## Development

### Running in Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python server.py
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## File Structure
```
ui/
├── index.html          # Main UI interface
├── app.js             # Frontend JavaScript application
├── server.py          # Flask backend API
├── start.py           # Startup launcher script
├── requirements.txt   # Python dependencies
├── temp_uploads/      # Temporary file uploads
└── temp_outputs/      # Analysis results
```

## Error Handling

### Common Issues

**"DEM must be in projected coordinate system"**
- Solution: Reproject DEM using QGIS or gdalwarp
- Example: `gdalwarp -t_srs EPSG:32617 input.tif output_utm.tif`

**"No pedestrian edges found"**  
- Solution: Try larger bounding box or different location
- Ensure area has mapped pedestrian infrastructure in OSM

**"Invalid GeoJSON file"**
- Solution: Validate GeoJSON format and ensure LineString geometries
- Use QGIS to export proper GeoJSON format

### Professional Error Messages
- Clear, actionable error descriptions
- Technical details available for debugging
- Guidance for common resolution steps

## Requirements

### System Requirements
- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Minimum 1GB RAM for processing
- Network access for OSM data fetching

### DEM Requirements  
- **Format**: GeoTIFF (.tif, .tiff)
- **Coordinate System**: Projected (meters) - UTM recommended
- **Resolution**: 1-30 meter resolution recommended
- **Size**: Reasonable file size for web upload (< 100MB recommended)

## Integration

The UI seamlessly integrates with the existing lean pipeline:
- **fetch_paths.py**: OSM data retrieval
- **eval_ada.py**: Core slope analysis engine
- **Existing data**: Works with processed FSU campus data

All analysis is performed by the proven Python backend with professional web interface overlay.
