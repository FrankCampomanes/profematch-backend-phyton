const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

// --- Middleware ---
app.use(cors()); 
app.use(express.json()); 

// --- Rutas Base ---
app.get('/', (req, res) => {
    res.json({ message: 'API de ProfeMatch funcionando correctamente con la nueva arquitectura' });
});

const authRoutes = require('./src/routes/auth.routes');
const profesorRoutes = require('./src/routes/profesor.routes');
const sesionRoutes = require('./src/routes/sesion.routes');
const usuarioRoutes = require('./src/routes/usuario.routes');

app.use('/api/auth', authRoutes);
app.use('/api/professors', profesorRoutes);
app.use('/api/sessions', sesionRoutes);
app.use('/api/usuarios', usuarioRoutes);

// --- Inicialización del Servidor ---
const { swaggerDocs } = require('./src/config/swagger');
const PORT = process.env.PORT || 3006;

app.listen(PORT, () => {
    console.log(`🚀 Servidor backend corriendo en el puerto ${PORT}`);
    swaggerDocs(app);
});