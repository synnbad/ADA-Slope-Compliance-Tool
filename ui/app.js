class ADAComplianceTool {
    constructor() {
        this.map = null;
        this.currentLayer = null;
        this.initializeEventListeners();
        this.initializeFileHandlers();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('analysisForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runAnalysis();
        });

        // Path file change handler
        document.getElementById('pathsFile').addEventListener('change', (e) => {
            const bboxSection = document.getElementById('bboxSection');
            if (e.target.files.length > 0) {
                bboxSection.style.display = 'none';
            } else {
                bboxSection.style.display = 'block';
            }
        });
    }

    initializeFileHandlers() {
        // DEM file handler
        const demUpload = document.getElementById('demUpload');
        const demFile = document.getElementById('demFile');
        
        demFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                demUpload.classList.add('has-file');
                demUpload.querySelector('span').textContent = e.target.files[0].name;
            } else {
                demUpload.classList.remove('has-file');
                demUpload.querySelector('span').textContent = 'Choose DEM file (.tif, .tiff)';
            }
        });

        // Paths file handler
        const pathsUpload = document.getElementById('pathsUpload');
        const pathsFile = document.getElementById('pathsFile');
        
        pathsFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                pathsUpload.classList.add('has-file');
                pathsUpload.querySelector('span').textContent = e.target.files[0].name;
            } else {
                pathsUpload.classList.remove('has-file');
                pathsUpload.querySelector('span').textContent = 'Choose paths file (.geojson)';
            }
        });
    }

    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('statusMessage');
        statusEl.className = `status-message status-${type}`;
        statusEl.textContent = message;
        statusEl.style.display = 'block';
    }

    hideStatus() {
        document.getElementById('statusMessage').style.display = 'none';
    }

    updateProgress(percentage, message = '') {
        const container = document.getElementById('progressContainer');
        const fill = document.getElementById('progressFill');
        
        container.style.display = 'block';
        fill.style.width = percentage + '%';
        
        if (message) {
            this.showStatus(message, 'info');
        }
    }

    hideProgress() {
        document.getElementById('progressContainer').style.display = 'none';
    }

    async runAnalysis() {
        try {
            this.hideStatus();
            this.updateProgress(0, 'Starting analysis...');

            // Validate inputs
            const demFile = document.getElementById('demFile').files[0];
            if (!demFile) {
                throw new Error('Please select a DEM file');
            }

            const pathsFile = document.getElementById('pathsFile').files[0];
            const bbox = this.getBoundingBox();

            if (!pathsFile && !bbox) {
                throw new Error('Please provide either a paths file or bounding box coordinates');
            }

            // Prepare form data
            const formData = new FormData();
            formData.append('dem', demFile);
            
            if (pathsFile) {
                formData.append('paths', pathsFile);
            }

            // Add parameters
            const params = this.getAnalysisParameters();
            formData.append('running_threshold', params.runningThreshold);
            formData.append('cross_threshold', params.crossThreshold);
            formData.append('interval_m', params.intervalM);
            
            if (bbox) {
                formData.append('bbox', bbox.join(','));
            }

            this.updateProgress(20, 'Uploading files and processing...');

            // Call backend API
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error');
            }

            this.updateProgress(80, 'Processing results...');
            const result = await response.json();

            if (result.error) {
                throw new Error(result.error);
            }

            // Display results
            this.updateProgress(90, 'Preparing visualization...');
            await this.displayResults(result.result);

            this.updateProgress(100, 'Analysis complete!');
            setTimeout(() => {
                this.hideProgress();
                this.showStatus('Analysis completed successfully!', 'success');
            }, 1000);

        } catch (error) {
            this.hideProgress();
            this.showStatus(`Error: ${error.message}`, 'error');
            console.error('Analysis error:', error);
        }
    }

    getBoundingBox() {
        const minLon = parseFloat(document.getElementById('minLon').value);
        const minLat = parseFloat(document.getElementById('minLat').value);
        const maxLon = parseFloat(document.getElementById('maxLon').value);
        const maxLat = parseFloat(document.getElementById('maxLat').value);

        if (minLon && minLat && maxLon && maxLat) {
            return [minLon, minLat, maxLon, maxLat];
        }
        return null;
    }

    getAnalysisParameters() {
        return {
            runningThreshold: parseFloat(document.getElementById('runningThreshold').value),
            crossThreshold: parseFloat(document.getElementById('crossThreshold').value),
            intervalM: parseFloat(document.getElementById('intervalM').value)
        };
    }

    async processPathsFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const geojson = JSON.parse(e.target.result);
                    resolve(geojson);
                } catch (error) {
                    reject(new Error('Invalid GeoJSON file'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read paths file'));
            reader.readAsText(file);
        });
    }

    async fetchOSMPaths(bbox) {
        // Simulate OSM API call
        // In real implementation, this would call the backend or use UrbanAccess
        await this.sleep(2000);
        
        // Generate sample data for demonstration
        return this.generateSamplePaths(bbox);
    }

    generateSamplePaths(bbox) {
        const [minLon, minLat, maxLon, maxLat] = bbox;
        const centerLon = (minLon + maxLon) / 2;
        const centerLat = (minLat + maxLat) / 2;
        
        return {
            type: 'FeatureCollection',
            features: [
                {
                    type: 'Feature',
                    properties: { name: 'Sample Path 1' },
                    geometry: {
                        type: 'LineString',
                        coordinates: [
                            [minLon + 0.001, minLat + 0.001],
                            [centerLon, centerLat],
                            [maxLon - 0.001, maxLat - 0.001]
                        ]
                    }
                },
                {
                    type: 'Feature',
                    properties: { name: 'Sample Path 2' },
                    geometry: {
                        type: 'LineString',
                        coordinates: [
                            [minLon + 0.002, maxLat - 0.001],
                            [centerLon, centerLat],
                            [maxLon - 0.002, minLat + 0.001]
                        ]
                    }
                }
            ]
        };
    }

    async computeSlopes(demFile, pathsData, params) {
        // Simulate slope computation
        // In real implementation, this would call the Python backend
        await this.sleep(2000);

        // Add compliance analysis to each feature
        return {
            ...pathsData,
            features: pathsData.features.map((feature, index) => ({
                ...feature,
                properties: {
                    ...feature.properties,
                    running_max: Math.random() * 8 + 1, // 1-9%
                    cross_max: Math.random() * 4 + 0.5, // 0.5-4.5%
                    running_ok: Math.random() > 0.3, // 70% compliant
                    cross_ok: Math.random() > 0.2, // 80% compliant
                }
            }))
        };
    }

    async displayResults(results) {
        this.hideWelcomeScreen();
        this.initializeMap();
        
        if (results.geojson) {
            this.addResultsToMap(results.geojson);
            this.updateResultsStats(results.geojson, results.summary);
        } else {
            // Handle legacy format
            this.addResultsToMap(results);
            this.updateResultsStats(results);
        }
    }

    hideWelcomeScreen() {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('mapContainer').style.display = 'block';
    }

    initializeMap() {
        if (this.map) {
            this.map.remove();
        }

        this.map = L.map('map').setView([39.8283, -98.5795], 4); // Center of US
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    addResultsToMap(geojson) {
        if (this.currentLayer) {
            this.map.removeLayer(this.currentLayer);
        }

        this.currentLayer = L.geoJSON(geojson, {
            style: (feature) => {
                const props = feature.properties;
                const isCompliant = props.running_ok && props.cross_ok;
                
                return {
                    color: isCompliant ? '#28a745' : '#dc3545',
                    weight: 4,
                    opacity: 0.8
                };
            },
            onEachFeature: (feature, layer) => {
                const props = feature.properties;
                const popupContent = `
                    <div style="font-size: 14px; line-height: 1.4;">
                        <strong>${props.name || 'Path'}</strong><br>
                        <strong>Running Slope:</strong> ${props.running_max?.toFixed(2) || 'N/A'}%<br>
                        <strong>Cross Slope:</strong> ${props.cross_max?.toFixed(2) || 'N/A'}%<br>
                        <strong>Status:</strong> 
                        <span style="color: ${props.running_ok && props.cross_ok ? '#28a745' : '#dc3545'}">
                            ${props.running_ok && props.cross_ok ? 'Compliant' : 'Non-compliant'}
                        </span>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        }).addTo(this.map);

        // Fit map to results
        if (geojson.features.length > 0) {
            this.map.fitBounds(this.currentLayer.getBounds(), { padding: [20, 20] });
        }
    }

    updateResultsStats(geojson, summary = null) {
        let stats;
        
        if (summary) {
            // Use provided summary
            stats = {
                total: summary.total_paths,
                compliant: summary.compliant_paths,
                nonCompliant: summary.non_compliant_paths,
                complianceRate: summary.compliance_rate.toFixed(1)
            };
        } else {
            // Calculate from geojson
            const total = geojson.features.length;
            const compliant = geojson.features.filter(f => 
                f.properties.running_ok && f.properties.cross_ok
            ).length;
            const nonCompliant = total - compliant;
            const complianceRate = total > 0 ? ((compliant / total) * 100).toFixed(1) : 0;
            
            stats = { total, compliant, nonCompliant, complianceRate };
        }

        const statsEl = document.getElementById('resultsStats');
        statsEl.innerHTML = `
            <div style="font-size: 13px; color: #495057;">
                <div style="margin-bottom: 5px;"><strong>Total Paths:</strong> ${stats.total}</div>
                <div style="margin-bottom: 5px; color: #28a745;"><strong>Compliant:</strong> ${stats.compliant}</div>
                <div style="margin-bottom: 5px; color: #dc3545;"><strong>Non-compliant:</strong> ${stats.nonCompliant}</div>
                <div style="margin-bottom: 10px;"><strong>Compliance Rate:</strong> ${stats.complianceRate}%</div>
            </div>
        `;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new ADAComplianceTool();
});
