#!/bin/bash

echo "=== Curiosity Box Setup ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Building and starting containers..."
docker-compose up --build -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

echo ""
echo "Creating superuser..."
echo "You'll be prompted to create an admin account."
docker-compose exec web python manage.py createsuperuser

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "🎉 Curiosity Box is running!"
echo ""
echo "Access the application:"
echo "  - API: http://localhost:8000/api/"
echo "  - Admin: http://localhost:8000/admin/"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop: docker-compose down"
echo "  - Restart: docker-compose restart"
echo "  - Run tests: docker-compose exec web python manage.py test core"
echo ""
