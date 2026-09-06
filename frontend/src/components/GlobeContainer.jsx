import { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const GlobeContainer = ({ spillResult, vessels, onVesselSelect, selectedVessel, playbackProgress }) => {
  const mapRef = useRef(null);
  const containerRef = useRef(null);
  const spillOverlayRef = useRef(null);
  const [styleLoaded, setStyleLoaded] = useState(false);

  useEffect(() => {
    // Initialize maplibre
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: `https://api.maptiler.com/maps/satellite/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`,
      projection: 'globe',
      center: [71.85, 18.95], // Arabian Sea center
      zoom: 4.5, // Tighter focus on Arabian Sea region
      minZoom: 1.5,
      maxZoom: 18,
      antialias: true
    });

    mapRef.current = map;

    // Add navigation controls
    map.addControl(new maplibregl.NavigationControl());

    // Wait for style to fully load before adding sources/layers
    const onStyleLoad = () => {
      // Set up lighting for globe
      map.setLight({
        anchor: 'map',
        position: [1.15, 210, 30]
      });
      setStyleLoaded(true);
    };

    // Register style.load handler
    if (map.isStyleLoaded()) {
      // Style already loaded (e.g., React StrictMode re-mount)
      onStyleLoad();
    } else {
      // Wait for style to load
      map.on('style.load', onStyleLoad);
    }

    // Cleanup
    return () => {
      map.off('style.load', onStyleLoad);
      map.remove();
    };
  }, []);

  // Spill zone DOM overlay - updates position on map move/zoom/rotate
  useEffect(() => {
    const map = mapRef.current;
    const overlay = spillOverlayRef.current;
    if (!map || !styleLoaded || !overlay) return;

    const updateOverlay = () => {
      if (!spillResult || spillResult.detected !== true || !spillResult.center) {
        overlay.style.display = 'none';
        return;
      }

      const { lat, lon } = spillResult.center;
      const centerPoint = map.project([lon, lat]);

      // Calculate screen radius for ~25km at current zoom
      // At zoom level z, 1 degree ≈ 2^(z+8) pixels at equator (Web Mercator)
      // For globe projection, use map.project to get pixel distance
      const radiusKm = 25;
      const radiusDeg = radiusKm / 111; // approximate degrees
      const edgePoint = map.project([lon + radiusDeg / Math.cos(lat * Math.PI / 180), lat]);
      const radiusPx = Math.abs(edgePoint.x - centerPoint.x);

      overlay.style.display = 'block';
      overlay.style.left = `${centerPoint.x - radiusPx}px`;
      overlay.style.top = `${centerPoint.y - radiusPx}px`;
      overlay.style.width = `${radiusPx * 2}px`;
      overlay.style.height = `${radiusPx * 2}px`;
    };

    // Initial position
    updateOverlay();

    // Update on map events
    map.on('move', updateOverlay);
    map.on('zoom', updateOverlay);
    map.on('rotate', updateOverlay);
    map.on('pitch', updateOverlay);
    map.on('resize', updateOverlay);

    return () => {
      map.off('move', updateOverlay);
      map.off('zoom', updateOverlay);
      map.off('rotate', updateOverlay);
      map.off('pitch', updateOverlay);
      map.off('resize', updateOverlay);
      overlay.style.display = 'none';
    };
  }, [spillResult, styleLoaded]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !styleLoaded) return;

    // Remove existing spill layers (keep DOM overlay, remove MapLibre layers)
    // IMPORTANT: Remove dependent layers FIRST, then sources
    if (map.getLayer('spill-label')) {
      map.removeLayer('spill-label');
    }
    if (map.getLayer('spill-zone-glow')) {
      map.removeLayer('spill-zone-glow');
    }
    if (map.getLayer('spill-zone-outline')) {
      map.removeLayer('spill-zone-outline');
    }
    if (map.getLayer('spill-zone-fill')) {
      map.removeLayer('spill-zone-fill');
    }
    if (map.getLayer('spill-center-point')) {
      map.removeLayer('spill-center-point');
    }
    if (map.getLayer('spill-zone')) {
      map.removeLayer('spill-zone');
    }
    if (map.getSource('spill-zone')) {
      map.removeSource('spill-zone');
    }
    if (map.getSource('spill-center')) {
      map.removeSource('spill-center');
    }
    if (map.getLayer('vessels')) {
      map.removeLayer('vessels');
    }
    if (map.getSource('vessels')) {
      map.removeSource('vessels');
    }
    if (map.getLayer('vessel-labels')) {
      map.removeLayer('vessel-labels');
    }
    if (map.getSource('vessel-labels')) {
      map.removeSource('vessel-labels');
    }
    // Remove prototype trajectories
    if (map.getLayer('prototype-trajectories')) {
      map.removeLayer('prototype-trajectories');
    }
    if (map.getSource('prototype-trajectories')) {
      map.removeSource('prototype-trajectories');
    }
    if (map.getLayer('vessel-trajectories')) {
      map.removeLayer('vessel-trajectories');
    }
    if (map.getSource('vessel-trajectories')) {
      map.removeSource('vessel-trajectories');
    }
    // Remove prototype DOM markers from DOM
    document.querySelectorAll('.prototype-vessel-marker').forEach(el => el.remove());

    // Add spill center marker and label ONLY (no MapLibre fill/outline)
    if (spillResult && spillResult.detected === true && spillResult.center) {
      const { lat, lon } = spillResult.center;
      const probability = spillResult.confidence || 0;

      // Add center point marker
      map.addSource('spill-center', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: { probability },
          geometry: {
            type: 'Point',
            coordinates: [lon, lat]
          }
        }
      });

      map.addLayer({
        id: 'spill-center-point',
        type: 'circle',
        source: 'spill-center',
        paint: {
          'circle-radius': 8,
          'circle-color': '#ff8c00',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff',
          'circle-opacity': 1
        }
      });

      // Add label
      map.addLayer({
        id: 'spill-label',
        type: 'symbol',
        source: 'spill-center',
        layout: {
          'text-field': ['concat', 'OIL SPILL: ', ['round', ['*', ['get', 'probability'], 100]], '%'],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 12,
          'text-offset': [0, 1.5],
          'text-anchor': 'top'
        },
        paint: {
          'text-color': '#ffffff',
          'text-halo-width': 1,
          'text-halo-color': '#000000'
        }
      });
    }

    // Add vessels if we have them (backend candidates take priority)
    // Prototype vessels only shown when no backend vessels available
    if (vessels && vessels.length > 0) {
      // Store marker references for later updates (playback)
      const markerRefs = {};

      // Create DOM markers for each backend vessel (same as prototype)
      vessels.forEach((vessel) => {
        const el = document.createElement('div');
        el.className = 'prototype-vessel-marker';
        el.innerHTML = `
          <svg class="ship-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L15 9H22L13 12L21 19L12 16L3 19L11 12L2 9H9L12 2Z" stroke="var(--accent)" stroke-width="1.5" fill="none"/>
          </svg>
          <div class="marker-label">${vessel.name}</div>
        `;

        // Ensure inner elements don't intercept clicks
        el.style.pointerEvents = 'auto';
        el.querySelectorAll('*').forEach(child => {
          child.style.pointerEvents = 'none';
        });

        // Handle click - pass complete backend candidate object
        el.addEventListener('click', (e) => {
          e.stopPropagation();

          const vesselData = {
            ...vessel,
            prototype: false,
            trajectory: vessel.trajectory,
            _marker: markerRefs[vessel.vessel_id || vessel.name]
          };

          onVesselSelect(vesselData);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([vessel.coordinates.lon, vessel.coordinates.lat])
          .addTo(map);

        markerRefs[vessel.vessel_id || vessel.name] = marker;
      });

      // Add trajectory lines for backend vessels
      const trajectoryFeatures = {
        type: 'FeatureCollection',
        features: vessels
          .filter(v => v.trajectory && v.trajectory.length > 0)
          .map(vessel => ({
            type: 'Feature',
            properties: { vesselName: vessel.name },
            geometry: {
              type: 'LineString',
              coordinates: vessel.trajectory
            }
          }))
      };

      if (trajectoryFeatures.features.length > 0) {
        map.addSource('vessel-trajectories', {
          type: 'geojson',
          data: trajectoryFeatures
        });

        map.addLayer({
          id: 'vessel-trajectories',
          type: 'line',
          source: 'vessel-trajectories',
          paint: {
            'line-color': '#4cc9f0',
            'line-width': 1.5,
            'line-opacity': 0.3,
            'line-dasharray': [2, 2]
          }
        });
      }
    } else if (!spillResult || !spillResult.detected) {
      // Only show prototype vessels when no spill detected and no backend vessels
      const prototypeVessels = [
        { name: 'PROTOTYPE-01', lat: 19.1, lon: 71.9 },
        { name: 'PROTOTYPE-02', lat: 18.8, lon: 72.1 },
        { name: 'PROTOTYPE-03', lat: 19.3, lon: 71.5 }
      ];

      // Store marker references for later updates
      const markerRefs = {};

      // Create DOM markers for each prototype vessel
      prototypeVessels.forEach((vessel) => {
        const el = document.createElement('div');
        el.className = 'prototype-vessel-marker';
        el.innerHTML = `
          <svg class="ship-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L15 9H22L13 12L21 19L12 16L3 19L11 12L2 9H9L12 2Z" stroke="var(--accent)" stroke-width="1.5" fill="none"/>
          </svg>
          <div class="marker-label"></div>
        `;

        // Ensure inner elements don't intercept clicks
        el.style.pointerEvents = 'auto';
        el.querySelectorAll('*').forEach(child => {
          child.style.pointerEvents = 'none';
        });

        // Handle click
        el.addEventListener('click', (e) => {
          e.stopPropagation();

          const vesselData = {
            name: vessel.name,
            vessel_id: vessel.name,
            timestamp: new Date().toISOString(),
            coordinates: { lat: vessel.lat, lon: vessel.lon },
            prototype: true,
            attribution_score: 0.85,
            spatial_consistency: 0.78,
            temporal_consistency: 0.92,
            drift_consistency: 0.88,
            _marker: markerRefs[vessel.name]
          };

          onVesselSelect(vesselData);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([vessel.lon, vessel.lat])
          .addTo(map);

        markerRefs[vessel.name] = marker;
      });

      // Add trajectory lines for prototype vessels
      map.addSource('prototype-trajectories', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: [[71.9, 19.1], [72.0, 19.15], [72.1, 19.2]]
              }
            },
            {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: [[72.1, 18.8], [72.0, 18.75], [71.95, 18.7]]
              }
            },
            {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: [[71.5, 19.3], [71.6, 19.25], [71.7, 19.2]]
              }
            }
          ]
        }
      });

      map.addLayer({
        id: 'prototype-trajectories',
        type: 'line',
        source: 'prototype-trajectories',
        paint: {
          'line-color': '#4cc9f0',
          'line-width': 1.5,
          'line-opacity': 0.3,
          'line-dasharray': [2, 2]
        }
      });
    }

    // Cleanup function
    return () => {
      // No rotation cleanup needed
    };
  }, [spillResult, vessels, styleLoaded]);

  // Update selected vessel position based on playback progress
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedVessel || !selectedVessel.prototype || !selectedVessel.trajectory || selectedVessel.trajectory.length === 0) return;

    // Find the DOM marker for the selected vessel by checking stored references
    // We'll store marker references when creating them
    let selectedMarker = null;

    // Look through all prototype vessels to find the matching one
    if (selectedVessel._marker) {
      selectedMarker = selectedVessel._marker;
    } else {
      // Fallback: query DOM (shouldn't be needed if we store references properly)
      const markers = document.querySelectorAll('.prototype-vessel-marker');
      markers.forEach(marker => {
        const label = marker.querySelector('.marker-label');
        if (label && label.textContent === selectedVessel.name) {
          selectedMarker = marker._marker || marker; // Try to get the maplibre marker
        }
      });
    }

    if (!selectedMarker) return;

    const trajectory = selectedVessel.trajectory;
    const progress = Math.min(playbackProgress / 100, 1); // Convert percentage to 0-1

    if (progress < 1 && trajectory.length >= 2) {
      // Interpolate between trajectory points
      const pointIndex = progress * (trajectory.length - 1);
      const lowerIndex = Math.floor(pointIndex);
      const upperIndex = Math.min(lowerIndex + 1, trajectory.length - 1);
      const segmentProgress = pointIndex - lowerIndex;

      const lowerPoint = trajectory[lowerIndex]; // [lon, lat]
      const upperPoint = trajectory[upperIndex]; // [lon, lat]

      const interpolatedLon = lowerPoint[0] + (upperPoint[0] - lowerPoint[0]) * segmentProgress;
      const interpolatedLat = lowerPoint[1] + (upperPoint[1] - lowerPoint[1]) * segmentProgress;

      // Update marker position
      selectedMarker.setLngLat([interpolatedLon, interpolatedLat]);
    } else if (progress >= 1 && trajectory.length > 0) {
      // Animation complete, show at end point
      const endPoint = trajectory[trajectory.length - 1];
      selectedMarker.setLngLat([endPoint[0], endPoint[1]]);
    }
  }, [selectedVessel, playbackProgress]);

  // Handle map click to deselect
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const handleClick = (e) => {
      // Click on map background - could deselect if needed
      // Vessel clicks are handled by DOM marker event listeners
    };

    map.on('click', handleClick);
    return () => {
      map.off('click', handleClick);
    };
  }, [onVesselSelect]);

  return (
    <div ref={containerRef} className="globe-container">
      <div
        ref={spillOverlayRef}
        className="spill-zone-overlay"
        style={{
          position: 'absolute',
          pointerEvents: 'none',
          borderRadius: '50%',
          background: 'radial-gradient(circle at center, rgba(255, 51, 0, 0.35) 0%, rgba(255, 170, 0, 0.15) 50%, transparent 70%)',
          border: '2px solid rgba(255, 0, 0, 0.8)',
          boxShadow: '0 0 20px rgba(255, 100, 0, 0.5), inset 0 0 20px rgba(255, 51, 0, 0.2)',
          display: 'none',
          zIndex: 10,
        }}
      />
    </div>
  );
};

export default GlobeContainer;