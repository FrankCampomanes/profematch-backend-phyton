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
    port: 3306
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

// 1. ENDPOINT PARA CREAR UN NUEVO USUARIO (POST)
app.post('/api/usuarios', (req, res) => {
    const { nombre, email, rol, score_confiabilidad } = req.body;
    const password_hash = 'temporal123'; // Clave por defecto para desarrollo
    const sql = "INSERT INTO Usuarios (nombre, email, password_hash, rol, score_confiabilidad, estado_cuenta) VALUES (?, ?, ?, ?, ?, 'activo')";
    
    db.query(sql, [nombre, email, password_hash, rol, score_confiabilidad], (err, result) => {
        if (err) return res.status(500).json({ error: err.message });
        res.status(201).json({ message: "Usuario creado exitosamente", id: result.insertId });
    });
});

// 2. ENDPOINT PARA EDITAR DATOS DE UN USUARIO (PUT)
app.put('/api/usuarios/:id', (req, res) => {
    const { id } = req.params;
    const { nombre, email, rol, score_confiabilidad } = req.body;
    const sql = "UPDATE Usuarios SET nombre = ?, email = ?, rol = ?, score_confiabilidad = ? WHERE id = ?";
    
    db.query(sql, [nombre, email, rol, score_confiabilidad, id], (err, result) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: "Usuario actualizado correctamente" });
    });
});

// 3. ENDPOINT PARA EL BORRADO LÓGICO / BLOQUEO (PUT)
app.put('/api/usuarios/bloquear/:id', (req, res) => {
    const { id } = req.params;
    // Cambiamos el estado de la cuenta a 'en_papelera' para el borrado lógico
    const sql = "UPDATE Usuarios SET estado_cuenta = 'en_papelera' WHERE id = ?";
    
    db.query(sql, [id], (err, result) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: "Usuario enviado a la papelera correctamente" });
    });
});

// 4. ENDPOINT PARA OBTENER USUARIOS EN LA PAPELERA (GET)
app.get('/api/usuarios/papelera', (req, res) => {
    // Seleccionamos solo los usuarios cuyo estado cuenta sea 'en_papelera'
    const sql = "SELECT * FROM Usuarios WHERE estado_cuenta = 'en_papelera'";
    db.query(sql, (err, results) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(results);
    });
});

// 5. ENDPOINT PARA RESTAURAR UN USUARIO DE LA PAPELERA (PUT)
app.put('/api/usuarios/restaurar/:id', (req, res) => {
    const { id } = req.params;
    // Cambiamos el estado de cuenta de vuelta a 'activo'
    const sql = "UPDATE Usuarios SET estado_cuenta = 'activo' WHERE id = ?";
    db.query(sql, [id], (err, result) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: "Usuario restaurado correctamente con éxito" });
    });
});