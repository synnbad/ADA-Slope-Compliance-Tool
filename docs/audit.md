# Audit Report

## Repo Structure & Clarity
- **Findings:** 
  - Good: Clean separation between UI (`app.py`), utilities (`processing_utils.py`), and tests
  - Good: Organized data/ and scripts/ folders
  - Issue: Mixed approaches - both Streamlit app and separate processing utils
  - Issue: No clear API structure for headless operation
  - Issue: Dependencies not pinned with exact versions
  - Issue: No type hints on most functions

- **Actions:** 
  - Refactor into proper FastAPI backend with Pydantic models
  - Pin all dependencies to exact versions
  - Add comprehensive type hints
  - Separate processing logic from UI concerns

## Core Logic & Correctness
- **DEM handling:**
  - Current: Uses rasterio.open() directly on file paths
  - Issue: No in-memory processing capability for API uploads
  - Issue: No robust nodata handling - assumes nodata exists and uses hardcoded -9999 fallback
  - Action: Implement MemoryFile-based processing with proper nodata masking

- **Slope computation:**
  - Current: Point-to-point slope calculation between consecutive resampled points
  - Issue: Not true DEM slope computation - missing pixel-based gradient analysis
  - Issue: No consideration of pixel spacing in slope calculation
  - Issue: Only considers running slope, missing cross-slope analysis
  - Action: Implement proper np.gradient-based slope with pixel spacing consideration

- **Threshold interpretation:**
  - Current: Hardcoded 5% threshold (0.05)
  - Good: Correct ADA running slope threshold
  - Missing: Cross-slope threshold (~2.083% for 1:48)
  - Action: Add parameterized thresholds with proper defaults

- **NaN/nodata handling:**
  - Current: Basic None checks, hardcoded -9999 fallback
  - Issue: No systematic masking of invalid values
  - Action: Implement robust np.isfinite() masking

- **Precision:**
  - Current: Rounds to 4 decimal places
  - Good: Reasonable precision for display
  - Action: Maintain precision but ensure consistent units (percentage)

## Performance & Scalability
- **File sizes:**
  - Current: No size limits mentioned
  - Risk: Lambda has 512MB memory limit and 15-minute timeout
  - Action: Add reasonable file size validation and document limits

- **Time/memory:**
  - Current: Synchronous processing in Streamlit
  - Risk: Large DEMs could exceed Lambda constraints
  - Action: Optimize for Lambda constraints, consider async for larger files

## Security & Licensing
- **Dependencies:**
  - Issue: Unpinned versions in requirements.txt
  - Issue: No security scanning
  - Action: Pin exact versions, add security considerations

- **Secrets:**
  - Good: No hardcoded secrets found
  - Action: Ensure AWS credentials use IAM roles/OIDC

- **Dataset licensing:**
  - Issue: No documentation of data provenance in data/ folder
  - Action: Add data/README.md with licensing information

## Testing Status
- **Gaps:**
  - Current tests cover basic functionality but lack comprehensive edge cases
  - No API endpoint testing
  - No synthetic DEM generation for consistent testing
  - No property-based testing for mathematical correctness
  - Coverage unknown

- **Actions:**
  - Add synthetic DEM generation utilities
  - Add FastAPI endpoint tests
  - Add property-based tests with hypothesis
  - Target 80% coverage on processing module

## Improvement Plan (Pre-AWS)
1. **Refactor core processing** - Implement proper DEM-based slope computation using np.gradient with pixel spacing, robust nodata handling via rasterio MemoryFile
2. **Add proper typing** - Convert to typed functions with Pydantic models for API responses  
3. **Implement comprehensive testing** - Synthetic DEM generation, API tests, property-based testing for mathematical correctness
4. **Pin dependencies** - Lock all versions for reproducible builds
5. **Add cross-slope analysis** - Implement both running and cross-slope thresholds with proper parameterization
6. **Create API structure** - Replace Streamlit with FastAPI + Mangum for Lambda deployment

## Summary
- **Decision:** Proceed with MVP after implementing the above improvements.
- **Primary concerns:** Current implementation is path-point based rather than true DEM analysis, lacks API structure, and has gaps in testing/typing.
- **Expected impact:** These improvements will create a robust, testable foundation suitable for AWS Lambda deployment with proper DEM processing capabilities.
