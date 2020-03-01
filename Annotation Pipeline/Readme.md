## Annotaiton Pipeline

This Pipeline scrapes Earning calls from SeekingAlpha, Pre-processes the said calls and uses Google NLP API to generate a sentiment score for every sentence. 

## Run Instructions 

```
python testp.py --environment=conda run
```

This pipeline will write it's result to an output bucket on AWS S3 which you will specify and configure in the pipeline.


The pipeline model is shown below:

