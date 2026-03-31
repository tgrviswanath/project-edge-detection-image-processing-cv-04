import React from "react";
import { Container } from "@mui/material";
import Header from "./components/Header";
import ProcessPage from "./pages/ProcessPage";

export default function App() {
  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ProcessPage />
      </Container>
    </>
  );
}
