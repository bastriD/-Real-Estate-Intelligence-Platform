#!/bin/sh
# governance:build-image / script. Sourced by GitLab; run from the project checkout.

echo "Building Real Estate Governance image..."
echo "Governance image tag = $IMAGE_TAG"
echo "Governance image = $IMAGE_NAME:$IMAGE_TAG"
docker build \
  -f governance/Dockerfile \
  -t "$IMAGE_NAME:$IMAGE_TAG" \
  -t "$IMAGE_NAME:latest" \
  governance
echo "Pushing immutable governance image..."
docker push "$IMAGE_NAME:$IMAGE_TAG"
echo "Pushing latest governance image..."
docker push "$IMAGE_NAME:latest"
docker image inspect "$IMAGE_NAME:$IMAGE_TAG" > /dev/null
echo "Governance image published successfully."
echo "GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA" > governance-image.env
cat governance-image.env
