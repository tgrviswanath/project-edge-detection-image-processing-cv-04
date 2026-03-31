import React, { useState, useRef, useEffect } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Grid, Select, MenuItem, FormControl, InputLabel,
  Slider, Button, Divider,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import { processImage, getOperations } from "../services/imageApi";

const OP_DESCRIPTIONS = {
  canny:     "Canny edge detection — finds edges using gradient thresholds",
  sobel:     "Sobel operator — detects horizontal + vertical gradients",
  laplacian: "Laplacian — second-order derivative edge detection",
  blur:      "Gaussian blur — smooths image to reduce noise",
  sharpen:   "Unsharp masking — enhances edges and fine details",
  threshold: "Adaptive threshold — binarizes image handling uneven lighting",
  dilate:    "Morphological dilation — expands bright regions",
  erode:     "Morphological erosion — shrinks bright regions",
  contours:  "Contour detection — finds and draws object boundaries",
  grayscale: "Grayscale conversion — removes color information",
};

const OP_PARAMS = {
  canny:     ["threshold1", "threshold2"],
  sobel:     [],
  laplacian: [],
  blur:      ["ksize"],
  sharpen:   ["sigma"],
  threshold: ["block_size", "C"],
  dilate:    ["ksize", "iterations"],
  erode:     ["ksize", "iterations"],
  contours:  ["threshold"],
  grayscale: [],
};

const PARAM_CONFIG = {
  threshold1:  { label: "Threshold 1", min: 0,  max: 300, step: 10,  default: 100 },
  threshold2:  { label: "Threshold 2", min: 0,  max: 500, step: 10,  default: 200 },
  ksize:       { label: "Kernel Size", min: 3,  max: 31,  step: 2,   default: 15  },
  sigma:       { label: "Sigma",       min: 1,  max: 10,  step: 0.5, default: 3   },
  block_size:  { label: "Block Size",  min: 3,  max: 51,  step: 2,   default: 11  },
  C:           { label: "C",           min: 0,  max: 20,  step: 1,   default: 2   },
  iterations:  { label: "Iterations",  min: 1,  max: 10,  step: 1,   default: 1   },
  threshold:   { label: "Threshold",   min: 0,  max: 255, step: 5,   default: 127 },
};

export default function ProcessPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [operation, setOperation] = useState("canny");
  const [params, setParams] = useState({ threshold1: 100, threshold2: 200, ksize: 15, sigma: 3, block_size: 11, C: 2, iterations: 1, threshold: 127 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [operations, setOperations] = useState([]);
  const fileRef = useRef();

  useEffect(() => {
    getOperations().then((r) => setOperations(r.data.operations)).catch(() => {});
  }, []);

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError("");
  };

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("operation", operation);
      Object.entries(params).forEach(([k, v]) => fd.append(k, v));
      const r = await processImage(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Processing failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Drop zone */}
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 2.5, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {file
          ? <Typography color="text.secondary">📷 {file.name} — click to change</Typography>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Drag & drop or click — JPG / PNG / BMP / WEBP</Typography>
            </Box>
        }
      </Paper>

      {/* Controls */}
      <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap", alignItems: "flex-start" }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Operation</InputLabel>
          <Select value={operation} label="Operation"
            onChange={(e) => { setOperation(e.target.value); setResult(null); }}>
            {(operations.length ? operations : Object.keys(OP_DESCRIPTIONS)).map((op) => (
              <MenuItem key={op} value={op}>{op}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button variant="contained" onClick={handleProcess}
          disabled={!file || loading}
          startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <PlayArrowIcon />}>
          {loading ? "Processing…" : "Apply"}
        </Button>
      </Box>

      {/* Operation description */}
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {OP_DESCRIPTIONS[operation]}
      </Typography>

      {/* Parameter sliders */}
      {OP_PARAMS[operation]?.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Parameters</Typography>
          <Grid container spacing={2}>
            {OP_PARAMS[operation].map((p) => (
              <Grid item xs={12} sm={6} key={p}>
                <Typography variant="caption">{PARAM_CONFIG[p].label}: {params[p]}</Typography>
                <Slider
                  value={params[p]}
                  min={PARAM_CONFIG[p].min}
                  max={PARAM_CONFIG[p].max}
                  step={PARAM_CONFIG[p].step}
                  onChange={(_, v) => setParams((prev) => ({ ...prev, [p]: v }))}
                  size="small"
                />
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Before / After comparison */}
      {result && (
        <Box>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: "flex", gap: 1, mb: 2, flexWrap: "wrap" }}>
            <Chip label={`${result.image_width} × ${result.image_height} px`} variant="outlined" size="small" />
            <Chip label={`mean: ${result.stats.mean}`} size="small" />
            <Chip label={`std: ${result.stats.std}`} size="small" />
            {result.contour_count !== null && (
              <Chip label={`${result.contour_count} contours`} color="success" size="small" />
            )}
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" gutterBottom>Original</Typography>
              <img src={`data:image/jpeg;base64,${result.original_image}`}
                alt="original" style={{ width: "100%", borderRadius: 4, border: "1px solid #e0e0e0" }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" gutterBottom>
                Result — <Chip label={result.operation} size="small" color="primary" />
              </Typography>
              <img src={`data:image/jpeg;base64,${result.result_image}`}
                alt="result" style={{ width: "100%", borderRadius: 4, border: "1px solid #e0e0e0" }} />
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
}
