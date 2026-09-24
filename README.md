# ISPS Data Extractor

Herramienta para extraer nombres y datos de contacto de proveedores ISP desde archivos CSV, limpiarlos y generar resultados estructurados para su uso posterior.

## Objetivo

Convertir archivos CSV heterogeneos en un conjunto de datos consistente de proveedores y contactos, sin cargar archivos completos en memoria. El proyecto debe poder crecer desde un script local hasta un proceso reutilizable para multiples archivos y fuentes.

## Metodo de trabajo: Spec-Driven Development

Trabajaremos con la especificacion como contrato antes de ampliar la implementacion:

1. Definir el comportamiento esperado y los casos limite.
2. Convertir cada regla en pruebas automatizadas.
3. Implementar el cambio minimo que haga pasar las pruebas.
4. Ejecutar una validacion enfocada y despues la suite completa.
5. Actualizar la especificacion cuando cambie el comportamiento del producto.

La especificacion debe describir entradas, salidas, reglas de limpieza, errores y limites de rendimiento. Una decision no se considera terminada hasta que tenga una prueba o una justificacion documentada.

## Alcance actual

- Lectura de CSV por bloques mediante `pandas`.
- Deteccion de columnas conocidas para el nombre del proveedor.
- Limpieza basica y deduplicacion de nombres.
- Exportacion de la lista de proveedores a Excel.
- Pruebas unitarias para deteccion de columnas y deduplicacion.

## Especificacion inicial

### Entrada

- Uno o varios archivos `.csv`.
- Los archivos pueden ser grandes y no deben requerir cargarse completos en memoria.
- Los nombres de columnas pueden variar entre fuentes.
- Las columnas de contacto previstas incluyen nombre, telefono, correo electronico, sitio web y direccion.

### Salida

El resultado normalizado debe conservar, como minimo:

- `provider_name`: nombre limpio del proveedor.
- `contact_name`: nombre de la persona o contacto, cuando exista.
- `phone`: telefono, cuando exista.
- `email`: correo electronico, cuando exista.
- `website`: sitio web, cuando exista.
- `address`: direccion, cuando exista.
- `source_file`: archivo de origen para trazabilidad.

Los campos ausentes deben quedar vacios, no provocar un fallo global. Los registros duplicados deben eliminarse usando una clave definida por la especificacion y conservar el origen.

### Reglas de calidad

- Recortar espacios al inicio y al final.
- Convertir valores nulos o vacios en ausencia de dato.
- No inventar datos ni mezclar contactos sin una regla explicita.
- Mantener trazabilidad del archivo de origen.
- Informar columnas no reconocidas y archivos que no puedan procesarse.
- Un archivo invalido no debe ocultar silenciosamente el resultado de los demas archivos.

## Arquitectura prevista

- `src/isps_extractor/input_reader.py`: descubrimiento y lectura por bloques.
- `src/isps_extractor/processor.py`: normalizacion, deteccion de columnas y deduplicacion.
- `src/isps_extractor/quality.py`: validacion de contactos y metricas de calidad.
- `src/isps_extractor/config.py`: configuracion de columnas, tamano de bloque y formatos.
- `src/isps_extractor/cli.py`: CLI y coordinacion del flujo.
- `tests/test_processor.py`: especificaciones ejecutables del procesamiento.

La siguiente evolucion debe separar la logica de dominio de la salida Excel. Asi podremos agregar CSV, JSON o base de datos sin duplicar el procesamiento.

## Roadmap

1. Definir mapas de columnas para nombres y contactos.
2. Procesar multiples archivos en una sola ejecucion.
3. Normalizar registros en una estructura comun y conservar `source_file`.
4. Añadir validacion de correo, telefono y URL sin descartar datos utiles.
5. Crear una CLI con entrada, salida, formato y tamano de bloque configurables.
6. Incorporar reportes de errores y metricas por archivo.
7. Añadir pruebas de integracion y pruebas con archivos grandes.

## Ejecutar

### Instalacion

Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Para instalar tambien las herramientas de desarrollo y los tipos de `pandas`:

```bash
pip install -e ".[dev]"
```

### Pruebas

```bash
python3 -m unittest discover -s tests -v
```

### Extraccion

Coloca los archivos CSV de entrada en la carpeta de trabajo y ejecuta:

```bash
isps-extractor
```

También puedes indicar una carpeta de entrada y nombres de salida personalizados:

```bash
isps-extractor \
	--input ./data \
	--contacts-output ./output/contacts.xlsx \
	--providers-output ./output/providers.xlsx
```

La ejecucion actual busca todos los archivos CSV en la carpeta de trabajo y genera:

- `Contactos_ISPs_Normalizados.xlsx`, con nombres, contactos y el archivo de origen.
- `Lista_ISPs_Colombia_Limpia.xlsx`, con los nombres de proveedores unicos.

Durante la ejecucion tambien se muestra un resumen de registros con problemas y
la cantidad de correos, telefonos y sitios web validos.
