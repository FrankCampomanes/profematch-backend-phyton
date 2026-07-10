const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');
require('dotenv').config();

async function migrate() {
    try {
        console.log('Iniciando migración de la base de datos...');

        const config = {
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'profematch_db',
            port: process.env.DB_PORT || 3306,
            multipleStatements: true // Importante para ejecutar el script SQL entero
        };

        // Habilitar SSL automáticamente si el host no es localhost (para bases de datos en la nube)
        if (config.host !== 'localhost') {
            config.ssl = {
                rejectUnauthorized: false
            };
        }

        // Si es localhost, intentamos asegurar que la base de datos exista
        if (config.host === 'localhost') {
            console.log(`Verificando/creando base de datos local: ${config.database}...`);
            const tempConnection = await mysql.createConnection({
                host: config.host,
                user: config.user,
                password: config.password,
                port: config.port
            });
            await tempConnection.query(`CREATE DATABASE IF NOT EXISTS \`${config.database}\`;`);
            await tempConnection.end();
        }

        // Conectar directamente a la base de datos especificada
        console.log(`Conectando a la base de datos en ${config.host}...`);
        const connection = await mysql.createConnection(config);

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

