/**
 * Catálogo de Certificações - Cert-Manager
 * Estes valores podem ser atualizados manualmente ou via Scraper.
 */

export const certifications = [
  {
    id: "az-900",
    title: "AZ-900: Microsoft Azure Fundamentals",
    category: "Cloud/OS",
    basePriceUSD: 99.00, // O Scraper monitora este campo
    lastUpdate: "2026-03-09",
    status: "Iniciada",
    examUrl: "https://learn.microsoft.com/en-us/credentials/certifications/exams/az-900/"
  },
  {
    id: "sc-900",
    title: "SC-900: Security, Compliance, and Identity Fundamentals",
    category: "Security",
    basePriceUSD: 99.00,
    lastUpdate: "2026-03-09",
    status: "Aguardando",
    examUrl: "https://learn.microsoft.com/en-us/credentials/certifications/exams/sc-900/"
  },
  {
    id: "az-104",
    title: "AZ-104: Microsoft Azure Administrator",
    category: "Admin/OS",
    basePriceUSD: 165.00,
    lastUpdate: "2026-03-09",
    status: "Aguardando",
    examUrl: "https://learn.microsoft.com/en-us/credentials/certifications/exams/az-104/"
  },
  {
    id: "sc-300",
    title: "SC-300: Microsoft Identity and Access Administrator",
    category: "Identity & Security", // Onde sua formação brilha!
    basePriceUSD: 165.00,
    lastUpdate: "2026-03-09",
    status: "Planejada",
    examUrl: "https://learn.microsoft.com/en-us/credentials/certifications/exams/sc-300/",
    relevance: "Alta - Reestruturação de AD no SFB" // Nota personalizada para seu portfólio
  }
];