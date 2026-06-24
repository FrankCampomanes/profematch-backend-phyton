const express = require('express');
const cors = require('cors');
const mysql = require('mysql2');
require('dotenv').config();

const app = express();

// --- 1. Configuración de Middleware ---
// Permite que tu Frontend en React se comunique sin errores de seguridad
app.use(cors()); 
// Permite que el servidor entienda datos en formato JSON
app.use(express.json()); 

// --- 2. Conexión a la Base de Datos ---
// --- 2. Conexión a la Base de Datos (FORZADA) ---
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '', // Dejamos esto vacío intencionalmente
    database: 'profematch_db',
    port: 3307
});

db.connect((err) => {
    if (err) {
        console.error('❌ Error conectando a la base de datos:', err);
        return;
    }
    console.log('✅ Conexión exitosa a la base de datos MySQL (profematch_db)');
});

// --- 3. Ruta de Prueba Base ---
app.get('/', (req, res) => {
    res.send('¡API de ProfeMatch funcionando correctamente!');
});

// --- 4. Inicialización del Servidor ---
const PORT = process.env.PORT || 3000;

// --- 5. Endpoint para obtener todos los usuarios activos ---
app.get('/api/usuarios', (req, res) => {
    const sql = "SELECT * FROM Usuarios WHERE estado_cuenta = 'activo'";
    db.query(sql, (err, results) => {
        if (err) {
            return res.status(500).json({ error: "Error en la consulta: " + err.message });
        }
        res.json(results);
    });
});

app.listen(PORT, () => {
    console.log(`🚀 Servidor backend corriendo en el puerto ${PORT}`);
});