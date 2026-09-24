CHUNK_SIZE = 50000
OUTPUT_FILE = "Lista_ISPs_Colombia_Limpia.xlsx"
CONTACTS_OUTPUT_FILE = "Contactos_ISPs_Normalizados.xlsx"
QUALITY_OUTPUT_FILE = "Reporte_Calidad_ISPs.xlsx"
EXCEL_MAX_DATA_ROWS = 1_048_575
COLUMN_ALIASES = {
    "provider_name": [
        "Razon Social",
        "RAZÓN SOCIAL",
        "Nombre Proveedor",
        "Empresa",
        "PROVEEDOR",
        "Nombre",
        "brand_name",
        "provider_id",
        "company_name",
    ],
    "contact_name": ["Contacto", "Nombre Contacto", "Contact Name"],
    "phone": ["Telefono", "Teléfono", "Phone", "Celular", "Mobile"],
    "email": ["Correo", "Email", "Correo Electronico", "E-mail"],
    "website": ["Sitio Web", "Website", "URL", "Pagina Web"],
    "address": ["Direccion", "Dirección", "Address"],
}

POSSIBLE_COLUMNS = COLUMN_ALIASES["provider_name"]
