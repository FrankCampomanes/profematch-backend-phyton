const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');

async function migrate() {
    try {
        console.log('Iniciando migración de la base de datos...');
        
        // Creamos una conexión cruda para poder crear la DB si no existe
        const connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: '',
            multipleStatements: true // Importante para ejecutar el script SQL entero
        });

        // Asegurar que la BD existe
        await connection.query('CREATE DATABASE IF NOT EXISTS profematch_db;');
        await connection.query('USE profematch_db;');

        // Leer el archivo setup.sql
        const sqlFilePath = path.join(__dirname, '../../database/setup.sql');
        const sqlScript = fs.readFileSync(sqlFilePath, 'utf8');

        console.log('Ejecutando setup.sql...');
        await connection.query(sqlScript);

        console.log('Migración completada exitosamente. Las tablas han sido recreadas limpias.');
        await connection.end();
        process.exit(0);
    } catch (error) {
        console.error('Error durante la migración:', error);
        process.exit(1);
    }
}

migrate();
