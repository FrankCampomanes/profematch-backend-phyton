const mysql = require('mysql2/promise');
require('dotenv').config(); // Para leer variables de entorno en migraciones

const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root', // XAMPP default
    password: process.env.DB_PASSWORD || '', // XAMPP default is empty
    database: process.env.DB_NAME || 'profematch_db',
    port: process.env.DB_PORT || 3306,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

module.exports = pool;
