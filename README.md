# Playground

## Build image

```sh
# Build image
docker build . -t playground
# Run container
docker run -p 40009:40009 -p 40011:40011 playground
```
