# Test Contracts

Three pairs of contract images for testing the LegalMove pipeline.
All images were generated from the provided PDFs in `additional-resources/`.

---

## pair_1_simple — Contrato de Servicio SaaS

| File | Description |
|------|-------------|
| `original.png` | CloudMetrics Ltd. & RetailPulse S.A. — SaaS service contract (Feb 2024) |
| `amendment.png` | Updated version with 3 simple modifications |

**Changes introduced by the amendment:**
- **Precio** (Cláusula 3): USD 1,200/month → USD 1,250/month
- **Disponibilidad** (Cláusula 4): 99.5% SLA → 99.9% SLA
- **Soporte** (Cláusula 5): email only → email + online ticket system

**Use case:** Validates the pipeline on a straightforward amendment with numeric and
text modifications across 3 sections, no clauses added or removed.

---

## pair_2_complex — Contrato de Licencia de Software

| File | Description |
|------|-------------|
| `original.png` | TechNova S.A. & DataBridge Soluciones S.R.L. — Software license (Mar 2024) |
| `amendment.png` | Amendment with multiple modifications and one new clause |

**Changes introduced by the amendment:**
- **Cláusula 2 - Plazo**: 12 months → 24 months *(MODIFICATION)*
- **Cláusula 3 - Pago**: USD 12,000 → USD 15,000 *(MODIFICATION)*
- **Cláusula 4 - Soporte**: email only → email + chat *(MODIFICATION)*
- **Cláusula 5 - Terminación**: 30-day notice → 60-day notice *(MODIFICATION)*
- **Cláusula 7 - Protección de Datos**: entirely new clause added *(ADDITION)*

**Use case:** Validates the pipeline on a complex amendment with 4 modifications
and 1 addition, requiring the extraction agent to distinguish change types.

---

## pair_3_consulting — Contrato de Servicios de Consultoría *(bonus)*

| File | Description |
|------|-------------|
| `original.png` | Orion Consulting Group & GreenWave Energía S.A. — Consulting contract (Jan 2024) |
| `amendment.png` | Amendment with scope expansion and new IP clause |

**Changes introduced by the amendment:**
- **Cláusula 1 - Alcance**: adds "y análisis regulatorio" *(MODIFICATION)*
- **Cláusula 2 - Duración**: 6 months → 9 months *(MODIFICATION)*
- **Cláusula 3 - Honorarios**: USD 8,000 → USD 9,500/month *(MODIFICATION)*
- **Cláusula 4 - Entregables**: monthly → biweekly reports *(MODIFICATION)*
- **Cláusula 7 - Propiedad Intelectual**: entirely new clause added *(ADDITION)*

**Use case:** Additional complex test case with domain-specific legal content
(energy/regulatory consulting).
