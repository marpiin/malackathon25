# 🤖 Configuración del Chat IA con Gemini

## 📋 Descripción

El Chat IA permite hacer consultas en lenguaje natural sobre los datos de salud mental almacenados en la base de datos Oracle. El sistema utiliza Google Gemini para:

1. **Traducir** tu pregunta en lenguaje natural a una consulta SQL válida
2. **Ejecutar** la consulta en la base de datos Oracle
3. **Interpretar** los resultados y presentarlos de forma comprensible

## 🔑 Obtener tu API Key de Google Gemini

### Paso 1: Accede a Google AI Studio

1. Ve a [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) o [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API Key"** o **"Get API Key"**

### Paso 2: Crea una API Key

1. Selecciona o crea un proyecto de Google Cloud (o usa uno existente)
2. La API key se generará automáticamente
3. **Copia la API key** (solo se mostrará una vez)

### Paso 3: Configura tu archivo .env

Añade la API key a tu archivo `.env`:

```bash
GOOGLE_API_KEY=AIzaSy...tu-api-key-completa-aqui
```

## ✅ Verificar la instalación

1. Asegúrate de haber instalado las dependencias:
   ```bash
   pip install google-generativeai tabulate
   ```

2. Verifica que tu archivo `.env` contiene la variable `GOOGLE_API_KEY`

3. Inicia la aplicación:
   ```bash
   python app.py
   ```

4. Ve a la pestaña **"Chat IA"** en el menú de navegación

## 💡 Ejemplos de preguntas

### Preguntas básicas
- ¿Cuántos pacientes hay en total?
- ¿Cuántos registros tenemos?

### Análisis por demografía
- ¿Cuántos hombres y mujeres hay?
- ¿Cuántos pacientes hay por comunidad autónoma?

### Estadísticas de estancia
- ¿Cuál es el promedio de días de estancia?
- ¿Cuál es la estancia máxima y mínima?

### Análisis de costes
- ¿Cuál es el coste total de todos los ingresos?
- ¿Cuál es el coste promedio por paciente?

### UCI
- ¿Cuántos pacientes estuvieron en UCI?
- ¿Cuál es el promedio de días en UCI?

### Comunidades y diagnósticos
- ¿Qué comunidad tiene más ingresos?
- ¿Cuáles son las categorías diagnósticas más comunes?
- ¿Cuántos pacientes hay de esquizofrenia?

### Consultas temporales
- ¿Cuántos ingresos hubo en 2023?
- ¿En qué mes hay más ingresos?

### Consultas complejas
- Dame el coste promedio por comunidad autónoma
- ¿Cuál es la distribución de pacientes por sexo y categoría diagnóstica?
- Muéstrame los 5 diagnósticos más costosos

## 🔧 Solución de problemas

### Error: "El servicio de IA no está configurado"

**Causa**: La variable `GOOGLE_API_KEY` no está configurada en el archivo `.env`

**Solución**: 
1. Verifica que tienes un archivo `.env` en la raíz del proyecto
2. Asegúrate de que contiene la línea: `GOOGLE_API_KEY=tu-api-key-aqui`
3. Reinicia la aplicación Flask

### Error: "API key not valid"

**Causa**: La API key es incorrecta o ha expirado

**Solución**: 
1. Genera una nueva API key en Google AI Studio
2. Actualiza tu archivo `.env` con la nueva key
3. Reinicia la aplicación

### Error en la consulta SQL

**Causa**: El modelo no pudo generar una consulta válida para tu pregunta

**Solución**: 
1. Reformula tu pregunta de manera más específica
2. Usa los ejemplos proporcionados como referencia
3. Asegúrate de que las tablas y columnas existen en tu esquema

### El chat no responde

**Causa**: Puede haber un problema de conectividad con la API de Google

**Solución**: 
1. Verifica tu conexión a Internet
2. Comprueba que no has excedido el límite de uso de la API
3. Revisa la consola del navegador (F12) para ver errores

## 📊 Tablas y columnas disponibles

El sistema tiene acceso al siguiente esquema (se obtiene automáticamente):

- **VISTA_DASHBOARD**: Vista principal con todos los datos agregados
- **COMUNIDADES**: Información de comunidades autónomas
- **INGRESOS**: Datos de ingresos hospitalarios
- **CATEGORIAS_DIAGNOSTICO**: Categorías de diagnósticos
- Y más tablas según tu esquema específico

## 🎯 Mejores prácticas

1. **Sé específico**: Preguntas claras obtienen mejores respuestas
2. **Usa los ejemplos**: Basa tus preguntas en los ejemplos proporcionados
3. **Revisa el SQL**: El sistema te muestra la consulta SQL generada para que puedas verificarla
4. **Itera**: Si la respuesta no es la esperada, reformula la pregunta

## 📈 Limitaciones

- El modelo es gratuito y tiene límites de uso (consulta la documentación de Google)
- Las consultas muy complejas pueden requerir reformulación
- El sistema trabaja solo con los datos disponibles en tu base de datos
- La interpretación depende del modelo de IA y puede variar

## 🔐 Seguridad

- **Nunca compartas tu API key** en repositorios públicos
- El archivo `.env` está en el `.gitignore` para proteger tus credenciales
- La API key se usa solo en el servidor (backend), no se expone al frontend
- Todas las consultas requieren autenticación en la aplicación

## 🆘 Soporte

Si tienes problemas:

1. Revisa que todas las variables de entorno estén configuradas
2. Verifica los logs de la aplicación Flask en la terminal
3. Consulta la documentación de [Google Generative AI](https://ai.google.dev/tutorials/python_quickstart)
4. Revisa que tu base de datos Oracle esté accesible

---

¡Disfruta haciendo preguntas en lenguaje natural sobre tus datos! 🚀
