#!/bin/bash

PROJECT_ID="financesight-463118"

build_and_push() {
  SERVICE_DIR=$1
  IMAGE_NAME=$2

  echo "Building $IMAGE_NAME from $SERVICE_DIR ..."
  cd "../$SERVICE_DIR" || exit 1

  docker build -t "gcr.io/$PROJECT_ID/$IMAGE_NAME:v1" .
  docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME:v1"

  cd ../
  echo "Done with $IMAGE_NAME"
  echo "---------------------------"
}

# Run for each service
build_and_push "aggregator" "aggregator"
build_and_push "service_1" "fetch_news_crypto_service_1"
build_and_push "service_2" "fetch_news_crypto_service_2"
build_and_push "service_3" "fetch_news_crypto_service_3"
