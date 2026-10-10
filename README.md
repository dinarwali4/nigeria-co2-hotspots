# Nigeria CO₂ Hotspots

Where Nigeria's fossil carbon dioxide comes from, located with emission inventories and checked from orbit and in Google Earth, 2000–2026.

**Live site:** https://dinarwali4.github.io/nigeria-co2-hotspots/
· [Presentation (44 slides)](https://dinarwali4.github.io/nigeria-co2-hotspots/deck/)
· [Google Earth atlas](https://dinarwali4.github.io/nigeria-co2-hotspots/atlas/)

Prepared by **Dinar Wali** · RegenX · October 2026

## Key findings

- Nigeria emitted **137.6 Mt** of fossil CO₂ in 2025 (EDGAR), **+58%** since 2005. Half of it comes from **0.57%** of the land (4,425 km²).
- **Largest clusters:** Lagos metro 12.2 Mt, Port Harcourt–Onne–Eleme 9.3 Mt, Obajana Cement 6.1 Mt, Bonny Island LNG 5.4 Mt.
- **Cement is the main growth story.** Six works are on the list (Obajana, Okpotu, Ibese, Sokoto, Gboko, Mfamosing); none existed in 2000–02 imagery.
- **The Dangote refinery** (2.65 Mt in 2024, Climate TRACE) went from forest in 2013 to a complete refinery in 2024. It is not yet in EDGAR's 1 km grid. EDGAR also misses BUA Okpotu and BUA Sokoto cement.
- **EDGAR misplaces Niger Delta oil-and-gas emissions** in coarse 0.1° blocks. MODIS fire persistence (fire on ≥60 of 730 days) locates the actual flare sites.
- **One inventory hotspot is false:** a 0.69 Mt single-pixel point in southern Kaduna is farmland, with background NO₂ and no listed facility.

## What's in the repo

| Path | Contents |
|---|---|
| `index.html` | The full report (home page of the site) |
| `deck/` | 44-slide presentation viewer, slide images and speaker notes |
| `atlas/` | Annotated Google Earth Pro imagery: latest, historical (~2013) and then-vs-now panels |
| `downloads/` | Deck PDF and PPTX, Google Earth atlas PDF, `Nigeria_CO2_Hotspots.kmz`, `hotspots.csv` |
| `data/` | Hotspot results, satellite statistics, flare pixels, Climate TRACE facilities, view and label definitions |
| `scripts/analysis/` | Earth Engine and Python analysis: hotspot detection, NO₂ and flare checks, imagery, maps, KMZ, report |
| `scripts/google_earth/` | Google Earth Pro camera control, settled-frame capture and annotation |
| `scripts/presentation/` | Slide sources and the HTML → PNG → PDF/PPTX render |

## Method

1. **Locate:** EDGAR 2025 1 km fossil-CO₂ grid for 2024, clustered above 3,300 t/km²/yr (the threshold above which pixels hold half the national total). 0.1° grids for 2005, 2015 and 2025 give trends.
2. **Attribute:** Climate TRACE v6 facility estimates for 2024 (259 point sources in Nigeria).
3. **Flares:** MODIS (FIRMS) pixels with fire on ≥60 of 730 days, 2014–15 and 2024–25.
4. **Verify:** Sentinel-5P tropospheric NO₂ (2019 vs 2025, against the national median), Landsat 7 and Sentinel-2 imagery, Google AlphaEarth satellite embeddings (k-means clustering and 2017→2024 change), and Google Earth Pro historical imagery.

**Limits.** No satellite yet measures CO₂ itself at plant scale over Nigeria, so each hotspot is an inventory figure confirmed with NO₂. Flare detection counts are not flared volumes. Land-use and fire CO₂ are outside this fossil-fuel analysis.

## Reproducing

The analysis scripts need the Earth Engine Python API with your own Cloud project: `export GOOGLE_CLOUD_PROJECT=<your-project>`. EDGAR grids are downloaded from the EU JRC site (the 1 km file is 1.1 GB and is not in this repo). The Google Earth scripts drive Google Earth Pro on macOS; set `EARTH_WINDOW_ID` to Earth's window ID before capturing.

## Data sources and credits

- EDGAR 2025/2026 GHG, European Commission JRC (CC BY 4.0)
- Climate TRACE v6 (CC BY 4.0)
- Copernicus Sentinel-2 and Sentinel-5P (Copernicus licence)
- Landsat 7, USGS
- NASA FIRMS / MODIS active fire
- Google Satellite Embedding (AlphaEarth), Google Earth Engine
- Google Earth Pro imagery: © Airbus, Maxar Technologies, CNES, Landsat/Copernicus, as credited on each image

## Licence

Code is MIT-licensed (see `LICENSE`). Text, maps, charts and annotations are © 2026 Dinar Wali, licensed CC BY 4.0. Satellite and Google Earth imagery remains © its respective providers and is shown with attribution; it is not covered by these licences.
