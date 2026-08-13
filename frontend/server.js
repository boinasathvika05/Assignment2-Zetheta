const express = require('express');
const path = require('path');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_HOST = process.env.BACKEND_HOST || '127.0.0.1';
const BACKEND_PORT = process.env.BACKEND_PORT || 8000;

// Reverse Proxy for API requests to FastAPI backend
app.use(['/api', '/health', '/metrics', '/docs', '/openapi.json', '/redoc'], (req, res) => {
  const targetPath = req.originalUrl;
  console.log(`[PROXY] ${req.method} ${targetPath} -> http://${BACKEND_HOST}:${BACKEND_PORT}${targetPath}`);

  const options = {
    hostname: BACKEND_HOST,
    port: BACKEND_PORT,
    path: targetPath,
    method: req.method,
    headers: {
      ...req.headers,
      host: `${BACKEND_HOST}:${BACKEND_PORT}`
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.error(`[PROXY ERROR] Failed to connect to FastAPI backend: ${err.message}`);
    res.status(503).json({
      success: false,
      error: {
        code: "BACKEND_UNREACHABLE",
        message: `Frontend Express reverse proxy could not connect to FastAPI backend service on port ${BACKEND_PORT}.`,
        details: err.message
      }
    });
  });

  req.pipe(proxyReq, { end: true });
});

app.use(express.static(path.join(__dirname, 'public')));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`NexBank Frontend Web Portal running on port ${PORT} (Proxying /api -> http://${BACKEND_HOST}:${BACKEND_PORT})`);
});
