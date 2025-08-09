# Limitations

## 1. No Docker
I know i know, it's a really useful tool but the clusters don't support it. Instead you have to use `apptainer`. However, you can turn your docker images into apptainer compatible containers and upload them to the clusters for your own use. But don't count on it without any testing. There's lots of docs on how to convert a docker image into `.sif` files that apptainer accepts. And one big difference between Docker and Apptainer is that Docker is layered, while apptainer is not. You can find more about it in the [DOCS](https://docs.alliancecan.ca/wiki/Apptainer)

## 2. No package manager (Poetry, Conda)
Package managers are not optimized for use in the clusters. They are just slow for use in the clusters. Use the manual package handling with the python virtual environment and you'll be better off.

## 3. CACHE CACHE CACHE CACHE
Remember! No internet in the jobs, that means to API calls, no pulling huggingface models, no `wget` commands and no scraping. If you're trying to use huggingface models search into their caching system and see how you can pre-download an image in your login node to be later used in the job
