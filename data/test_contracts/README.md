# Contratos de Prueba

Tres pares de imágenes de contratos para testear el pipeline de LegalMove.
Todas las imágenes fueron generadas a partir de los PDFs provistos en `additional-resources/`.

---

## pair_1_simple — Contrato de Servicio SaaS

| Archivo | Descripción |
|---------|-------------|
| `original.png` | CloudMetrics Ltd. y RetailPulse S.A. — Contrato de servicio SaaS (feb. 2024) |
| `amendment.png` | Versión actualizada con 3 modificaciones simples |

**Cambios introducidos por la enmienda:**
- **Precio** (Cláusula 3): USD 1.200/mes → USD 1.250/mes
- **Disponibilidad** (Cláusula 4): SLA del 99,5% → 99,9%
- **Soporte** (Cláusula 5): solo correo electrónico → correo + sistema de tickets en línea

**Caso de uso:** Valida el pipeline ante una enmienda sencilla con modificaciones numéricas
y de texto en 3 secciones, sin cláusulas agregadas ni eliminadas.

---

## pair_2_complex — Contrato de Licencia de Software

| Archivo | Descripción |
|---------|-------------|
| `original.png` | TechNova S.A. y DataBridge Soluciones S.R.L. — Licencia de software (mar. 2024) |
| `amendment.png` | Enmienda con múltiples modificaciones y una cláusula nueva |

**Cambios introducidos por la enmienda:**
- **Cláusula 2 - Plazo**: 12 meses → 24 meses *(MODIFICACIÓN)*
- **Cláusula 3 - Pago**: USD 12.000 → USD 15.000 *(MODIFICACIÓN)*
- **Cláusula 4 - Soporte**: solo correo → correo + chat *(MODIFICACIÓN)*
- **Cláusula 5 - Terminación**: aviso de 30 días → 60 días *(MODIFICACIÓN)*
- **Cláusula 7 - Protección de Datos**: cláusula completamente nueva *(ADICIÓN)*

**Caso de uso:** Valida el pipeline ante una enmienda compleja con 4 modificaciones
y 1 adición, requiriendo que el agente de extracción distinga los tipos de cambio.

---

## pair_3_consulting — Contrato de Servicios de Consultoría *(bonus)*

| Archivo | Descripción |
|---------|-------------|
| `original.png` | Orion Consulting Group y GreenWave Energía S.A. — Contrato de consultoría (ene. 2024) |
| `amendment.png` | Enmienda con ampliación de alcance y nueva cláusula de propiedad intelectual |

**Cambios introducidos por la enmienda:**
- **Cláusula 1 - Alcance**: agrega "y análisis regulatorio" *(MODIFICACIÓN)*
- **Cláusula 2 - Duración**: 6 meses → 9 meses *(MODIFICACIÓN)*
- **Cláusula 3 - Honorarios**: USD 8.000 → USD 9.500/mes *(MODIFICACIÓN)*
- **Cláusula 4 - Entregables**: reportes mensuales → quincenales *(MODIFICACIÓN)*
- **Cláusula 7 - Propiedad Intelectual**: cláusula completamente nueva *(ADICIÓN)*

**Caso de uso:** Caso de prueba complejo adicional con contenido legal específico
del dominio de consultoría energética y regulatoria.
