#!/bin/bash
# Validate OpenAPI specification using docker

echo "Validating OpenAPI specification..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Validate using openapitools/openapi-generator-cli
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli validate \
    -i /local/openapi.yaml

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ OpenAPI specification is valid!"
    echo ""
    echo "Next steps:"
    echo "  - View in Swagger Editor: https://editor.swagger.io/"
    echo "  - Run local viewer: docker run -p 8080:8080 -e SWAGGER_JSON=/docs/openapi.yaml -v \$(pwd):/docs swaggerapi/swagger-ui"
else
    echo ""
    echo "❌ OpenAPI specification has errors. Please fix them and try again."
    exit 1
fi
