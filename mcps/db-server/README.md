docker run --rm --init \
  --name dbhub \
  -p 8080:8080 \
  -v $(pwd)/dbhub.toml:/workspace/dbhub.toml \
  bytebase/dbhub \
  --transport http \
  --port 8080 \
  --config /workspace/dbhub.toml