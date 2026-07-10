const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'ProfeMatch API',
      version: '1.0.0',
      description: 'Documentación interactiva de la API del backend de ProfeMatch',
    },
    servers: [
      {
        url: 'http://localhost:3006',
        description: 'Servidor Local (Desarrollo)'
      },
      {
        url: 'https://profematch-backend.onrender.com',
        description: 'Servidor de Producción (Render)'
      }
    ],
  },
  // Especificamos las rutas donde swagger-jsdoc leerá los comentarios:
  apis: ['./src/routes/*.js'],
};

const swaggerSpec = swaggerJsdoc(options);

const swaggerDocs = (app) => {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
  console.log('📄 Swagger Docs disponibles en /api-docs');
};

module.exports = { swaggerDocs };
