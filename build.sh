#!/bin/bash
set -eo pipefail

echo "Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps

echo "Building frontend..."
npm run build

echo "Build complete!"
