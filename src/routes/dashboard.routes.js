const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboard.controller');

router.get('/admin', dashboardController.getAdminDashboard);
router.put('/quejas/:id/sancionar', dashboardController.sancionarQueja);
router.put('/quejas/:id/desestimar', dashboardController.desestimarQueja);

module.exports = router;