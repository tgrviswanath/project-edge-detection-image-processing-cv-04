import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <AutoFixHighIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">
          Edge Detection & Image Processing
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
